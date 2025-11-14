"""
Anki deck import routes (Premium feature)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import zipfile
import sqlite3
import tempfile
import os
import re
import html
from html.parser import HTMLParser
from typing import List, Dict, Any, Tuple, Optional
from app.database import get_db
from app.models import User, Flashcard, Deck
from app.services.auth import get_current_active_user
from app.services.premium_service import check_premium_status

router = APIRouter()


class HTMLStripper(HTMLParser):
    """Strip HTML tags from text"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text)


def strip_html(html_text: str) -> str:
    """Strip HTML tags and decode HTML entities"""
    if not html_text:
        return html_text
    
    # First unescape HTML entities (like &nbsp;, &lt;, etc.)
    text = html.unescape(html_text)
    
    # Then strip HTML tags
    stripper = HTMLStripper()
    stripper.feed(text)
    return stripper.get_text().strip()


def parse_cloze_deletion(text: str) -> Optional[Tuple[str, str]]:
    """
    Parse cloze deletion format: {{c1::answer}} or {{c1::hint::answer}}
    Returns (front, back) tuple if cloze found, None otherwise
    """
    # Pattern to match {{c1::text}} or {{c1::hint::text}}
    cloze_pattern = r'\{\{c\d+::(?:[^:]+::)?([^}]+)\}\}'
    
    matches = list(re.finditer(cloze_pattern, text))
    if not matches:
        return None
    
    # Extract all cloze deletions
    cloze_texts = []
    front_text = text
    
    for match in reversed(matches):  # Reverse to maintain positions when replacing
        cloze_text = match.group(1)  # The answer text
        cloze_texts.append(cloze_text)
        # Replace with ellipsis or placeholder
        front_text = front_text[:match.start()] + "..." + front_text[match.end():]
    
    # For multiple clozes, combine them; otherwise use single answer
    back_text = ", ".join(cloze_texts) if len(cloze_texts) > 1 else cloze_texts[0]
    
    return (front_text.strip(), back_text.strip())


@router.post("/import")
async def import_anki_deck(
    file: UploadFile = File(...),
    deck_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import an Anki deck (.apkg file) and create flashcards
    Premium feature only
    """
    # Check premium status
    if not current_user.is_premium:
        raise HTTPException(
            status_code=403,
            detail="Anki import is a premium feature. Please upgrade to Premium to use this feature."
        )
    
    # Validate file type
    if not file.filename.endswith('.apkg'):
        raise HTTPException(status_code=400, detail="File must be an .apkg file")
    
    # Create temporary directory for extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        # Extract zip file
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid .apkg file format")
        
        # Find SQLite database file (usually collection.anki2 or collection.anki21)
        db_file = None
        for filename in os.listdir(temp_dir):
            if filename.startswith('collection.anki') and filename.endswith(('.anki2', '.anki21')):
                db_file = os.path.join(temp_dir, filename)
                break
        
        if not db_file:
            raise HTTPException(status_code=400, detail="Could not find Anki database in .apkg file")
        
        # Connect to SQLite database
        try:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # First, let's check what tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"Available tables: {tables}")
            
            # Check if we have a notes table
            if 'notes' not in tables:
                raise HTTPException(status_code=400, detail="Anki database structure not recognized. No 'notes' table found.")
            
            # Get notes from database
            # Anki notes table structure: id, guid, mid (model id), mod, usn, tags, flds, sfld, csum, flags, data
            # Let's also check the schema
            cursor.execute("PRAGMA table_info(notes)")
            columns = cursor.fetchall()
            print(f"Notes table columns: {columns}")
            
            # Get a sample note to see what we're working with
            cursor.execute("SELECT id, flds, tags, sfld FROM notes LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print(f"Sample note - id: {sample[0]}, flds: {sample[1][:100] if sample[1] else None}, tags: {sample[2]}, sfld: {sample[3]}")
            
            # Get all notes from database
            cursor.execute("SELECT id, flds, tags, sfld FROM notes")
            notes = cursor.fetchall()
            
            if not notes:
                raise HTTPException(status_code=400, detail="No notes found in Anki deck")
            
            # Get or create deck
            if deck_id:
                deck = db.query(Deck).filter(
                    Deck.id == deck_id,
                    Deck.user_id == current_user.id
                ).first()
                if not deck:
                    raise HTTPException(status_code=404, detail="Deck not found")
            else:
                # Create a new deck with the filename (without extension)
                deck_name = os.path.splitext(file.filename)[0]
                deck = Deck(
                    name=deck_name,
                    user_id=current_user.id
                )
                db.add(deck)
                db.flush()
            
            # Parse notes and create flashcards
            created_count = 0
            skipped_count = 0
            
            for note_id, flds, tags, sfld in notes:
                # flds is pipe-separated fields (usually front|back for basic cards)
                fields = flds.split('\x1f')  # Anki uses \x1f as field separator
                
                if len(fields) < 1:
                    skipped_count += 1
                    continue
                
                # Get the first field (main content) and strip HTML
                main_field = strip_html(fields[0].strip()) if fields[0] else ""
                
                # If main_field is empty or looks like an error, try using sfld (sort field) as fallback
                if not main_field or "Please update to the latest Anki version" in main_field or "import the .colpkg/.apkg file again" in main_field:
                    if sfld:
                        main_field = strip_html(sfld.strip())
                        # Re-split fields if we're using sfld - it might be different
                        if not main_field or "Please update to the latest Anki version" in main_field:
                            print(f"Skipping note {note_id} - appears to be an error message or empty")
                            skipped_count += 1
                            continue
                    else:
                        print(f"Skipping note {note_id} - empty field and no sfld")
                        skipped_count += 1
                        continue
                
                # Check if this is a cloze deletion card
                cloze_result = parse_cloze_deletion(main_field)
                
                if cloze_result:
                    # It's a cloze deletion card
                    concept, definition = cloze_result
                else:
                    # Regular card - check if we have a second field
                    if len(fields) >= 2 and fields[1]:
                        concept = main_field
                        definition = strip_html(fields[1].strip())
                        # Skip if definition is also the error message
                        if "Please update to the latest Anki version" in definition:
                            print(f"Skipping note {note_id} - definition field contains error message")
                            skipped_count += 1
                            continue
                    else:
                        # Single field card - use the field as both concept and definition
                        concept = main_field
                        definition = main_field
                
                if not concept:
                    skipped_count += 1
                    continue
                
                # If definition is empty, use concept as definition
                if not definition:
                    definition = concept
                
                # Parse tags (space-separated, may have # prefix)
                tag_list = []
                if tags:
                    tag_list = [tag.strip().lstrip('#') for tag in tags.split() if tag.strip()]
                
                # Convert tags to comma-separated string
                tags_string = ', '.join(tag_list) if tag_list else None
                
                # Create flashcard
                flashcard = Flashcard(
                    concept=concept,
                    definition=definition,
                    tags=tags_string,
                    deck_id=deck.id,
                    user_id=current_user.id
                )
                db.add(flashcard)
                created_count += 1
            
            db.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"Imported {created_count} flashcards from Anki deck",
                "deck_id": deck.id,
                "deck_name": deck.name,
                "created_count": created_count,
                "skipped_count": skipped_count
            }
            
        except sqlite3.Error as e:
            raise HTTPException(status_code=400, detail=f"Error reading Anki database: {str(e)}")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error importing deck: {str(e)}")


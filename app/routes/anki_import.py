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
            
            # Get notes from database
            # Anki notes table structure: id, guid, mid (model id), mod, usn, tags, flds, sfld, csum, flags, data
            cursor.execute("SELECT id, flds, tags FROM notes")
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
            
            for note_id, flds, tags in notes:
                # flds is pipe-separated fields (usually front|back for basic cards)
                fields = flds.split('\x1f')  # Anki uses \x1f as field separator
                
                if len(fields) < 1:
                    skipped_count += 1
                    continue
                
                # Get the first field (main content) and strip HTML
                main_field = strip_html(fields[0].strip())
                
                if not main_field:
                    skipped_count += 1
                    continue
                
                # Check if this is a cloze deletion card
                cloze_result = parse_cloze_deletion(main_field)
                
                if cloze_result:
                    # It's a cloze deletion card
                    concept, definition = cloze_result
                else:
                    # Regular card - check if we have a second field
                    if len(fields) >= 2:
                        concept = main_field
                        definition = strip_html(fields[1].strip())
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


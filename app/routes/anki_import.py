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
    
    # Validate file type - support both .apkg and .colpkg
    if not (file.filename.endswith('.apkg') or file.filename.endswith('.colpkg')):
        raise HTTPException(status_code=400, detail="File must be an .apkg or .colpkg file")
    
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
        # For .colpkg files, it might be just "collection.anki2" or "collection.anki21"
        db_file = None
        for filename in os.listdir(temp_dir):
            if filename.startswith('collection.anki') and filename.endswith(('.anki2', '.anki21')):
                db_file = os.path.join(temp_dir, filename)
                break
        
        if not db_file:
            raise HTTPException(
                status_code=400, 
                detail="Could not find Anki database in the file. This might be a newer Anki format. Please try exporting from Anki as 'Anki Deck Package (*.apkg)' instead of 'Anki Collection Package (*.colpkg)'."
            )
        
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
            
            # Check the col table for deck information (if it exists)
            deck_name_from_file = None
            if 'col' in tables:
                try:
                    cursor.execute("SELECT decks FROM col")
                    col_data = cursor.fetchone()
                    if col_data and col_data[0]:
                        import json
                        try:
                            decks_json = json.loads(col_data[0])
                            # decks_json is a dict where keys are deck IDs and values are deck info
                            # Get the first deck name as a fallback
                            if decks_json:
                                first_deck = list(decks_json.values())[0]
                                deck_name_from_file = first_deck.get('name', None)
                                print(f"Found deck name from col table: {deck_name_from_file}")
                        except:
                            pass
                except Exception as e:
                    print(f"Could not read col table: {e}")
            
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
                sample_flds = str(sample[1]) if sample[1] is not None else ""
                sample_sfld = str(sample[3]) if sample[3] is not None else ""
                print(f"Sample note - id: {sample[0]}, flds: {sample_flds[:100]}, tags: {sample[2]}, sfld: {sample_sfld[:100]}")
                
                # Check if the sample contains the error message - if so, this is definitely a .colpkg issue
                error_indicators = [
                    "Please update to the latest Anki version",
                    "import the .colpkg/.apkg file again",
                    ".colpkg"
                ]
                
                has_error = any(indicator in sample_flds or indicator in sample_sfld for indicator in error_indicators)
                
                if has_error:
                    # Check if there are any cards in the cards table that might have real data
                    if 'cards' in tables:
                        cursor.execute("SELECT COUNT(*) FROM cards")
                        card_count = cursor.fetchone()[0]
                        print(f"Found {card_count} cards in cards table")
                        
                        if card_count == 0:
                            conn.close()
                            raise HTTPException(
                                status_code=400,
                                detail="This Anki file appears to be corrupted or from an incompatible Anki version. The notes contain an error message instead of actual card content. Please try: 1) Update Anki to the latest version, 2) Re-export your deck as 'Anki Deck Package (*.apkg)', 3) If the deck was originally imported from a .colpkg file, you may need to recreate the cards manually."
                            )
                    else:
                        conn.close()
                        raise HTTPException(
                            status_code=400,
                            detail="This appears to be an Anki Collection Package (.colpkg) file, which is not supported. Please export your deck from Anki as 'Anki Deck Package (*.apkg)' instead. In Anki: File → Export → Select 'Anki Deck Package (*.apkg)' → Choose your deck → Export."
                        )
            
            # Check if all notes contain the error message (indicates .colpkg format issue)
            cursor.execute("SELECT COUNT(*) FROM notes WHERE flds LIKE '%Please update to the latest Anki version%'")
            error_note_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM notes")
            total_notes = cursor.fetchone()[0]
            
            if error_note_count == total_notes and total_notes > 0:
                conn.close()
                raise HTTPException(
                    status_code=400,
                    detail="This Anki file appears to be corrupted or from an incompatible Anki version. All notes contain an error message instead of actual card content. Please try: 1) Update Anki to the latest version, 2) Re-export your deck as 'Anki Deck Package (*.apkg)', 3) If the deck was originally imported from a .colpkg file, you may need to recreate the cards manually."
                )
            
            # Get all notes from database, but filter out error messages
            cursor.execute("SELECT id, flds, tags, sfld FROM notes WHERE flds NOT LIKE '%Please update to the latest Anki version%'")
            notes = cursor.fetchall()
            
            if not notes:
                conn.close()
                raise HTTPException(
                    status_code=400, 
                    detail="No valid notes found in Anki deck. All notes appear to contain error messages. This might be a corrupted file or from an incompatible Anki version. Please try re-exporting the deck from Anki."
                )
            
            # Get or create deck
            if deck_id:
                deck = db.query(Deck).filter(
                    Deck.id == deck_id,
                    Deck.user_id == current_user.id
                ).first()
                if not deck:
                    raise HTTPException(status_code=404, detail="Deck not found")
            else:
                # Create a new deck - use deck name from col table if available, otherwise use filename
                if deck_name_from_file:
                    deck_name = deck_name_from_file
                else:
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
                try:
                    # Convert sfld to string if it's not already (it might be an integer in the schema)
                    sfld_str = str(sfld) if sfld is not None else ""
                    
                    # flds is pipe-separated fields (usually front|back for basic cards)
                    fields = flds.split('\x1f') if flds else []  # Anki uses \x1f as field separator
                    
                    if len(fields) < 1:
                        skipped_count += 1
                        continue
                    
                    # Get the first field (main content) and strip HTML
                    main_field = strip_html(fields[0].strip()) if fields[0] else ""
                    
                    # If main_field is empty or looks like an error, try using sfld (sort field) as fallback
                    if not main_field or "Please update to the latest Anki version" in main_field or "import the .colpkg/.apkg file again" in main_field:
                        if sfld_str and sfld_str != "None" and not sfld_str.isdigit():
                            main_field = strip_html(sfld_str.strip())
                            # Re-split fields if we're using sfld - it might be different
                            if not main_field or "Please update to the latest Anki version" in main_field:
                                print(f"Skipping note {note_id} - appears to be an error message or empty")
                                skipped_count += 1
                                continue
                        else:
                            print(f"Skipping note {note_id} - empty field and no valid sfld")
                            skipped_count += 1
                            continue
                except Exception as e:
                    print(f"Error processing note {note_id}: {str(e)}")
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
            
            # Check if we actually created any flashcards
            if created_count == 0:
                db.rollback()
                conn.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"Could not import any flashcards from this Anki deck. All {skipped_count} notes were skipped. This might be an Anki Collection Package (.colpkg) file. Please export your deck from Anki as 'Anki Deck Package (*.apkg)' instead. In Anki: File → Export → Select 'Anki Deck Package (*.apkg)' → Choose your deck → Export."
                )
            
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


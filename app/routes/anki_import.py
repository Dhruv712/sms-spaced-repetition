"""
Anki deck import routes
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
    Also supports HTML cloze format: <span class="cloze" data-cloze="answer">[...]</span>
    Returns (front, back) tuple if cloze found, None otherwise
    """
    if not text or not text.strip():
        return None
    
    # First try HTML cloze format (from plain text export)
    # Pattern matches: <span class="cloze" data-cloze="answer">[...]</span>
    html_cloze_pattern = r'<span\s+class=["\']cloze["\'][^>]*data-cloze=["\']([^"\']+)["\'][^>]*>\[\.\.\.\]</span>'
    html_matches = list(re.finditer(html_cloze_pattern, text, re.IGNORECASE))
    
    if html_matches:
        # Extract all cloze deletions
        cloze_texts = []
        front_text = text
        
        for match in reversed(html_matches):  # Reverse to maintain positions when replacing
            cloze_text = html.unescape(match.group(1))  # Decode HTML entities like &#x20; (space), &#x2E; (.)
            # Clean up the cloze text - remove extra spaces and normalize
            cloze_text = ' '.join(cloze_text.split())
            if cloze_text:  # Only add non-empty clozes
                cloze_texts.append(cloze_text)
            # Replace with ellipsis
            front_text = front_text[:match.start()] + "..." + front_text[match.end():]
        
        if not cloze_texts:  # No valid clozes found
            return None
        
        # For multiple clozes, combine them; otherwise use single answer
        back_text = ", ".join(cloze_texts) if len(cloze_texts) > 1 else cloze_texts[0]
        
        # Strip remaining HTML from front
        front_text = strip_html(front_text)
        back_text = strip_html(back_text)
        
        # Clean up - remove extra spaces and normalize
        front_text = ' '.join(front_text.split())
        back_text = ' '.join(back_text.split())
        
        if not front_text or not back_text:
            return None
        
        return (front_text.strip(), back_text.strip())
    
    # Fall back to Anki {{c1::text}} format
    cloze_pattern = r'\{\{c\d+::(?:[^:]+::)?([^}]+)\}\}'
    
    matches = list(re.finditer(cloze_pattern, text))
    if not matches:
        return None
    
    # Extract all cloze deletions
    cloze_texts = []
    front_text = text
    
    for match in reversed(matches):  # Reverse to maintain positions when replacing
        cloze_text = match.group(1)  # The answer text
        cloze_text = ' '.join(cloze_text.split())  # Normalize spaces
        if cloze_text:  # Only add non-empty clozes
            cloze_texts.append(cloze_text)
        # Replace with ellipsis or placeholder
        front_text = front_text[:match.start()] + "..." + front_text[match.end():]
    
    if not cloze_texts:  # No valid clozes found
        return None
    
    # For multiple clozes, combine them; otherwise use single answer
    back_text = ", ".join(cloze_texts) if len(cloze_texts) > 1 else cloze_texts[0]
    
    # Clean up
    front_text = ' '.join(front_text.split())
    back_text = ' '.join(back_text.split())
    
    if not front_text or not back_text:
        return None
    
    return (front_text.strip(), back_text.strip())


async def import_anki_plain_text(
    file: UploadFile,
    deck_id: int,
    current_user: User,
    db: Session
):
    """
    Import Anki plain text export format using GPT to structure the data
    """
    from openai import OpenAI
    from app.utils.config import settings
    import json
    
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Cannot process Anki import."
        )
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Read file content
    content = await file.read()
    text_content = content.decode('utf-8')
    
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
    
    # Use GPT to parse and structure the Anki export
    prompt = f"""You are parsing an Anki deck export file. Extract all flashcards from the text below and return them as a JSON array.

Each flashcard should have:
- "concept": The front/question/prompt of the card (clean text, no HTML, no cloze markers)
- "definition": The back/answer/explanation of the card (clean text, no HTML)
- "tags": Optional comma-separated tags if present, otherwise empty string

Rules:
1. For cloze deletion cards (with {{c1::...}} or <span class="cloze">), extract the full question with "..." where the cloze deletion is, and put the answer in the definition field
2. Remove all HTML tags and entities (convert &nbsp; to spaces, etc.)
3. Skip empty cards or cards with no meaningful content
4. Clean up extra whitespace
5. If a card has multiple cloze deletions, combine all answers in the definition separated by commas
6. Return ONLY valid JSON, no markdown code blocks, no explanation

Example input:
"A human hair is ~<span class=""cloze"" data-cloze=""50&#x20;um"" data-ordinal=""1"">[...]</span> in diameter."	"A human hair is ~<span class=""cloze"" data-ordinal=""1"">50 um</span> in diameter."

Example output:
[
  {{
    "concept": "A human hair is ~ ... in diameter.",
    "definition": "A human hair is ~ 50 um in diameter.",
    "tags": ""
  }}
]

Now parse this Anki export:
{text_content[:50000]}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistent parsing
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Strip markdown code block if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            flashcards_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Response text: {response_text[:500]}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to parse GPT response as JSON. Please try again or contact support."
            )
        
        if not isinstance(flashcards_data, list):
            raise HTTPException(
                status_code=500,
                detail="GPT returned invalid format. Expected a JSON array."
            )
        
        # Enforce 100 card limit
        if len(flashcards_data) > 100:
            raise HTTPException(
                status_code=400,
                detail=f"This import contains {len(flashcards_data)} cards, which exceeds the limit of 100 cards per import. Please split your deck into smaller files."
            )
        
        # Create flashcards from structured data
        created_count = 0
        skipped_count = 0
        
        for card_data in flashcards_data:
            try:
                if not isinstance(card_data, dict):
                    skipped_count += 1
                    continue
                
                concept = card_data.get("concept", "").strip()
                definition = card_data.get("definition", "").strip()
                tags = card_data.get("tags", "").strip()
                
                # Skip if concept or definition is empty
                if not concept or not definition:
                    skipped_count += 1
                    continue
                
                # Create flashcard
                flashcard = Flashcard(
                    concept=concept,
                    definition=definition,
                    tags=tags if tags else None,
                    deck_id=deck.id,
                    user_id=current_user.id
                )
                db.add(flashcard)
                created_count += 1
                
            except Exception as e:
                print(f"Error creating flashcard from GPT data: {str(e)}")
                skipped_count += 1
                continue
        
        if created_count == 0:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=f"Could not import any flashcards. GPT parsed {len(flashcards_data)} cards but none were valid. Please check your Anki export file."
            )
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Imported {created_count} flashcards from Anki export (GPT-parsed)",
            "deck_id": deck.id,
            "deck_name": deck.name,
            "created_count": created_count,
            "skipped_count": skipped_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in GPT parsing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing Anki import with GPT: {str(e)}"
        )


@router.post("/import")
async def import_anki_deck(
    file: UploadFile = File(...),
    deck_id: int = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import an Anki deck (.apkg file) and create flashcards
    Available for all users (free and premium)
    """
    
    # Validate file type - support .apkg, .colpkg, and .txt (plain text export)
    if not (file.filename.endswith('.apkg') or file.filename.endswith('.colpkg') or file.filename.endswith('.txt')):
        raise HTTPException(status_code=400, detail="File must be an .apkg, .colpkg, or .txt file (Anki plain text export)")
    
    # Handle plain text export format (.txt)
    if file.filename.endswith('.txt'):
        return await import_anki_plain_text(file, deck_id, current_user, db)
    
    # Handle .apkg/.colpkg format (zip file with database)
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
            
            # Get a sample note to see what we're working with - also check the data field
            cursor.execute("SELECT id, flds, tags, sfld, data FROM notes LIMIT 5")
            sample_notes = cursor.fetchall()
            print(f"Sample notes (first 5):")
            for sample in sample_notes:
                sample_flds = str(sample[1]) if sample[1] is not None else ""
                sample_sfld = str(sample[3]) if sample[3] is not None else ""
                sample_data = str(sample[4]) if sample[4] is not None else ""
                print(f"  Note {sample[0]}: flds={sample_flds[:100]}, sfld={sample_sfld[:100]}, data={sample_data[:100]}")
            
            # Check if we have cards table and see what's there
            if 'cards' in tables:
                cursor.execute("SELECT COUNT(*) FROM cards")
                card_count = cursor.fetchone()[0]
                print(f"Total cards in cards table: {card_count}")
                
                if card_count > 0:
                    # Get a sample card to see structure
                    cursor.execute("SELECT id, nid, did, ord FROM cards LIMIT 1")
                    sample_card = cursor.fetchone()
                    if sample_card:
                        print(f"Sample card: id={sample_card[0]}, nid={sample_card[1]}, did={sample_card[2]}, ord={sample_card[3]}")
            
            # Get a sample note to check for error messages
            if sample_notes:
                sample = sample_notes[0]
                sample_flds = str(sample[1]) if sample[1] is not None else ""
                sample_sfld = str(sample[3]) if sample[3] is not None else ""
                
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
            
            # Check models table to see what note types exist
            if 'notetypes' in tables or 'models' in tables:
                model_table = 'notetypes' if 'notetypes' in tables else 'models'
                cursor.execute(f"SELECT COUNT(*) FROM {model_table}")
                model_count = cursor.fetchone()[0]
                print(f"Found {model_count} note types/models")
                
                if model_count > 0:
                    cursor.execute(f"SELECT id, name, flds FROM {model_table} LIMIT 1")
                    sample_model = cursor.fetchone()
                    if sample_model:
                        print(f"Sample model: id={sample_model[0]}, name={sample_model[1]}, flds={sample_model[2][:100] if sample_model[2] else None}")
            
            # Get all notes from database, but filter out error messages
            cursor.execute("SELECT id, flds, tags, sfld FROM notes WHERE flds NOT LIKE '%Please update to the latest Anki version%'")
            notes = cursor.fetchall()
            
            # If we filtered out all notes, let's check if there are ANY notes with actual content
            if not notes:
                # Try getting notes that don't match the exact error message pattern
                cursor.execute("SELECT id, flds, tags, sfld FROM notes WHERE flds IS NOT NULL AND flds != '' AND LENGTH(flds) > 10 AND flds NOT LIKE '%Please update to the latest Anki version%'")
                notes = cursor.fetchall()
                print(f"After filtering: found {len(notes)} notes with content")
            
            if not notes:
                conn.close()
                raise HTTPException(
                    status_code=400, 
                    detail="No valid notes found in Anki deck. All notes contain the error message 'Please update to the latest Anki version, then import the .colpkg/.apkg file again.' This means the deck in Anki itself has this error message stored. To fix: 1) Open the deck in Anki and check if the cards display correctly, 2) If they show the error message in Anki too, you need to recreate the deck, 3) If they show correctly in Anki, try updating Anki to the latest version and re-exporting the deck."
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
            
            # Enforce 100 card limit
            if created_count > 100:
                db.rollback()
                conn.close()
                raise HTTPException(
                    status_code=400,
                    detail=f"This import contains {created_count} cards, which exceeds the limit of 100 cards per import. Please split your deck into smaller files."
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
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except sqlite3.Error as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error reading Anki database: {str(e)}")
        except Exception as e:
            db.rollback()
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error importing Anki deck: {str(e)}")
            print(f"Traceback: {error_trace}")
            raise HTTPException(status_code=500, detail=f"Error importing deck: {str(e)}")


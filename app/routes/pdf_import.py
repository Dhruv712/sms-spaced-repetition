"""
PDF to flashcards import routes (Premium feature)
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard, Deck
from app.services.auth import get_current_active_user
from openai import OpenAI
from app.utils.config import settings
import json
import os
import tempfile

router = APIRouter()


async def extract_text_from_pdf(file: UploadFile) -> str:
    """
    Extract text from PDF file
    """
    try:
        import pypdf
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="PDF processing library not installed. Please contact support."
        )
    
    # Read PDF content
    content = await file.read()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Extract text from PDF
        text_content = []
        with open(tmp_path, 'rb') as pdf_file:
            pdf_reader = pypdf.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return '\n\n'.join(text_content)
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/import")
async def import_flashcards_from_pdf(
    file: UploadFile = File(...),
    instructions: str = Form(""),
    deck_id: int = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Import flashcards from PDF using GPT
    Premium feature only
    """
    # Check premium status
    if not current_user.is_premium:
        raise HTTPException(
            status_code=403,
            detail="PDF import is a premium feature. Please upgrade to Premium to use this feature."
        )
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF (.pdf)")
    
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured. Cannot process PDF import."
        )
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Extract text from PDF
    try:
        pdf_text = await extract_text_from_pdf(file)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting text from PDF: {str(e)}"
        )
    
    if not pdf_text or not pdf_text.strip():
        raise HTTPException(
            status_code=400,
            detail="Could not extract any text from the PDF. Please ensure the PDF contains readable text."
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
        # Create a new deck with the filename (without extension)
        deck_name = os.path.splitext(file.filename)[0] if file.filename else "PDF Import"
        deck = Deck(
            name=deck_name,
            user_id=current_user.id
        )
        db.add(deck)
        db.flush()
    
    # Build GPT prompt with base instructions + user instructions
    base_instructions = """Base instructions:
- Don't create too many flashcards (aim for 10-30 cards unless the user specifies otherwise)
- Keep flashcards concise - concepts should be brief questions or prompts, definitions should be clear but not overly long
- Focus on key concepts, important facts, and essential information
- Skip trivial details or overly specific information
- If the PDF is very long, prioritize the most important content"""
    
    user_instructions_text = f"\n\nUser's specific instructions:\n{instructions}" if instructions.strip() else ""
    
    prompt = f"""You are creating flashcards from a PDF document. {base_instructions}{user_instructions_text}

Extract flashcards from the PDF text below and return them as a JSON array.

Each flashcard should have:
- "concept": The front/question/prompt of the card (brief and clear)
- "definition": The back/answer/explanation of the card (concise but complete)
- "tags": Optional comma-separated tags relevant to the content, otherwise empty string

Rules:
1. Create high-quality flashcards that test understanding, not just memorization
2. Keep concepts brief (ideally one sentence or phrase)
3. Keep definitions concise but informative (2-3 sentences max)
4. Focus on important concepts, key facts, definitions, and relationships
5. Skip trivial details, examples that are too specific, or content that doesn't make good flashcards
6. Return ONLY valid JSON, no markdown code blocks, no explanation
7. Follow the user's specific instructions above

PDF content:
{pdf_text[:100000]}  # Limit to 100k chars to avoid token limits
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Low temperature for consistent output
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
                detail=f"This import contains {len(flashcards_data)} cards, which exceeds the limit of 100 cards per import. Please split your PDF into smaller sections or adjust your instructions to create fewer cards."
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
                detail=f"Could not create any flashcards. GPT parsed {len(flashcards_data)} cards but none were valid. Please try adjusting your instructions."
            )
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Created {created_count} flashcards from PDF",
            "deck_id": deck.id,
            "deck_name": deck.name,
            "created_count": created_count,
            "skipped_count": skipped_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error in GPT processing: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF with GPT: {str(e)}"
        )


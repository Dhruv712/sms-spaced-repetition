from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Flashcard, User
from app.dependencies.auth import get_current_active_user
from openai import OpenAI
import os
import json
import re

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/generate_flashcard")
def generate_flashcard_from_text(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    text = data.get("text")
    save_directly = data.get("save_directly", False)  # Default to False for web interface

    if not text:
        raise HTTPException(status_code=400, detail="Missing text")

    prompt = f"""
You are an assistant that extracts flashcards from natural language.

Each flashcard has two fields:
- concept: what the user is trying to remember
- definition: the answer, explanatio, or formula (use LaTeX if the definition is a formula)
– tags: tags requested by the user, comma-separated. If no tags requested, this is an empty string.

Return ONLY a JSON object with 'concept' and 'definition' fields. No text before or after it.

Examples:

Input: "make a card about how Pretoria is Elon Musk's birthplace, with biography and Elon tags"
Output: {{
  "concept": "Elon Musk's birthplace",
  "definition": "Pretoria",
  "tags": biography, Elon
  
}}

Input: "create a card for the capital of Japan"
Output: {{
  "concept": "Capital of Japan",
  "definition": "Tokyo",
  "tags": ""
}}

Input: "create a card for Ohm's law"
Output: {{
  "concept": "Ohm's law",
  "definition": "$$ V = IR $$",
  "tags": ""
}}

Important:
- Use double quotes around all keys and string values.
- Escape all backslashes in LaTeX as \\\\ (double-escaped for JSON validity).
- Return only a raw JSON object with no explanation.

Now convert this into a flashcard:
"{text}"
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        response_text = completion.choices[0].message.content.strip()

        try:
            card_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: escape single backslashes and try again
            safe_text = re.sub(r'(?<!\\)\\(?![\\ntr"])', r'\\\\', response_text)
            card_data = json.loads(safe_text)

        if "concept" not in card_data or "definition" not in card_data or "tags" not in card_data:
            raise ValueError("Invalid format from GPT")

        if save_directly:
            new_card = Flashcard(
                user_id=current_user.id,
                concept=card_data["concept"],
                definition=card_data["definition"],
                tags=card_data["tags"],
            )
            db.add(new_card)
            db.commit()
            db.refresh(new_card)
            return new_card
        else:
            return card_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create flashcard: {e}")

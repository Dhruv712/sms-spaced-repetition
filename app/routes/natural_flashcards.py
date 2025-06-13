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

Each flashcard has three fields:
- concept: what the user is trying to remember
- definition: the answer, explanation, or formula (use LaTeX if the definition is a formula)
- tags: tags requested by the user, comma-separated. If no tags requested, this is an empty string.
- source_url: the URL of the source you used to verify the information. If no source was used, this should be an empty string.

Return ONLY a JSON object with these fields. No text before or after it.

Examples:

Input: "make a card about how Pretoria is Elon Musk's birthplace, with biography and Elon tags"
Output: {{
  "concept": "Elon Musk's birthplace",
  "definition": "Pretoria",
  "tags": "biography, Elon",
  "source_url": "https://example.com/elon-musk-biography"
}}

Input: "create a card for the capital of Japan"
Output: {{
  "concept": "Capital of Japan",
  "definition": "Tokyo",
  "tags": "",
  "source_url": "https://example.com/japan-capital"
}}

Input: "create a card for Ohm's law"
Output: {{
  "concept": "Ohm's law",
  "definition": "$$ V = IR $$",
  "tags": "",
  "source_url": ""
}}

Important:
- Use double quotes around all keys and string values.
- Escape all backslashes in LaTeX as \\\\ (double-escaped for JSON validity).
- Return only a raw JSON object with no explanation.
- Always include a source_url field, even if empty.

Now convert this into a flashcard:
"{text}"
"""

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-search-preview",
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = completion.choices[0].message.content.strip()
        print("Raw response:", response_text)

        # Strip markdown code block if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove trailing ```
        response_text = response_text.strip()
        print("Cleaned response:", response_text)

        try:
            card_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Error position: {e.pos}")
            print(f"Line: {e.lineno}, Column: {e.colno}")
            # Fallback: escape single backslashes and try again
            safe_text = re.sub(r'(?<!\\)\\(?![\\ntr"])', r'\\\\', response_text)
            print("Attempting with escaped backslashes:", safe_text)
            try:
                card_data = json.loads(safe_text)
            except json.JSONDecodeError as e2:
                print(f"Second JSON decode error: {str(e2)}")
                raise ValueError(f"Could not parse LLM response as JSON. Raw response:\n{response_text}")

        print("Parsed card data:", card_data)

        if "concept" not in card_data or "definition" not in card_data or "tags" not in card_data or "source_url" not in card_data:
            print("Missing required fields in parsed JSON:", card_data)
            raise ValueError("Invalid format from GPT - missing required fields")

        # Print source URL regardless of save_directly
        if "source_url" in card_data:
            print("Source URL from card data (pre-sanitization):", card_data["source_url"])

        if save_directly:
            source_url = card_data["source_url"].lstrip('@').strip()
            print("Source URL (after sanitization):", source_url)
            new_card = Flashcard(
                user_id=current_user.id,
                concept=card_data["concept"],
                definition=card_data["definition"],
                tags=card_data["tags"],
                source_url=source_url
            )
            db.add(new_card)
            db.commit()
            db.refresh(new_card)
            return new_card
        else:
            return card_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create flashcard: {e}")

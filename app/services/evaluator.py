from openai import OpenAI
from app.utils.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def evaluate_answer(concept: str, correct_definition: str, user_response: str):
    prompt = f"""You're a helpful tutor. Grade the student's answer.

Concept: {concept}
Definition: {correct_definition}
Student Answer: {user_response}

Respond in JSON like this:
{{
  "was_correct": true/false,
  "confidence_score": float (0 to 1),
  "llm_feedback": "short feedback here"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        return parsed
    except json.JSONDecodeError:
        raise ValueError(f"LLM response not parsable:\n{content}")

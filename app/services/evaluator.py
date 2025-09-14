from openai import OpenAI
from app.utils.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def evaluate_answer(concept: str, correct_definition: str, user_response: str):
    prompt = f"""You're a helpful tutor. Grade the student's answer, focusing on intuition and important details.
    Remember, don't be a stickler for unimportant details. For example, if the correct answer is "Robert Oppenheimer was born
    on the 12th of June" and they say "Oppie was born June 12", of course that's still correct.
    In other words, use your intuition to determine if the student has the right answer. 
    And if they get it wrong, ALWAYS give them the right answer in your feedback so they can study and get it right next time.

Concept: {concept}
Correct Definition: {correct_definition}
Student's Answer: {user_response}

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
        temperature=0.3,
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        return parsed
    except json.JSONDecodeError:
        raise ValueError(f"LLM response not parsable:\n{content}")

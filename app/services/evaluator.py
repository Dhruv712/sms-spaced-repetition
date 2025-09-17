from openai import OpenAI
from app.utils.config import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def evaluate_answer(concept: str, correct_definition: str, user_response: str):
    prompt = f"""
    You are a STRICT, TERSE GRADER for a flashcard app.
    Your job: decide if the student’s answer captures the essential idea(s), not the wording.

    Rules
    - Prioritize MATERIAL POINTS ONLY. Ignore trivial phrasing, synonyms, extra context, or small omissions.
    - If the core idea is present → mark correct even if wording differs.
    - If partially correct but the key idea is there, or if only slightly misspelled → mark correct and add ONE short reminder.
    - If wrong or the key idea is missing → mark incorrect and provide the right answer.
    - Be concise. No compliments, no exclamation marks, no hedging, no multi-sentence lectures.
    - Max feedback length: 140 characters.
    - Output EXACT JSON. No prose before/after.

    Process
    1) Extract 1–3 essential key points from the Correct Definition.
    2) Check if the Student's Answer expresses those key points (allow paraphrase).
    3) Decide correctness:
    - Correct if the main point(s) are clearly present.
    - Incorrect only if a core idea is absent or contradicted.
    4) Compose feedback:
    - If correct: "Correct." or "Correct. (brief reminder)" where the reminder is a single clause if truly helpful.
    - If incorrect: "Incorrect. Correct answer: <concise correct answer>"

    Concept: {concept}
    Correct Definition: {correct_definition}
    Student's Answer: {user_response}

    Respond in JSON EXACTLY like this:
    {{
    "was_correct": true/false,
    "confidence_score": float (0 to 1, one decimal place),
    "llm_feedback": "≤140 chars, per the rules"
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

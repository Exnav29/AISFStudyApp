import os
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_quiz_questions(content: str, num_questions: int = 5) -> list:
    prompt = f"Generate {num_questions} quiz questions based on the following content. Include multiple-choice, true/false, and fill-in-the-blank questions. Format the response as a JSON array of question objects, each with 'question', 'type', 'options' (for multiple-choice), and 'answer' fields: {content}"

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content

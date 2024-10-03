import os
import PyPDF2
from openai import OpenAI

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def extract_pdf_content(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        content = ""
        for page in reader.pages:
            content += page.extract_text()
    return content

def generate_quiz_questions(pdf_name: str, num_questions: int = 5) -> list:
    pdf_path = os.path.join('static', 'pdfs', pdf_name)
    content = extract_pdf_content(pdf_path)
    
    prompt = f"Generate {num_questions} quiz questions based on the following content from {pdf_name}. Include multiple-choice, true/false, and fill-in-the-blank questions. Format the response as a JSON array of question objects, each with 'question', 'type', 'options' (for multiple-choice), and 'answer' fields. Content: {content[:4000]}"  # Limiting content to 4000 characters to avoid token limit

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content

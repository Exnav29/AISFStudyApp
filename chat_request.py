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
    
    prompt = f"""Generate {num_questions} quiz questions based on the following content from {pdf_name}. 
    Include a mix of the following question types:
    1. Multiple-choice
    2. True/false
    3. Fill-in-the-blank
    4. Matching
    5. Ordering
    6. Short answer
    
    Format the response as a JSON array of question objects, each with 'question', 'type', 'options' (if applicable), and 'answer' fields. 
    For matching and ordering questions, include 'items' and 'correct_order' fields.
    
    Content: {content[:4000]}"""  # Limiting content to 4000 characters to avoid token limit

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("OpenAI returned an empty response.")
    return content

def generate_lesson(pdf_name: str) -> str:
    pdf_path = os.path.join('static', 'pdfs', pdf_name)
    content = extract_pdf_content(pdf_path)
    
    prompt = f"""Generate a comprehensive lesson based on the following content from {pdf_name}. 
    The lesson should include:
    1. An introduction to the topic
    2. Key concepts and definitions
    3. Detailed explanations of important points
    4. Examples or case studies to illustrate the concepts
    5. A summary of the main takeaways

    Format the response as HTML, using appropriate tags for headings, paragraphs, lists, etc.
    
    Content: {content[:4000]}"""  # Limiting content to 4000 characters to avoid token limit

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    lesson_content = response.choices[0].message.content
    if not lesson_content:
        raise ValueError("OpenAI returned an empty response.")
    return lesson_content

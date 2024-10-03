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

def extract_exam_objectives(pdf_path):
    content = extract_pdf_content(pdf_path)
    prompt = f"""Extract and list the exam objectives from the following content:

    {content[:4000]}

    Return the objectives as a JSON array of strings."""

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content

def generate_lesson() -> dict:
    pdf_dir = os.path.join('static', 'pdfs')
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    
    # Extract exam objectives
    objectives_pdf = "DRAFT_AKYLADE_AI_Security_Foundation_AAISF_AIF_001_Exam_Objectives_v_1.pdf"
    objectives = extract_exam_objectives(os.path.join(pdf_dir, objectives_pdf))
    
    all_content = ""
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        all_content += extract_pdf_content(pdf_path) + "\n\n"
    
    prompt = f"""Generate a comprehensive lesson based on the following content from multiple PDFs. 
    Organize the lesson according to these exam objectives: {objectives}

    For each objective, include:
    1. An introduction to the topic
    2. Key concepts and definitions
    3. Detailed explanations of important points
    4. Examples or case studies to illustrate the concepts
    5. A summary of the main takeaways

    Format the response as JSON, with each objective as a key and its corresponding lesson content as the value.
    The lesson content for each objective should be formatted as HTML.
    
    Content: {all_content[:8000]}"""  # Increased character limit to accommodate multiple PDFs

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    lesson_content = response.choices[0].message.content
    if not lesson_content:
        raise ValueError("OpenAI returned an empty response.")
    return lesson_content

def generate_quiz_questions(pdf_name: str, num_questions: int = 5) -> list:
    # Existing implementation...
    pass

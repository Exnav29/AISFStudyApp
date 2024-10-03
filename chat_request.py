import os
import PyPDF2
from openai import OpenAI
import logging
from io import BytesIO

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def extract_pdf_content(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file, strict=False)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
        return content
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"Error reading PDF {pdf_path}: {str(e)}")
        if "EOF marker not found" in str(e):
            logger.warning(f"Attempting to repair PDF {pdf_path}")
            try:
                with open(pdf_path, 'rb') as file:
                    content = file.read()
                fixed_content = content.replace(b'\x0d', b'\x0a')
                reader = PyPDF2.PdfReader(BytesIO(fixed_content), strict=False)
                content = ""
                for page in reader.pages:
                    content += page.extract_text()
                return content
            except Exception as repair_error:
                logger.error(f"Failed to repair PDF {pdf_path}: {str(repair_error)}")
                raise ValueError(f"Failed to read or repair PDF: {str(repair_error)}")
        else:
            raise ValueError(f"Error reading PDF: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error reading PDF {pdf_path}: {str(e)}")
        raise ValueError(f"Unexpected error reading PDF: {str(e)}")

def extract_exam_objectives(pdf_path):
    try:
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
    except Exception as e:
        logger.error(f"Error extracting exam objectives: {str(e)}")
        raise ValueError(f"Error extracting exam objectives: {str(e)}")

def generate_lesson() -> dict:
    try:
        pdf_dir = os.path.join('static', 'pdfs')
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        objectives_pdf = "DRAFT_AKYLADE_AI_Security_Foundation_AAISF_AIF_001_Exam_Objectives_v_1.pdf"
        objectives_path = os.path.join(pdf_dir, objectives_pdf)
        
        if not os.path.exists(objectives_path):
            raise FileNotFoundError(f"Exam objectives PDF not found: {objectives_pdf}")
        
        objectives = extract_exam_objectives(objectives_path)
        
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
        
        Content: {all_content[:8000]}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        lesson_content = response.choices[0].message.content
        if not lesson_content:
            raise ValueError("OpenAI returned an empty response.")
        return lesson_content
    except FileNotFoundError as e:
        logger.error(str(e))
        raise
    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_lesson: {str(e)}")
        raise ValueError(f"Unexpected error generating lesson: {str(e)}")

def generate_quiz_questions(pdf_name: str, num_questions: int = 5) -> list:
    try:
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
        
        Content: {content[:4000]}"""

        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        questions = response.choices[0].message.content
        if not questions:
            raise ValueError("OpenAI returned an empty response.")
        return questions
    except Exception as e:
        logger.error(f"Error generating quiz questions: {str(e)}")
        raise ValueError(f"Error generating quiz questions: {str(e)}")
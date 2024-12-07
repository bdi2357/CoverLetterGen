import os
import json
import csv
import fitz
import base64
import re
from typing import Tuple, Dict
from openai import OpenAI
from dotenv import load_dotenv

import json
import re

import os
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
from ai_interaction import OpenAIModel
from typing import Tuple, Dict
import base64
import requests
load_dotenv('.env', override=True)

class ResumeEvaluator:
    def __init__(self, ai_model: OpenAI, output_folder: str):
        """
        Initialize the ResumeEvaluator.

        Args:
            ai_model (OpenAI): An instance of OpenAI API.
            output_folder (str): Directory where the evaluations and CSV file will be stored.
        """
        self.ai_model = ai_model
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)

    def extract_first_page_as_image(self, pdf_path: str) -> str:
        """
        Extract the first page of a PDF as a PNG image.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Path to the saved PNG file.
        """
        image_path = os.path.join(self.output_folder, os.path.basename(pdf_path).replace('.pdf', '.png'))
        pdf_document = fitz.open(pdf_path)
        page = pdf_document[0]
        pix = page.get_pixmap()
        pix.save(image_path)
        pdf_document.close()
        return image_path

    def question_image(self, image_path: str, query: str) -> str:
        """
        Analyze an image with a visual query using OpenAI's API.

        Args:
            image_path (str): Path to the image file.
            query (str): Query for analyzing the image.

        Returns:
            str: The analysis response from the model.
        """
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                    ]
                }
            ],
            "max_tokens": 1000
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code != 200:
            raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")
        json_response = response.json()
        if "choices" in json_response:
            return json_response['choices'][0]['message']['content']
        else:
            raise KeyError("The API response does not contain 'choices'.")

    def evaluate_resume(self, pdf_path: str, query: str) -> Tuple[str, Dict[str, float]]:
        """
        Evaluate a resume using the provided query.

        Args:
            pdf_path (str): Path to the PDF file.
            query (str): Query to analyze the resume's visual appeal.

        Returns:
            Tuple[str, Dict[str, float]]: The detailed evaluation text and grades.
        """
        image_path = self.extract_first_page_as_image(pdf_path)
        vision_response = self.question_image(image_path, query)
        grades = {}
        try:
            match = re.search(r"\{.*?\}", vision_response, re.DOTALL)
            if match:
                grades_text = match.group(0)
                grades = json.loads(grades_text)
            else:
                raise ValueError("Grades section not found in the response.")
        except json.JSONDecodeError as e:
            grades = {"error": f"Failed to parse grades (JSON error): {e}"}
        return vision_response, grades


def main():
    #load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Set it in the .env file.")

    ai_model = OpenAI(api_key=openai_api_key)
    evaluator = ResumeEvaluator(ai_model, output_folder=os.path.join("Output", "VisualEval"))

    # Directory containing CV files
    input_directory = os.path.join("Data", "CV")
    csv_output_path = os.path.join(evaluator.output_folder, "cv_visual_evaluation.csv")

    query = """
    Evaluate the visual appeal of this CV with a focus on identifying the best design for professional purposes. Assess the following criteria:

    1. **Layout and Structure**: Is the content organized logically, with clear headers and well-defined sections? Are sections like Work Experience, Education, and Skills easy to locate?

    2. **Font Consistency and Size**: Are fonts consistent across the document, including bullet points? Evaluate whether font sizes differentiate effectively between headers and body text, emphasizing important information like the name and section titles.

    3. **Visual Hierarchy and Readability**: How well does the design guide the reader's eye? Assess whether the use of bold text, spacing, and alignment makes critical information stand out while maintaining a clear flow.

    4. **Use of Colors, Lines, or Separators**: Are colors, lines, and separators used professionally and consistently? Highlight whether elements like shading or borders enhance the document's clarity and visual structure.

    5. **Suitability for Professional Use**: Does the design align with standards for the relevant industry, such as corporate, technical, or creative roles?

    6. **Overall Professionalism and Aesthetic Appeal**: Consider the overall balance of design elements, readability, and professionalism. Is the CV visually engaging without unnecessary complexity?

    Provide detailed textual reasoning for each criterion, and return a JSON object with grades (0–10) for:
       - Layout and Structure
       - Font Consistency and Size
       - Visual Hierarchy and Readability
       - Use of Colors, Lines, or Separators
       - Suitability for Professional Use
       - Overall Professionalism and Aesthetic Appeal
       - Overall Grade (average of the above scores)
    """

    # Prepare the CSV file
    with open(csv_output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["file_path", "Layout and structure", "Font consistency and size",
                      "Visual hierarchy and readability", "Use of colors, lines, or separators",
                      "Suitability for professional use", "Overall Grade"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Process each CV file
        for file_name in os.listdir(input_directory):
            if file_name.endswith(".pdf"):
                pdf_path = os.path.join(input_directory, file_name)
                try:
                    detailed_evaluation, grades = evaluator.evaluate_resume(pdf_path, query)

                    # Save the textual description
                    text_output_path = os.path.join(evaluator.output_folder, f"{file_name}.txt")
                    with open(text_output_path, mode='w', encoding='utf-8') as textfile:
                        textfile.write(detailed_evaluation)

                    # Write grades to CSV
                    row = {
                        "file_path": pdf_path,
                        "Layout and structure": grades.get("Layout and Structure", "N/A"),
                        "Font consistency and size": grades.get("Font Consistency and Size", "N/A"),
                        "Visual hierarchy and readability": grades.get("Visual Hierarchy and Readability", "N/A"),
                        "Use of colors, lines, or separators": grades.get("Use of Colors, Lines, or Separators", "N/A"),
                        "Suitability for professional use": grades.get("Suitability for Professional Use", "N/A"),
                        "Overall Grade": grades.get("Overall Grade", "N/A"),
                    }
                    writer.writerow(row)

                except Exception as e:
                    print(f"Failed to evaluate {pdf_path}: {e}")

    print(f"Evaluation completed. Results saved to {csv_output_path}")


if __name__ == "__main__":
    main()

import PyPDF2
from ai_interaction import OpenAIModel
from typing import Tuple, Dict
from dotenv import load_dotenv
import os
import json
import re
class ResumeEvaluator:
    def __init__(self, ai_model: OpenAIModel):
        """
        Initialize the ResumeEvaluator with a specific LLM model.

        Args:
            ai_model (OpenAIModel): An instance of the OpenAIModel class.
        """
        self.ai_model = ai_model

    def read_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            str: Extracted text content of the PDF.
        """
        pdf_text = []
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                pdf_text.append(page.extract_text())
        return "\n".join(pdf_text)

    import json
    import re

    def evaluate_resume(self, file_path: str) -> Tuple[str, Dict[str, float]]:
        """
        Evaluate the resume using the OpenAI model and return a detailed textual description and grading criteria.

        Args:
            file_path (str): Path to the PDF resume.

        Returns:
            Tuple[str, Dict[str, float]]: A detailed textual evaluation and a dictionary of grades.
        """
        # Extract the content of the PDF
        pdf_content = self.read_pdf(file_path)

        # Construct the improved prompt for the OpenAI model
        prompt = f"""
        You are tasked with evaluating the graphical appeal of the following resume content based on the criteria below. 
        Please provide the output in the following structured format:

        1. A **detailed textual description** for each criterion, covering its strengths and areas for improvement.
        2. A **JSON-like dictionary structure** containing numerical grades (0–10) for each criterion:
           - Visual Hierarchy
           - Font Style and Size
           - Spacing and Alignment
           - Bullet Points
           - Use of Color
           - Borders and Separators
           - Overall Layout

        3. Additionally, calculate an **Average Grade** based on the numerical grades.

        Here is the resume content:
        {pdf_content}
        """

        # Get the LLM response
        response = self.ai_model.get_response(prompt)

        # Initialize output variables
        description = response.strip()
        grades = {}

        try:
            # Extract JSON-like structure using regex
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                grades_text = match.group(0)

                # Clean and validate JSON format
                cleaned_grades_text = grades_text.replace("```json", "").replace("```", "").strip()
                grades = json.loads(cleaned_grades_text)
            else:
                raise ValueError("Grades section not found in the response.")

            # Calculate average grade if grades were parsed
            if grades:
                numerical_grades = [value for value in grades.values() if isinstance(value, (int, float))]
                grades["Average Grade"] = sum(numerical_grades) / len(numerical_grades)

        except json.JSONDecodeError as e:
            description += f"\n\nError parsing grades (JSON error): {e}"
        except Exception as e:
            description += f"\n\nUnexpected error parsing grades: {e}"

        return description, grades


# Example Usage
if __name__ == "__main__":
    # Replace with your actual OpenAI API key
    load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    ai_model = OpenAIModel(api_key=openai_api_key, model_name="gpt-4o")
    evaluator = ResumeEvaluator(ai_model)

    file_path = os.path.join("Output","CV","CV_Rise_DataScientist.pdf")  # Replace with the actual file path
    evaluation_text, grades = evaluator.evaluate_resume(file_path)

    print("Detailed Evaluation:")
    print(evaluation_text)
    print("\nGrades:")
    print(grades)

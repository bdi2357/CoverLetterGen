import os
import json
import csv
import fitz
import base64
import re
from typing import Tuple, Dict
from openai import OpenAI
from dotenv import load_dotenv
from matplotlib import pyplot as plt
import json
import re
import pandas as pd
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

    def evaluate_resumeX(self, pdf_path: str, query: str, csv_path: str) -> Tuple[str, Dict[str, float]]:
        """
        Evaluate a resume using the provided query and update the CSV with grades and histogram information.

        Args:
            pdf_path (str): Path to the PDF file.
            query (str): Query to analyze the resume's visual appeal.
            csv_path (str): Path to the CSV file where results are recorded.

        Returns:
            Tuple[str, Dict[str, float]]: The detailed evaluation text and grades.
        """
        # Step 1: Extract the first page image
        image_path = self.extract_first_page_as_image(pdf_path)

        # Step 2: Get visual evaluation response
        vision_response = self.question_image(image_path, query)

        # Step 3: Parse grades from the response
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

        # Step 4: Generate grade histogram and update CSV
        self.update_csv_and_generate_graphic(csv_path, pdf_path, grades)

        return vision_response, grades

    def update_csv_and_generate_graphic(self, csv_path: str, file_path: str, grades: Dict[str, float]):
        """
        Update the CSV with grades and generate histogram for grade visualization.

        Args:
            csv_path (str): Path to the CSV file.
            file_path (str): Path to the evaluated CV file.
            grades (Dict[str, float]): Grades extracted from the evaluation.
        """
        # Load the CSV data
        data = pd.read_csv(csv_path)
        overall_grade = grades.get("Overall Grade", 0)
        grade_columns = [
            "Layout and Structure",
            "Font Consistency and Size",
            "Visual Hierarchy and Readability",
            "Use of Colors, Lines, or Separators",
            "Suitability for Professional Use",
            "Overall Professionalism and Aesthetic Appeal",
        ]

        # Ensure the grades dictionary contains all fields
        for col in grade_columns:
            grades.setdefault(col, 0)

        # Step 1: Add/update grades for the current file
        new_row = {
            "file_path": file_path,
            "Overall Grade": overall_grade,
            **{col: grades.get(col, "N/A") for col in grade_columns},
        }
        #data = data.append(new_row, ignore_index=True)
        data = pd.concat([data, pd.DataFrame([new_row])], ignore_index=True)

        # Step 2: Analyze grade position and generate histogram
        grades_list = data["Overall Grade"].dropna().astype(float).tolist()
        histogram_image_path = os.path.join(self.output_folder, f"{os.path.basename(file_path)}_histogram.png")
        self.plot_histogram(grades_list, overall_grade, histogram_image_path)

        # Step 3: Update grade position
        position = self.evaluate_grade_position(grades_list, overall_grade)
        data.loc[data['file_path'] == file_path, 'Grade Position'] = position
        data.loc[data['file_path'] == file_path, 'Histogram Image Path'] = histogram_image_path

        # Save updated CSV
        updated_csv_path = csv_path.replace(".csv", "_updated.csv")
        data.to_csv(updated_csv_path, index=False)
        print(f"Updated CSV saved to {updated_csv_path}")

    def plot_histogram(self, grades: list, current_grade: float, output_image_path: str):
        """
        Plot a histogram showing grade distribution and the current grade.

        Args:
            grades (list): List of all grades.
            current_grade (float): The grade of the current CV.
            output_image_path (str): Path to save the histogram image.
        """
        plt.figure(figsize=(8, 6))
        plt.hist(grades, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
        plt.axvline(current_grade, color='red', linestyle='--', linewidth=2,
                    label=f"Current Grade: {current_grade:.2f}")
        plt.title("Grade Distribution")
        plt.xlabel("Grades")
        plt.ylabel("Frequency")
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.savefig(output_image_path)
        plt.close()
        print(f"Histogram saved to {output_image_path}")

    def evaluate_grade_position(self, grades: list, current_grade: float) -> str:
        """
        Determine the grade position relative to the mean grade.

        Args:
            grades (list): List of all grades.
            current_grade (float): The grade of the current CV.

        Returns:
            str: "Above Average", "Average", or "Below Average".
        """
        mean_grade = sum(grades) / len(grades)
        if current_grade > mean_grade:
            return "Above Average"
        elif current_grade == mean_grade:
            return "Average"
        else:
            return "Below Average"


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


def main2(query):
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Set it in the .env file.")

    ai_model = OpenAI(api_key=openai_api_key)
    evaluator = ResumeEvaluator(ai_model, output_folder=os.path.join("Output", "VisualEval"))
    #evaluator = ResumeEvaluator(ai_model, output_folder="Output/VisualEval")
    csv_path = "Output/VisualEval/cv_visual_evaluation.csv"
    file_path = os.path.join("Output","CV" ,"CV_Rise_DataScientist.pdf")

    evaluation_text, grades = evaluator.evaluate_resumeX(file_path, query, csv_path)
    print("Evaluation Text:", evaluation_text)
    print("Grades:", grades)


if __name__ == "__main__":
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
    main2(query)

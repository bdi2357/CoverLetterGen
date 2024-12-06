import PyPDF2
from ai_interaction import OpenAIModel
from typing import Tuple, Dict
from dotenv import load_dotenv
import os
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
from dotenv import load_dotenv
load_dotenv('.env', override=True)
from openai import OpenAI
class ResumeEvaluator:
    def __init__(self, ai_model: OpenAIModel):
        """
        Initialize the ResumeEvaluator with a specific LLM model.

        Args:
            ai_model (OpenAIModel): An instance of the OpenAIModel class.
        """
        self.ai_model = ai_model

    def extract_first_page_as_image(self, pdf_path: str) -> str:
        """
        Extract the first page of the PDF as an image and save it as PNG.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Path to the saved PNG image.
        """
        output_image_path = "cv_first_page.png"  # Save the image locally
        pdf_document = fitz.open(pdf_path)
        page = pdf_document.load_page(0)
        pix = page.get_pixmap()
        image_bytes = BytesIO(pix.tobytes("png"))
        image = Image.open(image_bytes)
        image.save(output_image_path, "PNG")
        pdf_document.close()
        return output_image_path

    def question_image(self, image_path: str, query: str) -> str:
        """
        Analyze an image with a visual query using OpenAI's API.

        Args:
            image_path (str): Path to the image file.
            query (str): Query for analyzing the image.

        Returns:
            str: The analysis response from the model.
        """
        # Encode the image in Base64 if it's a local file
        if not image_path.startswith("http://") and not image_path.startswith("https://"):
            with open(image_path, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            image_data = {"url": f"data:image/png;base64,{encoded_image}"}
        else:
            image_data = {"url": image_path}  # URL provided as is

        # Construct the payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": query},
                        {"type": "image_url", "image_url": image_data},
                    ]
                }
            ],
            "max_tokens": 1000,
        }

        # Make the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        }
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )

        # Debug: Print the raw response for inspection
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        # Check for HTTP errors
        if response.status_code != 200:
            raise ValueError(f"API request failed with status code {response.status_code}: {response.text}")

        try:
            # Parse the JSON response
            json_response = response.json()
        except json.JSONDecodeError:
            raise ValueError("Failed to parse JSON response. Response might be empty or invalid.")

        # Extract and return the content
        if "choices" in json_response:
            return json_response['choices'][0]['message']['content']
        else:
            raise KeyError("The API response does not contain 'choices'.")

    def evaluate_resume(self, pdf_path: str) -> Tuple[str, Dict[str, float]]:
        """
        Evaluate the resume using both text-based and vision-based analysis.

        Args:
            pdf_path (str): Path to the PDF resume.

        Returns:
            Tuple[str, Dict[str, float]]: A detailed evaluation and grades.
        """
        vision_query = """
        Please evaluate the visual aspects of this CV, including:
        - Layout and structure
        - Font consistency and size
        - Visual hierarchy and readability
        - Use of colors, lines, or separators
        - Suitability for professional use

        Provide your response in the following structured format:
        1. Detailed textual evaluation of each criterion.
        2. A JSON object with numerical grades (0–10) for the following criteria:
           - Layout and Structure
           - Font Consistency and Size
           - Visual Hierarchy and Readability
           - Use of Colors, Lines, or Separators
           - Suitability for Professional Use

        Ensure all grades are numeric and included in the JSON object.
        """
        # Step 1: Extract the first page as an image
        first_page_image_path = self.extract_first_page_as_image(pdf_path)

        # Step 2: Perform vision-based analysis
        vision_response = self.question_image(first_page_image_path, vision_query)

        # Step 3: Parse the response
        grades = {}
        detailed_evaluation = vision_response.strip()  # Default to full response if parsing fails

        try:
            # Extract JSON-like structure using regex
            match = re.search(r"\{.*?\}", vision_response, re.DOTALL)
            if match:
                grades_text = match.group(0)
                grades = json.loads(grades_text)
            else:
                raise ValueError("Grades section not found in the response.")

        except json.JSONDecodeError as e:
            grades = {"error": f"Failed to parse grades (JSON error): {e}"}

        return detailed_evaluation, grades

        return description, grades


# Example Usage

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"
}
client = OpenAI()
def question_image(url,query):
    if url.startswith("http://")or url.startswith("https://"):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
            {
            "role": "user",
            "content": [
                {"type": "text", "text": f"{query}"},
                    {
                    "type": "image_url",
                    "image_url": url,
                        },
                    ],
                }
            ],
          max_tokens=1000,
        )
        return response.choices[0].message.content
    else:
        base64_image = encode_image(url)
        payload = {
            "model": "gpt-4o",
            "messages": [
              {
                "role": "user",
                "content": [
                  {
                    "type": "text",
                    "text": f"{query}?"
                  },
                  {
                    "type": "image_url",
                    "image_url": {
                      "url": f"data:image/jpeg;base64,{base64_image}"
                    },
                  }
                ]
              }
            ],
            "max_tokens": 1000
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        temp=response.json()
        #print(temp)
        return temp['choices'][0]['message']['content']


"""
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
"""
if __name__ == "__main__":
    query = "Describe this image to me in detail"
    url = os.path.join("Data","sunflower.jpg")
    desc = question_image(url, query)
    print(desc)
    # Load the OpenAI API key
    os.environ['OPENAI_API_KEY'] =os.getenv('OPENAI_API_KEY')

    # Initialize the AI model
    ai_model = OpenAIModel(api_key=os.getenv('OPENAI_API_KEY'), model_name="gpt-4o")

    # Initialize the evaluator
    evaluator = ResumeEvaluator(ai_model)

    # Path to the resume PDF
    #resume_pdf_path = "cv_Shira.pdf"
    #file_path = os.path.join("Output", "CV", "CV_Rise_DataScientist.pdf")
    #file_path = os.path.join("Data", "CV", "cv_Shira.pdf")
    file_path = os.path.join("Data", "CV","cv-David-Pal.pdf")
    # Evaluate the resume
    evaluation_text, grades = evaluator.evaluate_resume(file_path)

    # Print the results
    print("Detailed Evaluation:")
    print(evaluation_text)
    print("\nGrades:")
    print(grades)
# data_handling.py

from PyPDF2 import PdfReader
import os
from pdfminer.high_level import extract_text

def load_and_extract_text(file_path):
    """
    Load a PDF file and extract its text content using pdfminer.six.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    text = extract_text(file_path)
    return text
""" 
def load_and_extract_text(file_path):
    
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        print("num of pages",len(pdf_reader.pages))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            print(page_text)
            text += page_text #page.extract_text()

    return text
"""

def extract_applicant_name(cv_text):
    """
    Extract the applicant's name from the CV text.
    This function assumes that the name is in the first line of the CV.

    Args:
        cv_text (str): The text of the CV.

    Returns:
        str: The applicant's name.
    """
    lines = cv_text.strip().split('\n')
    if lines:
        name_line = lines[0]
        # Additional processing can be added here to accurately extract the name.
        return name_line.strip()
    else:
        return "Applicant"

# Testing functions
if __name__ == '__main__':
    """
    import unittest
    import os

    class TestDataHandling(unittest.TestCase):
        def test_load_and_extract_text(self):
            # Create a sample PDF file for testing
            sample_pdf_path = os.path.join("..","Data",'CV_GPT_rev.pdf')
            sample_text = 'Hello, this is a test PDF file.'

            # Create the PDF file
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(sample_pdf_path)
            c.drawString(100, 750, sample_text)
            c.save()

            # Test the load_and_extract_text function
            extracted_text = load_and_extract_text(sample_pdf_path)
            self.assertIn(sample_text, extracted_text)
            print(extracted_text)
            # Clean up
            os.remove(sample_pdf_path)

        def test_extract_applicant_name(self):
            # Test with a sample CV text
            cv_text = "John Doe\nExperienced Software Engineer\n..."

            name = extract_applicant_name(cv_text)
            self.assertEqual(name, "John Doe")

            # Test with empty CV text
            cv_text_empty = ""
            name_empty = extract_applicant_name(cv_text_empty)
            self.assertEqual(name_empty, "Applicant")

            # Test with CV text without newline
            cv_text_no_newline = "Jane Smith"
            name_no_newline = extract_applicant_name(cv_text_no_newline)
            self.assertEqual(name_no_newline, "Jane Smith")

    # Run the tests
    unittest.main()
    """
    print(os.path.isdir(os.path.join("Data")))
    sample_pdf_path = os.path.join("Data", 'CV_GPT_rev.pdf')
    print(load_and_extract_text(sample_pdf_path))
    print("Name :", extract_applicant_name(load_and_extract_text(sample_pdf_path)))

# main.py

import os
from data_handling import load_and_extract_text, extract_applicant_name
from ai_interaction import AIModel, CoverLetterGenerator
from utilities import create_pdf
from dotenv import load_dotenv

import random

#Get the OpenAI API key from the .env file
load_dotenv('.env', override=True)
def main(cv_file_path, job_description_text):
    # Load API key securely
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set the 'OPENAI_API_KEY' environment variable.")

    # Initialize AI model and cover letter generator
    ai_model = AIModel(api_key=openai_api_key, model_name='gpt-4o')
    cover_letter_gen = CoverLetterGenerator(ai_model)

    # Load CV text

    cv_text = load_and_extract_text(cv_file_path)
    applicant_name = extract_applicant_name(cv_text)



    # Initialize conversation history
    history = []

    # Generate initial cover letter
    cover_letter = cover_letter_gen.generate_cover_letter(cv_text, job_description_text, history=history)
    print("Initial Cover Letter:")
    print(cover_letter)

    # Add to history
    history.append({"role": "user", "content": cover_letter})
    history.append({"role": "assistant", "content": cover_letter})

    # Loop to improve cover letter based on critique
    max_iterations = 3
    for iteration in range(max_iterations):
        critique, grade = cover_letter_gen.create_critique(cover_letter, cv_text, job_description_text, history=history)
        print(f"Iteration {iteration+1}, Grade: {grade}")

        # Add critique to history
        history.append({"role": "user", "content": critique})
        history.append({"role": "assistant", "content": critique})

        if grade >= 9:
            print("Achieved satisfactory grade.")
            break
        else:
            cover_letter = cover_letter_gen.improve_cover_letter(cv_text, cover_letter, job_description_text, critique, grade, history=history)
            # Add improved cover letter to history
            history.append({"role": "user", "content": cover_letter})
            history.append({"role": "assistant", "content": cover_letter})
    else:
        print("Maximum iterations reached without achieving satisfactory grade.")

    # Output the final cover letter
    print("Final Cover Letter:")
    print(cover_letter)

    # Create a PDF of the final cover letter
    output_pdf_path = "Output/cover_letter.pdf"
    create_pdf(output_pdf_path, "Cover Letter", applicant_name, cover_letter)
    print(f"Cover letter saved to {output_pdf_path}")

if __name__ == "__main__":
    cv_file_path = os.path.join("Data", 'CV_GPT_rev.pdf')
    job_description_text = """ We're seeking an AI Developer to join our team. In this role, you'll leverage artificial intelligence and machine learning techniques to improve the invoice reconciliation process and create a unified data format across various financial systems.

    Responsibilities:
    - Develop and implement AI and machine learning models to automate invoice reconciliation
    - Create intelligent systems to unify diverse invoice data into a standardized format
    - Design and build natural language processing (NLP) solutions to extract key information from unstructured invoice data
    - Implement machine learning algorithms to identify patterns, anomalies, and potential errors in financial data
    - Collaborate with finance and accounting teams to understand business requirements and integrate AI solutions into existing workflows
    - Continuously improve and optimize AI models based on new data and changing business needs

    Requirements:
    - Masters or PhD in Computer Science, Artificial Intelligence, or related field
    - 3+ years of experience developing AI and machine learning solutions, preferably in finance or accounting domains
    - Strong programming skills in Python and experience with ML frameworks (e.g., TensorFlow, PyTorch, scikit-learn)
    - Experience with NLP techniques and text analysis
    - Familiarity with financial systems, ERP software, and accounting principles
    - Knowledge of data privacy and security best practices
    - Excellent problem-solving skills and ability to translate complex business requirements into technical solutions

    No agencies please.
    This individual must be available for 30h/week and during UK working hours.

    """
    main(cv_file_path, job_description_text)

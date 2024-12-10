# main.py

import os
from ai_interaction import OpenAIModel, CoverLetterGenerator
from basic_iterative import BasicIterativeAgent  # Import BasicIterativeAgent
#from actor_critic import ActorCriticAgent  # Import ActorCriticAgent
from data_handling import load_and_extract_text, extract_applicant_name
from utilities import create_pdf
from dotenv import load_dotenv
from parsing_cv_to_dict import CVParserAI
load_dotenv('.env', override=True)
from openai import OpenAI
from doc_from_template import generate_cv
def main(cv_file_path, job_description_text, llm_provider='openai', method='basic'):
    # Load API key securely
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the appropriate environment variable.")

    # Initialize the appropriate AI model based on the llm_provider argument
    if llm_provider == 'openai':
        ai_model = OpenAIModel(api_key=api_key, model_name='gpt-4o')
    else:
        raise ValueError(f"Unsupported LLM providerh: {llm_provider}")

    # Initialize CoverLetterGenerator
    parser = CVParserAI(OpenAI())
    cover_letter_gen = CoverLetterGenerator(ai_model)

    # Initialize the method-agnostic agent
    if method == 'basic':
        agent = BasicIterativeAgent(cover_letter_gen)
    elif method == 'actor_critic':
        agent = ActorCriticAgent(ai_model)
    elif method == 'actor_critic_adaptive':
        agent = ActorCriticAdaptiveAgent(ai_model)
    else:
        raise ValueError(f"Unsupported method: {method}")

    # Load CV text
    cv_text = load_and_extract_text(cv_file_path)
    applicant_name = extract_applicant_name(cv_text)

    # Generate initial cover letter
    cover_letter = agent.generate_cover_letter(cv_text, job_description_text)
    print("Initial Cover Letter:")
    print(cover_letter)

    # Improve the cover letter
    improved_cover_letter,last_critique = agent.improve_cover_letter(cv_text, cover_letter, job_description_text)
    print("Final Cover Letter:")
    print(improved_cover_letter)
    print("Critique of the Final Cover Letter")
    print(last_critique)


    sections_cover_letter = parser.parse_cv_and_cover_letter_to_dict(cv_text, cover_letter)
    print(sections_cover_letter)
    generate_cv()
    # Create a PDF of the final cover letter
    output_pdf_path = "Output/cover_letter.pdf"
    create_pdf(output_pdf_path, applicant_name, improved_cover_letter)
    print(f"Cover letter saved to {output_pdf_path}")


if __name__ == "__main__":
    cv_file_path = os.path.join("Data", 'CV' ,'CV_GPT_N5.pdf')
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
    # Run with basic iterative method
    main(cv_file_path, job_description_text, method='basic')
    """
    # Run with actor-critic method
    main(cv_file_path, job_description_text, method='actor_critic')

    # Run with actor-critic adaptive method
    main(cv_file_path, job_description_text, method='actor_critic_adaptive')
    """

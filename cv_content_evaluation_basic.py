import os,re
# Assume the required imports from the respective modules (like OpenAIModel, GeminiModel, etc.)
from cv_info_extractor import load_and_extract_text
from ai_interaction import OpenAIModel, GeminiModel

def extract_information_from_cv(cv_text):
    """
    Extracts applicant's name, email, phone, address, GitHub, and LinkedIn from the provided CV text.

    Args:
        cv_text (str): The full text of the CV.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    prompt = f"""
    Extract the following information from the given CV text:
    - Full name of the applicant
    - Email address
    - Phone number
    - Physical address
    - GitHub profile (if present)
    - LinkedIn profile (if present)

    If any of the information is missing, simply omit it from the result. Provide the output in a structured format.

    Here is the CV text:
    \"{cv_text}\"
    """

    response = get_llm_response(prompt)

    if response:
        # Parse the response into a dictionary (assume that the GPT response is structured)
        extracted_info = parse_extracted_info(response)
        return extracted_info
    else:
        return {}



class ContentEvaluator:
    def __init__(self, ai_model):
        self.ai_model = ai_model

    def evaluate_cv(self, cv_text, job_description, history=None):
        prompt = f"""
        Please analyze the relevance of the candidate's qualifications, skills, and experience based on the provided job description.

        Job Description:
        {job_description}

        CV:
        {cv_text}

        Provide feedback on the candidate’s overall fit for the job, and suggest areas of improvement.
        Provide an overall grade on a scale of 1-10 at the end in the format: **#Overall Grade : NUMBER#**
        """
        return self.ai_model.get_response(prompt, history=history)

    def create_critique(self, cv_evaluation, cv_text, job_description, history=None):
        """
        Generate a critique of the CV evaluation.
        """
        prompt = f"""
        Based on the following CV evaluation, provide a critique of the assessment and suggest improvements.

        CV Evaluation:
        {cv_evaluation}

        CV:
        {cv_text}

        Job Description:
        {job_description}

        Provide  specific suggestions for improving the evaluation and an overall grade on a scale of 1-10 at the end in the format: **#Overall Grade : NUMBER#** 
        """
        response = self.ai_model.get_response(prompt, history=history)
        match = re.search(r"#Overall Grade\s*:\s*(\d+(\.\d+)?)\s*/?\d*\s*#", response)
        if match:
            grade = float(match.group(1))
        else:
            raise ValueError("Failed to extract overall grade from the critique.")
        return response, grade


def main(cv_file_path, job_description_text, llm_provider='openai'):
    # Load API key securely
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the appropriate environment variable.")

    # Initialize the appropriate AI model based on the llm_provider argument
    if llm_provider == 'openai':
        ai_model = OpenAIModel(api_key=api_key, model_name='gpt-4')
    elif llm_provider == 'gemini':
        ai_model = GeminiModel()
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    # Initialize the ContentEvaluator
    content_evaluator = ContentEvaluator(ai_model)

    # Load CV text
    cv_text = load_and_extract_text(cv_file_path)

    # Initialize conversation history
    history = []

    # Generate initial evaluation
    cv_evaluation = content_evaluator.evaluate_cv(cv_text, job_description_text, history=history)
    print("Initial CV Evaluation:")
    print(cv_evaluation)

    # Add to history
    history.append({"role": "user", "content": cv_evaluation})
    history.append({"role": "assistant", "content": cv_evaluation})

    # Loop to improve CV evaluation based on critique
    max_iterations = 3
    for iteration in range(max_iterations):

        critique, grade = content_evaluator.create_critique(cv_evaluation, cv_text, job_description_text, history=history)
        print(f"Iteration {iteration+1}, Grade: {grade}")

        # Add critique to history
        history.append({"role": "user", "content": critique})
        history.append({"role": "assistant", "content": critique})

        if grade >= 9:
            print("Achieved satisfactory grade.")
            break
        else:
            cv_evaluation = content_evaluator.evaluate_cv(cv_text, job_description_text, history=history)
            # Add improved evaluation to history
            history.append({"role": "user", "content": cv_evaluation})
            history.append({"role": "assistant", "content": cv_evaluation})
    else:
        print("Maximum iterations reached without achieving satisfactory grade.")

    # Output the final CV evaluation
    print("Final CV Evaluation:")
    print(cv_evaluation)
    match = re.search(r"#Overall Grade\s*:\s*(\d+(\.\d+)?)\s*/?\d*\s*#", cv_evaluation)
    if match:
        grade = float(match.group(1))
    else:
        raise ValueError("Failed to extract overall grade from the critique.")
    print("Final Grade is: %0.2f"%grade)


if __name__ == "__main__":
    cv_file_path = os.path.join("Data", 'CV_GPT_rev.pdf')
    job_description_text = """
    We're seeking an AI Developer to join our team. In this role, you'll leverage artificial intelligence and machine learning techniques to improve the invoice reconciliation process and create a unified data format across various financial systems.

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
    """

    # You can specify the LLM provider to test different models
    main(cv_file_path, job_description_text, llm_provider="openai")

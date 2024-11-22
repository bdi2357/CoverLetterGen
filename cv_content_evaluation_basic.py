import os,re
# Assume the required imports from the respective modules (like OpenAIModel, GeminiModel, etc.)
from cv_info_extractor import load_and_extract_text
from ai_interaction import OpenAIModel, GeminiModel
from ai_interaction import OpenAIModel, CVGenerator
from basic_iterative import BasicIterativeAgent
from cv_info_extractor import extract_information_from_cv
from docx_generate import generate_cv_document, save_cv_sections_to_file, extract_cv_sections,load_cv_sections_from_file
import  time
from parsing_cv_to_dict import CVParserAI
from dotenv import load_dotenv
from openai import OpenAI
from ExtractCompanyNameJob import extract_company_name_and_job_name
from doc_from_template import sections2cv
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
        #ai_model = OpenAIModel(api_key=api_key, model_name='gpt-4o-mini')
        ai_model = OpenAIModel(api_key=api_key, model_name='gpt-4o')

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


def cv_content_generation(cv_file_path, job_description_text, llm_provider='openai'):
    # Load API key securely
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the appropriate environment variable.")

    # Initialize the appropriate AI model based on the llm_provider argument
    if llm_provider == 'openai':
        ai_model = OpenAIModel(api_key=api_key, model_name='gpt-4o')
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

    # Initialize the CVGenerator with the chosen AI model
    cv_gen = CVGenerator(ai_model)

    # Extract text from the CV file
    cv_text = load_and_extract_text(cv_file_path)

    # Use extract_information_from_cv to get structured data from CV text
    cv_data = extract_information_from_cv(cv_text)
    personal_info = cv_data.get('Full name', '') + ", " + cv_data.get('Email', '')
    job_history = cv_data.get('Professional Summary', 'No job history found')
    skills = cv_data.get('Key skills', '')

    # Initialize BasicIterativeAgent with the CVGenerator
    agent = BasicIterativeAgent(cv_gen, max_iterations=4, improvement_threshold=-1.5)

    # Generate initial CV and perform iterative improvements
    generated_cv, final_critique = agent.improve_cv(cv_text,personal_info, job_history, skills, job_description_text)

    # Output the final improved CV and critique
    print("Final Improved CV:")
    print(generated_cv)
    print("\nFinal Critique:")
    print(final_critique)
    return generated_cv, final_critique

def wrapping_cv_generation(cv_file_path,job_description_text, output_dir,openai_api_key, template_path):
    company_name_and_job_name = extract_company_name_and_job_name(job_description_text)
    sections_file_path = os.path.join("Output", "Sections",
                                      company_name_and_job_name.replace(".", "_") + "_sections.txt")
    critique_file_path = os.path.join("Output", "CritiqueFinal",
                                      company_name_and_job_name.replace(".", "_") + "_crtitque.txt")
    cv_content_final_file_path = os.path.join("Output", "CV_content",
                                              company_name_and_job_name.replace(".", "_") + "_cv_content.txt")
    dest_cv_path = os.path.join("Output", "CV","CV_"+company_name_and_job_name.replace(".", "_") )
    finalized_cv_content, citique_final = cv_content_generation(cv_file_path, job_description_text,
                                                                llm_provider="openai")
    client = OpenAI(api_key=openai_api_key)

    # Assume `openai` is the OpenAI client object initialized with your API key
    parser = CVParserAI(client)
    sections = parser.parse_cv_sections(finalized_cv_content)
    save_cv_sections_to_file(sections, sections_file_path)
    # generate_cv_document(file_name, finalized_cv_content)

    print(f"Generated CV saved to {sections}")
    with open(critique_file_path, "w", encoding="utf-8") as f:
        f.write(f"{citique_final}:\n")
    with open(cv_content_final_file_path, "w", encoding="utf-8") as f:
        f.write(f"{finalized_cv_content}:\n")

    print(load_cv_sections_from_file(sections_file_path))
    sections2cv(template_path, sections_file_path, dest_cv_path)
    print("total time %0.2f" % (time.time() - start))



if __name__ == "__main__":
    start = time.time()
    #cv_file_path = os.path.join("Data", 'CV_GPT_rev.pdf')
    cv_file_path = os.path.join("Data","CV", 'CV_GPT_N3.pdf')

    job_description_text_file_path = os.path.join("Data","JobDescriptions","Moloco.txt")

    load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    output_dir = "Output"
    template_path = os.path.join("Templates", "Final_Revised_Template_V2.docx")
    job_description_text = open(job_description_text_file_path,"r").read()
    #print(job_description_text)
    wrapping_cv_generation(cv_file_path, job_description_text, output_dir, openai_api_key,template_path)
    # Set up OpenAI client
    """ 
    client = OpenAI(api_key=openai_api_key)

    # Assume `openai` is the OpenAI client object initialized with your API key
    parser = CVParserAI(client)
    sections = parser.parse_cv_sections(finalized_cv_content)
    print("*"*60)
    print(sections)
    save_cv_sections_to_file(sections, sections_file_path)
    #generate_cv_document(file_name, finalized_cv_content)

    print(f"Generated CV saved to {sections}")
    with open(critique_file_path, "w", encoding="utf-8") as f:
        f.write(f"{citique_final}:\n")
    with open(cv_content_final_file_path, "w", encoding="utf-8") as f:
        f.write(f"{finalized_cv_content}:\n")

    print(load_cv_sections_from_file(sections_file_path))
    print("total time %0.2f"%(time.time() - start) )
    """


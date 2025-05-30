import os,re
# Assume the required imports from the respective modules (like OpenAIModel, GeminiModel, etc.)
from cv_info_extractor import load_and_extract_text
from ai_interaction import OpenAIModel, GeminiModel
from ai_interaction import OpenAIModel, CVGenerator
from basic_iterative import BasicIterativeAgent
from modular_iterative import ModularIterativeAgent
from cv_info_extractor import extract_information_from_cv
from docx_generate import generate_cv_document, save_cv_sections_to_file, extract_cv_sections,load_cv_sections_from_file
import time
import logging

from parsing_cv_to_dict import CVParserAI
from dotenv import load_dotenv
from openai import OpenAI
from ExtractCompanyNameJob import extract_company_name_and_job_name
from doc_from_template import sections2cv
from parse_critique_to_dict import parse_cv_critique_to_dict
from doc_from_template import generate_cv

def critique_original_cv(cv_content, job_description_text, cover_letter_gen_a, critique_file_path, api_key ):
    critique, grade, grades_dict = cover_letter_gen_a.create_critique(
                cv_content, cv_content, job_description_text, history=""
            )
    cv_data = extract_information_from_cv(cv_content, api_key)

    cv_data = {key.strip('"'): value.strip('"').replace(',', '').strip() if isinstance(value, str) else value for
               key, value in cv_data.items()}
    company_name_and_job_name = extract_company_name_and_job_name(job_description_text, openai_api_key)
    company_name_and_job_name = company_name_and_job_name.replace("/", "_")
    print(company_name_and_job_name)
    company_name, job_name = company_name_and_job_name.split("|")
    company_name_and_job_name = company_name_and_job_name.replace("|", "_")

    # generate_cv_document(file_name, finalized_cv_content)
    sections_critique = parse_cv_critique_to_dict(critique, "cv_critique" + company_name_and_job_name,
                                                  cv_data["Full name"])
    sections_critique["job_name"] = job_name
    sections_critique["company_name"] = company_name
    sections_critique['name'] = sections_critique['name'].replace("\"", "")


    print(sections_critique)
    sections_critique["FinalGrade"] = [float(section["Grade"]) for section in sections_critique['sections'] if
                                       section['Title'].find('Overall Impression') > -1][0]
    for section in sections_critique['sections']:
        section['Content'] = section['Content'].replace("Ph.D", "PhD").split(".")
        if len(section["Content"][-1]) < 3:
            section["Content"] = section["Content"][:-1]
    template_cv_critique_path = os.path.join("Templates", "Critique_CV_Template_v2.docx")


    final_verdict_prompt = create_final_verdict_prompt_v2(sections_critique)
    client = OpenAI(api_key=openai_api_key)
    final_verdict = get_response(client, final_verdict_prompt)
    sections_critique["final_verdict"] = final_verdict
    #output_criqique_path = os.path.join("Output", "CV", "CVCritique_" + company_name_and_job_name)
    # sections_critique["FinalGrade "] = sections_critique.pop()
    generate_cv(critique_file_path, sections_critique, template_cv_critique_path)

    return
"""
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
"""
import importlib


def get_response(client, prompt, history=None, temperature=0.01,model_name="gpt-4o-mini"):
    """
    Get the response from the OpenAI model for the given prompt.

    Args:
        client : client
        prompt (str): The prompt to send to the model.
        history (list): A list of previous messages (dictionaries with 'role' and 'content').
        temperature (float): The temperature for response randomness.

    Returns:
        str: The response from the model.
    """
    messages = [
        {"role": "system", "content": "You are a helpful but terse AI assistant who gets straight to the point."}
    ]
    if history:
        messages.extend(history)

    messages.append({"role": "user", "content": prompt})

    try:
        completion = client.chat.completions.create(
            model= model_name,
            messages=messages,
            temperature=temperature
        )
        response = completion.choices[0].message.content.strip()
        return response
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None
def cv_content_generation(cv_file_path, job_description_text, llm_provider='openai', agent_type='BasicIterativeAgent', agent_module='basic_iterative'):
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
    cv_data = extract_information_from_cv(cv_text,api_key)

    cv_data = {key.strip('"'): value.strip('"').replace(',', '').strip() if isinstance(value, str) else value for key, value in cv_data.items()}

    #personal_info = cv_data.get('Full name', '') + ", " + cv_data.get('Email', '')
    #job_history = cv_data.get('Professional Summary', 'No job history found')
    #skills = cv_data.get('Key skills', '')
    print(cv_data)
    print(cv_data['Full name'])
    print("#$"*44)
    # Dynamically load the agent class from the specified module
    try:
        agent_module_obj = importlib.import_module(agent_module)
        agent_class = getattr(agent_module_obj, agent_type)
    except (ModuleNotFoundError, AttributeError) as e:
        raise ImportError(f"Could not load agent '{agent_type}' from module '{agent_module}': {e}")

    # Initialize the agent dynamically
    agent = agent_class(cv_gen, max_iterations=4, improvement_threshold=-1.5)

    # Generate initial CV and perform iterative improvements
    #generated_cv_p = cv_gen.generate_cv(cv_text, job_description_text, cv_text, history=None)
    generated_cv, final_critique = agent.improve_cv(cv_text, job_description_text)

    # Output the final improved CV and critique
    print("Final Improved CV:")
    print(generated_cv)
    print("\nFinal Critique:")
    print(final_critique)
    return generated_cv, final_critique, cv_data

def create_final_verdict_prompt(sections_critique):
    """
    Generates a prompt to create a final verdict for a CV critique based on input sections.

    Parameters:
        sections_critique (dict): A dictionary containing critique sections, including grades and content.

    Returns:
        str: A formatted prompt for generating the final verdict.
    """
    prompt = f"""
You are a professional CV reviewer. Based on the provided critique sections, create a **Final Verdict** for the candidate's CV. The final verdict should include:
1. **Grade**: Calculate the overall grade as the average of the grades from all sections.
2. **Strengths**: Summarize the key strengths across all sections, focusing on the most impactful aspects.
3. **Areas for Improvement**: Highlight the main weaknesses or areas for refinement.
4. **Next Steps**: Provide actionable suggestions to help the candidate improve their CV and make it more aligned with the job role.

Here is the input data:

{sections_critique}

Format the output in the following structure:
Final Verdict

Grade: [Overall Grade]

[Summary of Strengths]

[Summary of Weaknesses]

[Actionable Suggestions or Next Steps]

vbnet
Copy code
"""
    return prompt
def create_final_verdict_prompt_v2(sections_critique):
    """
    Generates a prompt to create a structured final verdict for a CV critique based on input sections.

    Parameters:
        sections_critique (dict): A dictionary containing critique sections, including grades and content.

    Returns:
        str: A formatted prompt for generating the structured final verdict.
    """
    prompt = f"""
You are a professional CV reviewer. Based on the provided critique sections, create a **Final Verdict** for the candidate's CV.
Format the result as a dictionary with the following structure:
- "Grade": A number representing the overall grade (average of all section grades).
- "Strengths": A list of strings summarizing the key strengths across all sections.
- "Areas for Improvement": A list of strings summarizing the main weaknesses or areas for refinement.
- "Next Steps": A list of actionable suggestions to help the candidate improve their CV.

Here is the input data:

{sections_critique}

Ensure the dictionary format is valid and follows this example structure:
{{ 
    "Grade": 8.8, 
    "Strengths": [ 
        "Strong alignment with the VP Data Science role, particularly in ML/DL and health tech.", 
        "Well-organized CV with clear sections and logical flow." 
    ], 
    "Areas for Improvement": [ 
        "Need for more emphasis on specific leadership roles and team management." 
    ], 
    "Next Steps": [ 
        "Explicitly mention leadership roles and team management experience in the work experience section." 
    ] 
}}
"""
    return prompt
def wrapping_cv_generation(cv_file_path,job_description_text, output_dir,openai_api_key, template_path,agent_type='BasicIterativeAgent', agent_module='basic_iterative'):
    company_name_and_job_name = extract_company_name_and_job_name(job_description_text, openai_api_key)
    company_name_and_job_name = company_name_and_job_name.replace("/","_")
    sections_file_path = os.path.join("Output", "Sections",
                                      company_name_and_job_name.replace(".", "_").replace("|","_") + agent_type +"_sections.txt")
    critique_file_path = os.path.join("Output", "CritiqueFinal",
                                      company_name_and_job_name.replace(".", "_").replace("|","_") + agent_type + "_crtitque.txt")
    cv_content_final_file_path = os.path.join("Output", "CV_content",
                                              company_name_and_job_name.replace(".", "_").replace("|","_") + agent_type +"_cv_content.txt")
    #extract_information_from_cv
    cv_text = load_and_extract_text(cv_file_path)
    cv_data2 = extract_information_from_cv(cv_text, openai_api_key)
    ai_model = OpenAIModel(api_key=openai_api_key, model_name='gpt-4o')


    # Initialize the CVGenerator with the chosen AI model
    cv_gen = CVGenerator(ai_model)
    critique_original_cv_file_path = os.path.join("Output", "CV", "OriginalCVCritique_" + company_name_and_job_name.replace("|","_"))
    critique_original_cv(cv_text, job_description_text, cv_gen, critique_original_cv_file_path, openai_api_key)

    cv_data2 = {key.strip('"'): value.strip('"').replace(',', '').strip() if isinstance(value, str) else value for
               key, value in cv_data2.items()}
    #cv_data['Full name']
    dest_cv_path = os.path.join("Output", "CV","CV_"+company_name_and_job_name.replace(".", "_").replace("|","_")+"_"+agent_type +cv_data2['Full name'].replace(" ","_").replace("-","_").replace("\"",""))
    finalized_cv_content, critique_final, cv_data = cv_content_generation(cv_file_path, job_description_text,
                                                                llm_provider="openai",
                                                                agent_type=agent_type, agent_module=agent_module)
    print(company_name_and_job_name)
    company_name,job_name = company_name_and_job_name.split("|")
    company_name_and_job_name = company_name_and_job_name.replace("|","_")
    client = OpenAI(api_key=openai_api_key)

    # Assume `openai` is the OpenAI client object initialized with your API key
    parser = CVParserAI(client)
    sections = parser.parse_cv_sections(finalized_cv_content)
    save_cv_sections_to_file(sections, sections_file_path)
    # generate_cv_document(file_name, finalized_cv_content)

    sections_critique = parse_cv_critique_to_dict(critique_final , "cv_critique" + company_name_and_job_name, cv_data["Full name"])
    sections_critique["job_name"] = job_name
    sections_critique["company_name"] = company_name
    sections_critique['name'] = sections_critique['name'].replace("\"","")
    print(f"Generated CV saved to {sections}")
    with open(critique_file_path, "w", encoding="utf-8") as f:
        f.write(f"{critique_final}:\n")
    with open(cv_content_final_file_path, "w", encoding="utf-8") as f:
        f.write(f"{finalized_cv_content}:\n")
    print(sections_critique)
    sections_critique["FinalGrade"] = [float(section["Grade"]) for section in sections_critique['sections'] if section['Title'].find('Overall Impression')>-1][0]
    for section in sections_critique['sections']:
        section['Content'] = section['Content'].replace("Ph.D","PhD").split(".")
        if len(section["Content"][-1]) < 3:
            section["Content"] = section["Content"][:-1]
    template_cv_critique_path = os.path.join("Templates", "Critique_CV_Template_v2.docx")
    print(load_cv_sections_from_file(sections_file_path))
    sections2cv(template_path, sections_file_path, dest_cv_path)

    final_verdict_prompt = create_final_verdict_prompt_v2(sections_critique)
    final_verdict = get_response(client, final_verdict_prompt)
    sections_critique["final_verdict"] = final_verdict
    output_criqique_path = os.path.join("Output", "CV", "CVCritique_" + company_name_and_job_name)
    #sections_critique["FinalGrade "] = sections_critique.pop()
    generate_cv(output_criqique_path, sections_critique, template_cv_critique_path)
    print(sections_critique)
    print("total time %0.2f" % (time.time() - start))



if __name__ == "__main__":
    start = time.time()
    #cv_file_path = os.path.join("Data", 'CV_GPT_rev.pdf')
    cv_file_path = os.path.join("Data","CV", 'CV_GPT_N6.pdf')
    #NetaShoham_CV_V2
    #cv_file_path = os.path.join("Data", "CV", 'NetaShoham_CV_V1.pdf')
    #cv_file_path = os.path.join("Data","CV","Neta Shoham - CV -2025.pdf")
    #cv_file_path = os.path.join("Data","CV","CV_2025_neta_shoham.pdf")
    #job_description_text_file_path = os.path.join("Data","JobDescriptions","Cellebrite.txt")
    #job_description_text_file_path = os.path.join("Data", "JobDescriptions", "PropHouse.txt")
    #job_description_text_file_path = os.path.join("Data", "JobDescriptions", "MobilEnginieye.txt")
    job_description_text_file_path = os.path.join("Data", "JobDescriptions", "Factify.txt")
    load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')
    output_dir = "Output"
    template_path = os.path.join("Templates", "Final_Revised_Template_v2.docx")
    job_description_text = open(job_description_text_file_path,"r",encoding="utf-8").read()
    #print(job_description_text)
    #wrapping_cv_generation(cv_file_path, job_description_text, output_dir, openai_api_key,template_path, "ModularIterativeAgent", "modular_iterative")
    wrapping_cv_generation(cv_file_path, job_description_text, output_dir, openai_api_key, template_path,"BasicIterativeAgent", "basic_iterative")
    # Set up OpenAI client
    print("Total time : %0.2f" %(time.time() -start))
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
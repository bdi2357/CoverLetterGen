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

if __name__ == "__main__":
    start = time.time()
    #cv_file_path = os.path.join("Data", 'CV_GPT_rev.pdf')
    cv_file_path = os.path.join("Data", 'CV_GPT_N.pdf')
    job_description_text = """About the job
At Logz.io, we are at the forefront of automating observability, pushing the boundaries of cloud observability with AI and cutting-edge technologies. We are integrating Generative AI into our platform to further our journey toward autonomous observability.





About the Position

At Logz.io, we are focused on advancing key observability metrics, with a particular emphasis on MTTR (mean time to recovery). We are seeking a GenAI Software Tech Leader who will design and build scalable AI solutions. We are looking for someone who enjoys exploring uncharted territories, has the ability to read and interpret scientific papers and other relevant materials, and is unafraid to experiment in both research and development.


Responsibilities

Lead the design and implementation of generative AI solutions for observability use cases such as log summarization, root cause analysis, and alert generation.
Continuously research emerging AI technologies and techniques to enhance our platform.
Architect scalable infrastructure to support AI-driven features across the Logz.io platform.
Collaborate with cross-functional teams to define and execute the AI strategy.
Promote AI best practices, including model performance evaluation, data privacy, and responsible AI deployment5+ years in software engineering, focusing on AI/ML or data-intensive systems.


Requirements

5+ years in software engineering, focusing on AI/ML or data-intensive systems.
Experience with LLMs, orchestration frameworks, RAG, and AI agents.
Proficiency in Python and strong understanding of prompting best practices for LLMs.
Creative problem-solving, a "can-do" attitude, and a hacker mindset.
Ability to communicate complex AI concepts to both technical and non-technical stakeholders.


Advantages

Experience with LangChain, LlamaIndex, OpenAI, AWS Lambdas, and AWS Bedrock.
Familiarity with observability products and telemetry data (logs, traces, metrics).
Knowledge of MLOps, large-scale data pipelines, NLP, and conversational AI.
"""


    job_description_text = """About the job
About us

Bounce is a fintech startup revolutionizing debt management for consumers and creditors with our best-in-class product. By leveraging the power of AI and automation, we create user-friendly experiences that drive positive outcomes for all parties involved.

With a team based in Tel Aviv and New York, we have been growing rapidly, supporting hundreds of thousands of consumers on their journey to financial resilience and building partnerships with top creditors and fintech companies.



About the role:

As a lead data scientist you will be the person in charge of creating business impact in the company using ML tools. This will include both hands on DS projects, and guiding a team of data scientists in their projects.

This position could include managerial capacities for DS professionals, depending on the skills, experience and preferences of candidates (which may also vary the title).



As a Lead Data Scientist you will:

Develop, backtest, and implement mathematical/statistical models to make complex credit (and other) decisions.
Build tools to query, clean, analyze raw data through databases, and work closely with the R&D team to design a standardized framework to streamline the research process.
Working cross-functionally with engineering, data, and business teams to ensure the maximum impact of research results.
Own the entire research lifecycle - including problem formulation, feature engineering, research, implementation, model explainability, and continuous monitoring.
Lead a team of data scientists to maximize their impact in the organization.
Have a seat at the table to impact decisions around everything data related.


What you’ll need:

M.Sc in a quantitative field (Ph.D. is a big advantage) - Math, CS, Physics, Bio-Informatics, Statistics
Strong background in Python
Experience with mathematical modeling of real-world problems (either in Academia or in Industry)
Experience with financial data or models - A big plus
Experience with pricing, credit or risk modeling - A very big plus
Hands-on experience in applying machine learning models to real-world problems
Excellent communication skills with the ability to distill complex problems into clear and concise insights
Ability to work autonomously and lead other data scientists"""

    job_description_text = """About the job
Start.io is a mobile marketing and audience platform. Start.io empowers the mobile app ecosystem and simplifies mobile marketing, audience building, and mobile monetization. Start.io 's direct integration with over 500,000 monthly active mobile apps provides access to unprecedented levels of global first-party data, which can be leveraged to understand and predict behaviors, identify new opportunities, and fuel growth.

If you’re a talented Data Scientist looking to be part of a fast-growing innovative R&D team, shape the future of decision-making in business, work on cutting-edge technologies and vast amounts of global real-time data, affect billions of mobile users, and become an industry leader - then let’s talk! Start.io is a mobile data platform that enables organizations to uncover insights and make data-driven decisions that enhance strategies and drive growth. We are seeking a Data Scientist to join our Data Science & Engineering team.

Responsibilities:

Analyze large and complex data to discover hidden patterns and opportunities.
Develop and own end-to-end highly scalable data pipelines.
Develop state-of-the-art machine learning models, and algorithms and build solutions in monetization fields.
Provisioning data models for real-time (online) processing
Shape new data products, and constantly improve the existing products.
Collaborate with multiple teams including Product, BI, Analysts, DevOps, R&D and Marketing to lead and accomplish overall solutions.
Oversee a complete release to production, including analyzing requirements, testing, monitoring and measuring results, multitasking, and quickly responding to critical issues.


Requirements:

Must:

B.Sc./M.A/M.Sc. degree in Computer Science, Engineering, Math, Statistics or other equivalent fields.
6-7 years as a Data Scientist - a strong background in ML concepts and models.
Hands-on experience with Python, especially with data science ML libraries (regression & classification algorithms e.g. XGB or LGBM, recommendation system algorithms, etc.)
Understanding of databases and SQL for data retrieval.
Monitoring and alerting tools (e.g. Grafana, Kibana)
Advantage:

Experience with relational (e.g. Vertica, VoltDB) and non-relational (e.g. MongoDB) databases.
Experience with PMML"""
    job_description_text = """About the job
    Bigabid focuses on solving the key challenge of growth for mobile apps by building Machine Learning and Big Data-driven technology that can both accurately predict what apps a user will like and connect them in a compelling way. Our technology operates at a scale well beyond some of the largest internet companies, processing over 50 TB of raw data per day, handling over 4 million requests per second, and interacting with over a billion unique users a week.

    Our innovative platform is leading-edge with a strong product-market fit. As a result, we're seeing remarkable growth and close to zero customer churn. To support our hyper-growth and continue propelling the growth of some of the biggest names in the mobile industry, we offer a wide range of opportunities for different skill levels and experiences.

    We are looking for a senior ML researcher who is passionate about exploring complex data sets, drawing meaningful insights, and building high-quality real-time data products that complement our robust arsenal of industry-leading technologies.

    As a senior ML researcher at Bigabid, you will be creating high-impact Machine Learning projects. In close coordination with stakeholders, you will play a major role in driving the data science roadmap and execution by providing the best solution to a game changer business problem.

    Deliver end-to-end ML products - including research, model development, prototyping, offline validation, implement in production, and online testing
    Be a key player in the DS group - providing insights, best practices, novel techniques and research, and technical know-how to other data scientists
    Develop ML solutions using advanced DL techniques to a diverse set of problems.
    Analyze huge amounts of complex data to identify meaningful patterns and build useful features for machine learning models
    Apply the scientific method to design, create, tune, and interpret machine learning models
    Perform data manipulation, validation, and cross-domain research
    Come up with new and creative research ideas and insights
    Collaborate with our product and engineering teams to solve problems and identify trends and opportunities.

    Requirements:

    5+ years experience as a Data Scientist
    2+ years experience working with Deep Learning.
    Experience working with recommender systems - an advantage
    Hands-on experience building and deploying deep learning models to production
    High level scripting and programming skills in Python
    Superior verbal, visual, and written communication skills to educate and work with cross functional teams on controlled experiments.
    Team player, responsible, delivery-oriented
    Troubleshooter, problem-solver who knows how to navigate trade-offs
    Work experience as a data analyst - an advantage
    At least a Master's degree in Computer Science, Math, Physics, Engineering, Statistics or other technical field.
    Experience in ML over user personalization, ad-tech, or highly imbalanced data- an advantage

    Excerpt:

    As a senior ML researcher at Bigabid, you will be creating high-impact Machine Learning projects. In close coordination with stakeholders, you will play a major role in driving the data science roadmap and execution by providing the best solution to a game changer business problem"""
    # You can specify the LLM provider to test different models
    company_name_and_job_name = extract_company_name_and_job_name(job_description_text)
    sections_file_path = os.path.join("Output", "Sections", company_name_and_job_name.replace(".","_")+"_sections.txt")
    critique_file_path = os.path.join("Output", "CritiqueFinal", company_name_and_job_name.replace(".","_")+"_crtitque.txt")
    cv_content_final_file_path = os.path.join("Output", "Sections",company_name_and_job_name.replace(".", "_") + "_cv_content.txt")
    finalized_cv_content , citique_final = cv_content_generation(cv_file_path, job_description_text, llm_provider="openai")
    load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Set up OpenAI client
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


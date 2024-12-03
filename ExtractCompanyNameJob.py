# import gradio as gr
import os

from openai import OpenAI
from dotenv import load_dotenv

import random

#Get the OpenAI API key from the .env file
load_dotenv('.env', override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set up the OpenAI client
client = OpenAI(api_key=openai_api_key)


def print_llm_response(prompt):
    """This function takes as input a prompt, which must be a string enclosed in quotation marks,
    and passes it to OpenAI's GPT3.5 model. The function then prints the response of the model.
    """
    llm_response = get_llm_response(prompt)
    print(llm_response)


def get_llm_response(prompt):
    """This function takes as input a prompt, which must be a string enclosed in quotation marks,
    and passes it to OpenAI's GPT3.5 model. The function then saves the response of the model as
    a string.
    """
    try:
        if not isinstance(prompt, str):
            raise ValueError("Input must be a string enclosed in quotes.")
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful but terse AI assistant who gets straight to the point.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0,
        )
        response = completion.choices[0].message.content
        return response
    except TypeError as e:
        print("Error:", str(e))


def get_chat_completion(prompt, history):
    history_string = "\n\n".join(["\n".join(turn) for turn in history])
    prompt_with_history = f"{history_string}\n\n{prompt}"
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful but terse AI assistant who gets straight to the point.",
            },
            {"role": "user", "content": prompt_with_history},
        ],
        temperature=0.0,
    )
    response = completion.choices[0].message.content
    return response

def extract_company_name_and_job_name(job_description_text):
    return get_llm_response(f"""Given the following job description, extract and return the company name and job title in the format CompanyName_JobName that is each there will be no spaces between the Words in the words in the
    CompanyName and the JobName, In the JobName each word will be the first Letter in upper case and the rest in lower case for example data scientist  will be written as DataScientist.
    if the company name is ABC and the job is data scientist the result should return ABC_DataScientist

{job_description_text}

Output the result in the specified format:""")


if __name__ == "__main__" :
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
    print_llm_response(f"""Given the following job description, extract and return the company name and job title in the format CompanyName_JobName that is each there will be no spaces between the Words in the words in the
    CompanyName and the JobName, In the JobName each word will be the first Letter in upper case and the rest in lower case for example data scientist  will be written as DataScientist.
    if the company name is ABC and the job is data scientist the result should return ABC_DataScientist

{job_description_text}

Output the result in the specified format:""")
    job_description_text = open("Data\JobDescriptions\Rise.txt","r").read()
    #job_description_text = open("Data\JobDescriptions\Darrow.txt", "r").read()
    print(extract_company_name_and_job_name(job_description_text))
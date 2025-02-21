# ai_interaction.py

import openai
import re

from abc import ABC, abstractmethod
import re
from abc import ABC, abstractmethod
import logging
import requests

# Base class for LLM interaction
import logging
from abc import ABC, abstractmethod
import google.generativeai as genai
from dotenv import load_dotenv
import os


# Base class for LLM interaction
class LLMModel(ABC):
    """
    Abstract class for interacting with different LLM providers.
    """

    @abstractmethod
    def get_response(self, prompt, history=None, temperature=0.7):
        pass


# Gemini implementation of LLMModel using google.generativeai
class GeminiModel(LLMModel):
    """
    Class to interact with the Gemini API through google.generativeai.
    """

    def __init__(self, model_name='gemini-1.5-flash'):
        """
        Initialize the Gemini model using google.generativeai.

        Args:
            model_name (str): The model to use, default is 'gemini-1.5-flash'.
        """
        # Load the Google API key from the environment
        load_dotenv('.env', override=True)
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            raise ValueError("Google API key not found. Please set the 'GOOGLE_API_KEY' environment variable.")

        # Configure the Google generative AI with the API key
        genai.configure(api_key=google_api_key)

        # Load the Gemini model
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def get_response(self, prompt, history=None, temperature=0.7):
        """
        Get the response from the Gemini model using google.generativeai.

        Args:
            prompt (str): The prompt to send to the model.
            history (list): Not currently supported in the google.generativeai, passed for future use.
            temperature (float): The temperature for response randomness.

        Returns:
            str: The response from the model.
        """
        try:
            # Use the Google generative AI library to generate content
            response = self.model.generate_content(prompt)
            return response.text.strip()  # Returning the generated content text
        except Exception as e:
            logging.error(f"An error occurred with the Gemini model: {e}")
            return None


# OpenAI implementation of LLMModel
class OpenAIModel(LLMModel):
    """
    Class to interact with the OpenAI API using a client instance.
    """

    def __init__(self, api_key, model_name='gpt-4o-mini'):
        """
        Initialize the OpenAI model with the given API key and model name.

        Args:
            api_key (str): The OpenAI API key.
            model_name (str): The model to use, default is 'gpt-3.5-turbo'.
        """
        import openai
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name

    def get_response(self, prompt, history=None, temperature=0.99):
        """
        Get the response from the OpenAI model for the given prompt.

        Args:
            prompt (str): The prompt to send to the model.
            history (list): A list of previous messages (dictionaries with 'role' and 'content').
            temperature (float): The temperature for response randomness.

        Returns:
            str: The response from the model.
        """
        if history is None:
            history = []

        # Build messages list
        messages = [
            {
                "role": "system",
                "content": "You are a helpful but terse AI assistant who gets straight to the point.",
            },
        ]
        # Add conversation history
        messages.extend(history)

        # Add current user prompt
        messages.append({"role": "user", "content": prompt})
        print("@$"*4)
        print("messages are:", messages)
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature
            )
            response = completion.choices[0].message.content.strip()
            return response
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return None


class CoverLetterGenerator:
    """
    Class to generate and improve cover letters using any LLM model.
    """

    def __init__(self, ai_model: LLMModel):
        """
        Initialize with an instance of LLMModel.

        Args:
            ai_model (LLMModel): The LLM model to use for generation.
        """
        self.ai_model = ai_model

    def generate_cover_letter(self, cv_text, job_description_text, history=None):
        """
        Generate a cover letter based on CV and job description.

        Args:
            cv_text (str): The text of the CV.
            job_description_text (str): The job description text.
            history (list): Conversation history.

        Returns:
            str: The generated cover letter.
        """
        prompt = f"""Based on the provided job description and CV, write a concise, compelling, and personalized cover letter that highlights relevant skills and experiences.

Job Description:
{job_description_text}

CV:
{cv_text}

Tailor the letter to the specific job requirements and showcase the candidate's match for the position. Mention specific accomplishments and quantify results whenever possible. Keep the tone professional and precise. The letter should be no more than 4 sentences. Avoid unnecessary adjectives and emotive language. Finalize with 'Best regards,' followed by the applicant's name from the CV."""
        return self.ai_model.get_response(prompt, history=history)

    def create_critique(self, cover_letter, cv_text, job_description_text, history=None):
        """
        Generate a critique of the cover letter.

        Args:
            cover_letter (str): The cover letter text.
            cv_text (str): The text of the CV.
            job_description_text (str): The job description text.
            history (list): Conversation history.

        Returns:
            tuple: A tuple containing the critique text and the overall grade.
        """
        prompt = f"""I need you to critique a cover letter submitted for an AI Developer role. Evaluate it based on the following criteria:

        1. **Relevance to the Job**  
        2. **Form and Structure**  
        3. **Reliability**  
        4. **Professional Matching**  

        For each criterion:  
        - Provide a grade on a scale of 1-10 in the format: **#<Criterion Name> Grade: NUMBER#**  
        - Accompany each grade with a brief explanation highlighting strengths and areas for improvement.

        Additionally:  
        - Provide an **Overall Grade** for the cover letter on a scale of 1-10 using the format: **#Overall Grade: NUMBER#**  
        - Explain what influenced the overall score, emphasizing key strengths and critical weaknesses.

        Here are the inputs:

        **Cover Letter**:  
        {cover_letter}  

        **Resume (CV)**:  
        {cv_text}  

        **Job Description**:  
        {job_description_text}  

        Please ensure the grades and explanations are clearly structured, following the exact format specified."""

        response = self.ai_model.get_response(prompt, history=history)

        if response is None:
            raise ValueError("Failed to get a response from the AI model.")

        # Log the response for debugging
        print("AI Critique Response:", response)

        # Adjusted regular expression to allow flexibility in spaces and format
        match = re.search(r"#Overall Grade\s*:\s*(\d+(\.\d+)?)\s*/?\d*\s*#", response)
        if match:
            grade = float(match.group(1))
        else:
            raise ValueError("Failed to extract overall grade from the critique.")

        return response, grade

    def improve_cover_letter(self, cv_text, cover_letter, job_description_text, critique, overall_grade, history=None):
        """
        Improve the cover letter based on the critique.

        Args:
            cv_text (str): The CV text.
            cover_letter (str): The original cover letter.
            job_description_text (str): The job description.
            critique (str): The critique text.
            overall_grade (float): The overall grade from the critique.
            history (list): Conversation history.

        Returns:
            str: The improved cover letter.
        """
        if overall_grade >= 8:
            prompt = f"""Based on the provided job description, original cover letter, CV, and a high critique score ({overall_grade}/10), write a concise, factual, and personalized cover letter that emphasizes the strong aspects while polishing weaker areas.

Job Description:
{job_description_text}

CV:
{cv_text}

Original Cover Letter:
{cover_letter}

Critique:
{critique}

Keep it precise and concise, no more than 4 sentences. Avoid emotive adjectives. Finalize with 'Best regards,' and the candidate's name from the CV."""
        else:
            prompt = f"""Based on the provided job description, original cover letter, CV, and critique, write a concise, factual, and personalized cover letter that addresses the weaknesses highlighted in the critique.

Job Description:
{job_description_text}

CV:
{cv_text}

Original Cover Letter:
{cover_letter}

Critique:
{critique}

Tailor the letter to the job requirements, highlighting relevant skills and experiences. Keep it professional and concise, no more than 4 sentences. Avoid emotive adjectives. Finalize with 'Best regards,' followed by the applicant's name from the CV."""
        return self.ai_model.get_response(prompt, history=history)


# ai_interaction.py
class CVGenerator:
    """
    Class to generate and improve CVs using any LLM model.
    """

    def __init__(self, ai_model):
        """
        Initialize with an instance of LLMModel.

        Args:
            ai_model (LLMModel): The LLM model to use for generation.
        """
        self.ai_model = ai_model

    def generate_cv(self, cv_content, job_description_text, original_cv, history=None):
        """
        Generate an improved CV based on the original CV and job description.

        Args:
            cv_content (str): The current version of the CV content.
            job_description_text (str): The job description text.
            original_cv (str): The original, full text of the CV.

        Returns:
            str: The improved CV content.
        """
        prompt = f"""
        Review and improve the current CV content based on the original CV and the provided job description. Focus on the following:

        1. **Relevance to the Job**  
           - Identify and incorporate key skills, technologies, and terminologies from the job description into the CV (e.g., {job_description_text}).  
           - Highlight specific roles, projects, or achievements that directly align with the job's requirements. Ensure that the CV effectively emphasizes the candidate's most relevant experience.

        2. **Clarity and Structure**  
           - Ensure the CV follows a clear and logical structure with well-defined sections: Professional Summary, Experience, Education, Skills, Projects, and Publications.  
           - Improve readability by using consistent bullet points and formatting. 

        3. **Achievements and Impact**  
           - Emphasize measurable achievements (e.g., “Improved system efficiency by 20%”) where possible.  
           - When specific metrics aren’t available, highlight qualitative impacts to demonstrate the value delivered.

        4. **ATS Optimization**  
           - Naturally incorporate keywords and phrases from the job description throughout the CV.  
           - Ensure that relevant technologies and industry-specific jargon are included in the Professional Summary, Experience, and Skills sections to enhance ATS compatibility.

        5. **Professional Tone**  
           - Maintain a concise and professional tone throughout. Ensure there are no grammatical errors or formatting inconsistencies.
        6. **Preserve Company Names**  
            - Ensure **each entry** in the **Experience section** includes the **company name** from the **original CV**.  
            - If a company name is missing, use the **corresponding job title and date** to locate it in the **original CV**.  

        Update the current CV version based on these guidelines while preserving essential information from the original CV.

        **Inputs**:

        **Original CV**:  
        {original_cv}  

        **Current CV Version**:  
        {cv_content}  

        **Job Description**:  
        {job_description_text}  
        """

        return self.ai_model.get_response(prompt, history=history)

    def create_critique(self, cv_content, original_cv, job_description_text, history=None):
        """
        Generate a critique of the CV based on its relevance, structure, and professional appeal.

        Args:
            cv_content (str): The content of the current version of the CV.
            original_cv (str): The original, full text of the CV.
            job_description_text (str): The job description text.
            history (list): Conversation history.

        Returns:
            tuple: A tuple containing the critique text and the overall grade.
        """
        print(cv_content)
        prompt = f"""Provide a detailed critique of the following CV based on these criteria:

       1. **Relevance to the Job** 
          - Does the CV emphasize skills and experiences directly aligned with the job description? 
          - Consider how the candidate's **transferable skills** and **relevant experiences** can help bridge gaps where specific skills may not be present.
          - Grade: **#Relevance to the Job Grade: NUMBER##** 
          - Explain how well the CV aligns with the job requirements, especially when rare skills are involved. For example, if the job requires forensic research or reverse engineering, acknowledge the candidate's **ability to quickly learn** or **adapt** their current skills to meet these needs.

       2. **Clarity and Structure** 
          - Is the CV easy to read, well-organized, and logically structured? 
          - Grade: **#Clarity and Structure Grade: NUMBER##** 
          - Assess whether the layout enhances readability.

       3. **Skills Presentation** 
          - Are the candidate's technical and soft skills adequately highlighted and relevant? 
          - Grade: **#Skills Presentation Grade: NUMBER##** 
          - Highlight strengths and areas for improvement in skills representation. Focus on how well these skills are linked to real-world achievements.

       4. **Professionalism** 
          - Is the CV professional in tone, free of errors, and written in clear language? 
          - Grade: **#Professionalism Grade: NUMBER##** 
          - Note any tone, grammar, or formatting issues.
          
        5. **Reliability & Factual Accuracy**
           - Does the improved CV maintain **factual consistency** with the original CV?
           - Are all new achievements **verifiable**, or are there claims that seem exaggerated or unsubstantiated?
           - Ensure that all **quantitative achievements** (e.g., "improved efficiency by 30%") are based on information **already present** in the original CV or are **clearly justifiable**.
           - Ensure that all **company names** from the original CV are present.
           - Grade: **#Reliability Grade: NUMBER##** 
           - Explain if any parts of the improved CV introduce **unclear or unverifiable claims** and how to correct them.


       6. **Overall Impression** 
          - How well does the CV present the candidate as a strong fit for the role? 
          - Grade: **#Overall Grade: NUMBER.#** 
          - Summarize key strengths and critical weaknesses.

       **Instructions**: 
       - Ensure each grade follows the specified format **#Criterion Name Grade: NUMBER##** for criteria grades, and **#Overall Grade: NUMBER.#** for the overall impression. 
       - Provide actionable feedback, especially when there are gaps in certain areas (e.g., forensic research) that the candidate can potentially fill with **transferable skills**.
       - Be mindful of **rare skills** (such as forensic research) not always being present in candidates’ CVs, and instead focus on **how the candidate’s expertise** in other areas could contribute to the role.

       **Inputs**:

       **Current CV Version**: 
       {cv_content} 
       
       **Original CV Version**:
        {original_cv}

       **Job Description**: 
       {job_description_text} 

       Ensure consistency and provide all grades using the required format. Keeping grades using the required format is very important."""

        response = self.ai_model.get_response(prompt, history=history, temperature=0.01)

        if response is None:
            raise ValueError("Failed to get a response from the AI model.")

        # Adjusted regular expression to allow flexibility in spaces and format
        print(response)
        print("?" * 100)
        grades = {
            "Relevance to the Job": r"#Relevance to the Job Grade\s*:\s*(\d+(\.\d+)?)#",
            "Clarity and Structure": r"#Clarity and Structure Grade\s*:\s*(\d+(\.\d+)?)#",
            "Skills Presentation": r"#Skills Presentation Grade\s*:\s*(\d+(\.\d+)?)#",
            "Professionalism": r"#Professionalism Grade\s*:\s*(\d+(\.\d+)?)#",
            "Overall": r"#Overall Grade\s*:\s*(\d+(\.\d+)?)#",
        }
        flag = False
        grades_res = {}
        for name, pattern in grades.items():
            print(name)
            match = re.search(pattern, response)

            if not match:
                flag = True
            else:
                grades_res[name] = float(re.search(grades[name], response).group(1))
                # raise ValueError(f"Failed to extract {name} grade.")
        if flag:
            response = self.ai_model.get_response(prompt, history=history, temperature=0.01)

            if response is None:
                raise ValueError("Failed to get a response from the AI model.")

            # Adjusted regular expression to allow flexibility in spaces and format

            for name, pattern in grades.items():
                print(name)
                print(response)
                match = re.search(pattern, response)
                print(float(re.search(grades[name], response).group(1)))
                grades_res[name] = float(re.search(grades[name], response).group(1))
                if not match:
                    raise ValueError(f"Failed to extract {name} grade.")

        grade = float(re.search(grades["Overall"], response).group(1))

        match = re.search(r"#Overall Grade\s*[:\-]?\s*(\d+(\.\d+)?)\s*#", response)
        if match:
            grade = float(match.group(1))
        else:
            raise ValueError("Failed to extract overall grade from the critique.")
        print("grades_res",grades_res)
        return response, grade,grades_res
 
 

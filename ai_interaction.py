# ai_interaction.py

import openai
import re

from abc import ABC, abstractmethod
import re
from abc import ABC, abstractmethod
import logging


# Base class for LLM interaction
class LLMModel(ABC):
    """
    Abstract class for interacting with different LLM providers.
    """

    @abstractmethod
    def get_response(self, prompt, history=None, temperature=0.7):
        pass


# OpenAI implementation of LLMModel
class OpenAIModel(LLMModel):
    """
    Class to interact with the OpenAI API using a client instance.
    """

    def __init__(self, api_key, model_name='gpt-3.5-turbo'):
        """
        Initialize the OpenAI model with the given API key and model name.

        Args:
            api_key (str): The OpenAI API key.
            model_name (str): The model to use, default is 'gpt-3.5-turbo'.
        """
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name

    def get_response(self, prompt, history=None, temperature=0.7):
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
        prompt = f"""I need you to critique a cover letter submitted for an AI Developer role. Evaluate it based on:

    1. **Relevance to the Job**
    2. **Form and Structure**
    3. **Reliability**
    4. **Professional Matching**
    5. **Overall Impression**

    Provide an overall grade on a scale of 1-10 at the end in the format: **#Overall Grade : NUMBER#**

    **Cover Letter**:
    {cover_letter}

    **Resume (CV)**:
    {cv_text}

    **Job Description**:
    {job_description_text}

    Please ensure the grade is clearly provided using this exact format. Do NOT deviate from this format."""

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


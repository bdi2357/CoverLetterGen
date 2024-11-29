import pandas as pd
import os
from format_combined_cv_with_prompt import format_combined_cv_with_prompt
desired_structure_template = {
    "Contact Information": [],
    "Summary": [],
    "Work Experience": [],
    "Skills": {},
    "Education": [],
    "Projects": [],
    "Publications": []
}

class ModularIterativeAgent:
    def __init__(self, llm_client, max_iterations=4, improvement_threshold=-0.5):
        """
        Initialize the agent for iterative CV improvement using LLM.

        Args:
            llm_client: The client interface to interact with the LLM.
            max_iterations (int): The maximum number of iterations to improve the CV.
            improvement_threshold (float): The threshold for stopping improvement iterations.
        """
        self.llm_client = llm_client
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        self.history = []
        self.grades = []

    def parse_raw_cv(self, raw_cv_text, desired_structure = desired_structure_template):
        """
        Use LLM to parse raw CV text into a structured format.

        Args:
            raw_cv_text (str): The unstructured CV text.
            desired_structure (dict): The desired structured format.

        Returns:
            dict: A dictionary of parsed CV sections.
        """
        prompt = f"""
        The following text is an unstructured CV. Extract and organize the information according to this structure:

        Desired Structure:
        {desired_structure}

        Unstructured CV:
        {raw_cv_text}

        Ensure the output is in JSON format and matches the desired structure exactly.
        """
        response = self.llm_client.get_response(prompt, temperature=0.01)
        return response.get("parsed_cv", {})

    def generate_critique(self, cv_text, job_description_text):
        """
        Generate a critique and grade for the CV using the job description.

        Args:
            cv_text (str): The current CV text.
            job_description_text (str): The job description.

        Returns:
            tuple: A critique string, grade, and structured critique dictionary.
        """
        prompt = f"""
        Evaluate the following CV based on its relevance to the job description, clarity, skills presentation, and professionalism.

        Job Description:
        {job_description_text}

        CV:
        {cv_text}

        Provide a detailed critique in the following categories:
        1. Relevance to the Job
        2. Clarity and Structure
        3. Skills Presentation
        4. Professionalism
        5. Overall Impression

        Include a numerical grade (out of 10) for each category and an overall grade. Format the response as a JSON object.
        """
        response = self.llm_client.get_response(prompt, temperature=0.01)
        critique = response.get("critique", "")
        grade = response.get("overall_grade", 0)
        grades_dict = response.get("grades", {})
        return critique, grade, grades_dict

    def improve_section(self, section, content, critique, job_description_text):
        """
        Improve a specific CV section based on LLM feedback.

        Args:
            section (str): The name of the section to improve.
            content (str): The current content of the section.
            critique (str): The critique for the section.
            job_description_text (str): The job description.

        Returns:
            str: The improved section content.
        """
        prompt = f"""
        Improve the {section} section of the CV based on the following critique and job description.

        Section: {section}
        Content:
        {content}

        Critique:
        {critique}

        Job Description:
        {job_description_text}

        Ensure the improved section is concise, professional, and adheres to the desired CV structure.
        """
        response = self.llm_client.get_response(prompt, temperature=0.01)
        return response.get("improved_section", "")

    def improve_cv(self, raw_cv, job_description_text, desired_structure = desired_structure_template):
        """
        Perform iterative improvements on the CV.

        Args:
            raw_cv (str): The raw CV text.
            job_description_text (str): The job description.
            desired_structure (dict): The desired structure for the CV.

        Returns:
            str: The final improved CV.
        """
        # Step 1: Parse the raw CV
        structured_cv = self.parse_raw_cv(raw_cv, desired_structure)

        # Step 2: Iteratively improve the CV
        total_reward = 0
        previous_grade = 0

        for iteration in range(self.max_iterations):
            # Format the current CV
            combined_cv_flat = format_combined_cv_with_prompt(structured_cv)

            # Obtain critique and grade
            critique, grade, grades_dict = self.generate_critique(combined_cv_flat, job_description_text)
            total_reward += grade
            self.grades.append(grade)

            # Early stopping conditions
            improvement = grade - previous_grade
            if improvement < self.improvement_threshold or grade >= 9:
                break

            # Improve individual sections
            for section, content in structured_cv.items():
                relevant_critique = critique.get(section, "")
                if relevant_critique:
                    improved_section = self.improve_section(section, content, relevant_critique, job_description_text)
                    structured_cv[section] = improved_section

            previous_grade = grade

        # Step 3: Final formatting
        return format_combined_cv_with_prompt(structured_cv)

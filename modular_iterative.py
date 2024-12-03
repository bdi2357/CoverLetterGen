import pandas as pd
import os
import json
from format_combined_cv_with_prompt import format_combined_cv_with_prompt
desired_structure_template = {
    "Name" : [],
    "Contact": {},
    "Summary": [],
    "Experience": [],
    "Skills": {},
    "Education": [],
    "Projects": [],
    "Publications": []
}
feedback_mapping = {
        "Relevance to the Job": ["Work Experience", "Projects", "Summary"],
        "Skills Presentation": ["Skills"],
        "Clarity and Structure": ["Contact Information", "Summary", "Work Experience"],
        "Professionalism": ["Entire CV"],
        "Overall Impression": ["Summary"]
    }
section_to_critique_mapping = {
    "Contact": ["Clarity and Structure", "Professionalism"],
    "Summary": ["Relevance to the Job", "Clarity and Structure", "Skills Presentation", "Professionalism", "Overall Impression"],
    "Skills": ["Clarity and Structure", "Professionalism", "Skills Presentation", "Relevance to the Job"],
    "Experience": ["Clarity and Structure", "Professionalism", "Relevance to the Job"],
    "Education": ["Clarity and Structure", "Professionalism"],
    "Projects": ["Clarity and Structure", "Professionalism", "Skills Presentation", "Relevance to the Job"],
    "Publications": ["Clarity and Structure"],
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

    def parse_raw_cv(self, raw_cv_text, desired_structure=desired_structure_template):
        """
        Use LLM to parse raw CV text into a structured format.

        Args:
            raw_cv_text (str): The unstructured CV text.
            desired_structure (dict): The desired structured format.

            Returns:
                dict: A dictionary of parsed CV sections or an empty dictionary.
        """
        # Update the prompt to strictly enforce valid JSON output
        prompt = f"""
        The following text is an unstructured CV. Extract and organize the information according to this structure:

        Desired Structure:
        {desired_structure}

        Unstructured CV:
        {raw_cv_text}

        **IMPORTANT**: Ensure the output is a valid JSON object and does not include any extraneous text, such as ```json or '''json.
        """
        try:
            # Get the response from the LLM
            response = self.llm_client.ai_model.get_response(prompt, temperature=0.01)
            #print("Raw response from LLM:")
            #print("#" * 88)
            #print(response)

            # Remove potential wrapping (post-processing step)
            if response.startswith("'''json") or response.startswith("```json"):
                print("Detected wrapping with '''json or ```json. Removing wrapper.")
                response = response.strip("'''").strip("```").strip()

            # Attempt to parse the response as JSON
            response_dict = json.loads(response)
            return  response_dict
            # Check for the expected "parsed_cv" field
            if "parsed_cv" in response_dict:
                return response_dict["parsed_cv"]

            # Handle alternative structures (e.g., critiques)
            print("Unrecognized response structure. Returning empty dictionary.")
            return {}

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            return {}

        except Exception as e:
            print(f"Unexpected error during CV parsing: {e}")
            return {}

    import json

    def format_cv_with_prompt_using_llm(self,structured_cv):
        """
        Formats a structured CV dictionary into a professional CV using LLM prompts.

        Args:
            structured_cv (dict): A dictionary containing structured CV data.

        Returns:
            str: The formatted CV as a string.
        """
        prompt = f"""
        You are a professional CV formatter. Use the structured data provided below to create a professional CV.
        The CV should include the following sections:

        - Name
        - Contact Information
        - Summary
        - Work Experience
        - Skills
        - Education
        - Projects
        - Publications

        **Structured CV Data**:
        {json.dumps(structured_cv, indent=2)}

        **Formatting Guidelines**:
        1. Each section should have a clear and professional heading.
        2. Work Experience should include the title, duration, and key responsibilities as bullet points.
        3. Skills should be organized by categories, with each category including relevant skills as a list.
        4. Education should include degree, institution, year, and additional details such as thesis or honors.
        5. Projects should include the project name, description, and technologies used. Provide GitHub links if available.
        6. Publications should be listed in proper citation format.

        **Output Example**:

        Name: [Full Name]

        Contact Information:
        - Phone: [Phone Number]
        - Email: [Email Address]
        - LinkedIn: [LinkedIn Profile]
        - GitHub: [GitHub Profile]

        Summary:
        [Summary Text]

        Work Experience:
        - [Job Title], [Company] ([Duration])
          - [Responsibility 1]
          - [Responsibility 2]

        Skills:
        - [Skill Category 1]: [Skill 1], [Skill 2]
        - [Skill Category 2]: [Skill 3], [Skill 4]

        Education:
        - [Degree], [Institution] ([Year])
          - [Details]

        Projects:
        - [Project Name]: [Project Description]
          - Technologies Used: [Technology 1], [Technology 2]

        Publications:
        - [Publication 1]
        - [Publication 2]

        Format the output as plain text without extraneous characters.
        """
        # Get response from LLM
        response = self.llm_client.ai_model.get_response(prompt, temperature=0.01)

        #print("LLM Response:")
        #print(response)

        try:
            # Validate the response
            if response:
                return response.strip()
            else:
                return "Error: No response from the LLM."
        except Exception as e:
            print(f"Error formatting CV: {e}")
            return "Error: Could not format CV."
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

        Include a numerical grade (out of 10) for each category and an overall grade. 
        Format the response as a strict JSON that does not include the string json  object like this:

        {{
          "Relevance to the Job": {{
            "grade": NUMBER,
            "critique": "TEXT"
          }},
          "Clarity and Structure": {{
            "grade": NUMBER,
            "critique": "TEXT"
          }},
          "Skills Presentation": {{
            "grade": NUMBER,
            "critique": "TEXT"
          }},
          "Professionalism": {{
            "grade": NUMBER,
            "critique": "TEXT"
          }},
          "Overall Impression": {{
            "grade": NUMBER,
            "critique": "TEXT"
          }},
          "Overall Grade": NUMBER
        }}
        **IMPORTANT**: Ensure the output is a valid JSON object and does not include any extraneous text, such as ```json or '''json or json.
        """
        # Get the response from the LLM
        response = self.llm_client.ai_model.get_response(prompt, temperature=0.01)
        #print("Raw response:")
        #print(response)

        try:
            # Clean up and validate response
            response = response.strip()  # Remove extra whitespace
            if not response:
                raise ValueError("Response is empty.")

            # Parse the JSON response into a Python dictionary
            response_dict = json.loads(response)
            #print("Parsed JSON:", response_dict)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error decoding JSON response: {e}")
            response_dict = {
                "Relevance to the Job": {"grade": 0, "critique": "Error parsing response."},
                "Clarity and Structure": {"grade": 0, "critique": "Error parsing response."},
                "Skills Presentation": {"grade": 0, "critique": "Error parsing response."},
                "Professionalism": {"grade": 0, "critique": "Error parsing response."},
                "Overall Impression": {"grade": 0, "critique": "Error parsing response."},
                "Overall Grade": 0,
            }

        # Extract critiques and grades
        critique = {
            "Relevance to the Job": response_dict.get("Relevance to the Job", {}).get("critique", ""),
            "Clarity and Structure": response_dict.get("Clarity and Structure", {}).get("critique", ""),
            "Skills Presentation": response_dict.get("Skills Presentation", {}).get("critique", ""),
            "Professionalism": response_dict.get("Professionalism", {}).get("critique", ""),
            "Overall Impression": response_dict.get("Overall Impression", {}).get("critique", ""),
        }
        grade = response_dict.get("Overall Grade", 0)
        grades_dict = {
            "Relevance to the Job": response_dict.get("Relevance to the Job", {}).get("grade", 0),
            "Clarity and Structure": response_dict.get("Clarity and Structure", {}).get("grade", 0),
            "Skills Presentation": response_dict.get("Skills Presentation", {}).get("grade", 0),
            "Professionalism": response_dict.get("Professionalism", {}).get("grade", 0),
            "Overall Impression": response_dict.get("Overall Impression", {}).get("grade", 0),
            "Overall Grade": grade,
        }

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
        Current Content:
        {content}

        Critique:
        {critique}

        Job Description:
        {job_description_text}

        Provide the improved section as plain text.
         **IMPORTANT**: Ensure the output is a valid JSON object and does not include any extraneous text, such as ```json or '''json.
        """
        # Get the response from the LLM
        response = self.llm_client.ai_model.get_response(prompt, temperature=0.01)
        #print("Raw response from LLM:")
        #print(response)

        # Handle the response appropriately
        if isinstance(response, dict):
            # If already a dictionary, return the appropriate section
            return response.get("improved_section", content)
        elif isinstance(response, str):
            try:
                # Attempt to parse if the response is JSON string
                response_dict = json.loads(response.strip())
                return response_dict.get("improved_section", content)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON response: {e}")
                return content  # Fallback to original content
        else:
            # Fallback if response is neither string nor dict
            print("Unexpected response format. Returning original content.")
            return content


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
        cv_content = raw_cv #self.llm_client.generate_cv(raw_cv, job_description_text, raw_cv, history=None)
        structured_cv = self.parse_raw_cv(cv_content, desired_structure)

        # Step 2: Iteratively improve the CV
        total_reward = 0
        previous_grade = 0

        for iteration in range(self.max_iterations):
            # Format the current CV
            combined_cv_flat = self.format_cv_with_prompt_using_llm(structured_cv)

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
                if section in section_to_critique_mapping.keys():
                    section_critique = "%s\n"%section
                    for k in section_to_critique_mapping[section]:
                        section_critique += k + ": " + critique.get(k,"") +"\n"
                    relevant_critique = section_critique
                    print("For section %s\n"%section)
                    print(relevant_critique)
                    print("&"*88)
                    if relevant_critique:
                        improved_section = self.improve_section(section, content, relevant_critique, job_description_text)
                        structured_cv[section] = improved_section

            previous_grade = grade

        # Step 3: Final formatting
        return self.format_cv_with_prompt_using_llm(structured_cv), critique
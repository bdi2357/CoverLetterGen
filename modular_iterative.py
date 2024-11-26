# basic_iterative.py
import  pandas as pd
import os
from ExtractCompanyNameJob import extract_company_name_and_job_name
class ModularIterativeAgent:
    def __init__(self, cover_letter_gen, max_iterations=4, improvement_threshold=-0.5):
        """
        Initialize the BasicIterativeAgent with a CoverLetterGenerator and hyperparameters.

        Args:
            cover_letter_gen (CoverLetterGenerator): The cover letter generator.
            max_iterations (int): The maximum number of iterations to perform.
            improvement_threshold (float): The threshold for stopping when no significant improvement is made.
        """
        self.cover_letter_gen = cover_letter_gen
        self.max_iterations = max_iterations
        self.improvement_threshold = improvement_threshold
        self.history = []
        self.grades = []


    def generate_cover_letter(self, cv_text, job_description_text):
        """
        Generate a cover letter using a constant prompt based on the CV and job description.

        Args:
            cv_text (str): The CV text.
            job_description_text (str): The job description text.

        Returns:
            str: The generated cover letter.
        """
        prompt = f"""Based on the provided job description and CV, write a concise, compelling, and personalized cover letter that highlights relevant skills and experiences.

Job Description:
{job_description_text}

CV:
{cv_text}

Tailor the letter to the specific job requirements and showcase the candidate's match for the position. Mention specific accomplishments and quantify results whenever possible. Keep the tone professional and precise. The letter should be no more than 4 sentences. Avoid unnecessary adjectives and emotive language."""
        cover_letter = self.cover_letter_gen.generate_cover_letter(cv_text, job_description_text, history=self.history)
        self._add_to_history("user", cover_letter)
        self._add_to_history("assistant", cover_letter)
        return cover_letter

    def _add_to_history(self, role, content):
        """
        Add a message to the conversation history.

        Args:
            role (str): The role of the message sender ('user' or 'assistant').
            content (str): The content of the message.
        """
        self.history.append({"role": role, "content": content})

    def improve_cover_letter(self, cv_text, cover_letter, job_description_text):
        """
        Perform iterative improvements on the cover letter based on critiques.

        Args:
            cv_text (str): The CV text.
            cover_letter (str): The current cover letter text.
            job_description_text (str): The job description text.

        Returns:
            str: The improved cover letter.
        """
        total_reward = 0
        previous_grade = 0

        for iteration in range(self.max_iterations):
            # Get critique and grade the current cover letter
            critique, grade = self.cover_letter_gen.create_critique(
                cover_letter, cv_text, job_description_text, history=self.history
            )
            total_reward += grade
            self.grades.append(grade)
            print(f"Iteration {iteration + 1}, Grade: {grade}, Cumulative Reward: {total_reward}")

            # Add critique to history as a response from the assistant, not the user
            self._add_to_history("assistant", critique)

            # Check for early stopping if improvement is minimal
            improvement = grade - previous_grade
            if improvement < self.improvement_threshold:
                print(f"No significant improvement, stopping early after iteration {iteration + 1}.")
                break

            # Check if satisfactory grade has been reached
            if grade >= 9:
                print("Achieved satisfactory grade.")
                break

            # Incorporate critique into the next improvement step
            improvement_prompt = f"""
                        Based on the provided job description, CV, original cover letter, and the critique, 
                        improve the cover letter to address the weaknesses pointed out. Tailor the letter 
                        to better match the job requirements and highlight the most relevant skills and 
                        experience.

                        Job Description:
                        {job_description_text}

                        CV:
                        {cv_text}

                        Original Cover Letter:
                        {cover_letter}

                        Critique:
                        {critique}

                        Keep the tone professional, concise, and focused on the strengths of the candidate.
                        """

            # Add user input for improvement prompt
            self._add_to_history("user", improvement_prompt)

            # Generate improved cover letter based on critique and prompt
            cover_letter = self.cover_letter_gen.get_response(improvement_prompt, history=self.history)

            # Add improved cover letter as an assistant response
            self._add_to_history("assistant", cover_letter)

            previous_grade = grade

        return cover_letter, critique

    def extract_relevant_critique(self, section, critique):
        """
        Map critique categories to the relevant CV sections and extract specific feedback.
        """
        critique_mapping = {
            "Relevance to the Job": ["Summary", "Work Experience", "Projects"],
            "Clarity and Structure": ["Summary", "Work Experience", "Skills", "Education", "Projects", "Publications"],
            "Skills Presentation": ["Skills"],
            "Professionalism": ["Summary", "Work Experience", "Projects"],
            "Overall Impression": ["Summary"]
        }

        relevant_feedback = []
        for category, sections in critique_mapping.items():
            if section in sections and category in critique:
                feedback = critique[category][0]  # Extract feedback text
                relevant_feedback.append(f"{category}: {feedback}")

        return "\n".join(relevant_feedback) if relevant_feedback else None

    def parse_improved_section(self, section, improved_content):
        """
        Parse the improved section content and integrate it into the CV structure.
        """
        parsed_content = improved_content.split("\n")
        return [line.strip() for line in parsed_content if line.strip()]

    def improve_cv(self, original_cv, last_improved_cv, job_description_text, desired_structure):
        # Parse original and last improved CVs
        original_structured = parse_original_cv(original_cv, desired_structure)
        last_improved_structured = parse_last_improved_cv(last_improved_cv, desired_structure)

        # Combine CVs
        combined_structured = combine_cvs(original_structured, last_improved_structured)

        # Initialize iteration variables
        total_reward = 0
        previous_grade = 0
        company_name_and_job_name = extract_company_name_and_job_name(job_description_text)
        grades_df = pd.DataFrame(
            columns=["iteration", "Relevance to the Job", "Clarity and Structure", "Skills Presentation",
                     "Professionalism", "Overall"])

        for iteration in range(self.max_iterations):
            # Flatten combined CV for critique
            combined_cv_flat = self.format_combined_cv(combined_structured)

            # Obtain critique and grade
            critique, grade, grades_dict = self.cover_letter_gen.create_critique(
                combined_cv_flat, original_cv, job_description_text, history=self.history
            )

            # Log grades
            grades_df = pd.concat([grades_df, pd.DataFrame([{**{"iteration": iteration}, **grades_dict}])],
                                  ignore_index=True)
            total_reward += grade
            self.grades.append(grade)

            # Add critique to history
            self._add_to_history("assistant", critique)

            # Early stopping
            improvement = grade - previous_grade
            if improvement < self.improvement_threshold:
                print(f"No significant improvement. Stopping after iteration {iteration + 1}.")
                break

            if grade >= 9:
                print("Achieved satisfactory grade.")
                break

            # Modular improvement for each section
            for section, content in combined_structured.items():
                relevant_critique = self.extract_relevant_critique(section, critique)
                if relevant_critique:
                    improvement_prompt = f"""
                    Improve the {section} section of the CV based on the critique provided. Focus on addressing the specific feedback below and aligning the section with the job description.

                    Section: {section}
                    Content:
                    {content}

                    Critique:
                    {relevant_critique}

                    Job Description:
                    {job_description_text}

                    Ensure the section aligns with the desired structure and highlights relevant skills, achievements, and professional tone effectively.
                    """
                    improved_section = self.cover_letter_gen.get_response(improvement_prompt, history=self.history)
                    combined_structured[section] = self.parse_improved_section(section, improved_section)

            previous_grade = grade

        # Final formatting
        final_cv = self.format_combined_cv(combined_structured)
        validation_critique = \
        self.cover_letter_gen.create_critique(final_cv, original_cv, job_description_text, history=self.history)[0]
        grades_df.to_csv(os.path.join("Output", "Grades", f"{company_name_and_job_name}_grades.csv"), index=False)

        return final_cv, validation_critique



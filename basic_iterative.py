# basic_iterative.py
import  pandas as pd
import os
from ExtractCompanyNameJob import extract_company_name_and_job_name
class BasicIterativeAgent:
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
            cover_letter = self.cover_letter_gen.ai_model.get_response(improvement_prompt, history=self.history)

            # Add improved cover letter as an assistant response
            self._add_to_history("assistant", cover_letter)

            previous_grade = grade

        return cover_letter, critique

    def improve_cv(self, original_cv,  job_description_text):
        """
        Perform iterative improvements on the CV based on detailed critiques.

        Args:
            original_cv (str): The full text of the original CV.
            personal_info (str): The personal information text from the CV.
            job_history (str): The job history text from the CV.
            skills (str): The skills extracted from the CV.
            job_description_text (str): The job description text.

        Returns:
            tuple: The improved CV and the final detailed critique.
        """
        total_reward = 0
        previous_grade = 0
        company_name_and_job_name = extract_company_name_and_job_name(job_description_text)
        # Combine initial CV sections
        cv_content = self.cover_letter_gen.generate_cv(original_cv, job_description_text, original_cv, history=None)
        grades_names = ["Relevance to the Job", "Clarity and Structure","Skills Presentation",
            "Professionalism","Overall"]
        grades_df = pd.DataFrame(columns=['iteration']+grades_names)
        final_cv = cv_content
        for iteration in range(self.max_iterations):

            # Obtain a detailed critique and grade for the current CV
            critique, grade, grades_dict = self.cover_letter_gen.create_critique(
                cv_content, original_cv, job_description_text, history=self.history
            )
            print("grades_dict\n",grades_dict)
            iteration_dict = {'iteration': iteration}

            # Merge the dictionaries and convert to DataFrame
            temp_df = pd.DataFrame({**iteration_dict, **grades_dict}, index=[0])

            # Append to the main DataFrame
            grades_df = pd.concat([grades_df, temp_df], ignore_index=True)

            total_reward += grade
            self.grades.append(grade)
            print(f"Iteration {iteration + 1}, Grade: {grade}, Cumulative Reward: {total_reward}")

            # Add critique to the assistant's responses in history
            self._add_to_history("assistant", critique)

            # Early stopping conditions
            improvement = grade - previous_grade
            if improvement < self.improvement_threshold:
                print(f"No significant improvement, stopping early after iteration {iteration + 1}.")
                break

            if grade >= 9:
                print("Achieved satisfactory grade.")
                grades_df.to_csv(os.path.join("Output","Grades",company_name_and_job_name + "_BasicIterativeAgent_grades.csv"), index=False)

                break

            # Use the critique to guide CV improvements
            improvement_prompt = f"""
            You are tasked with improving the candidate's CV iteratively. Your goal is to align the CV with the job description, ensure factual correctness, and enhance readability and impact. In each iteration, you must address the critique points and ensure measurable improvements in the following categories:

            ### Key Improvement Areas:
            1. **Relevance to the Job**:
               - Ensure alignment with the job description by incorporating role-specific skills, tools, and technologies where factually applicable.
               - Use critique feedback such as "{critique.split('**1. Relevance to the Job**')[1].split('**')[0].strip() if '**1. Relevance to the Job**' in critique else 'No feedback provided'}".
               - Emphasize directly relevant experience and projects that demonstrate the candidate's ability to meet job requirements.

            2. **Clarity and Structure**:
               - Follow a clear and logical structure with consistent formatting.
               - Address specific feedback such as "{critique.split('**2. Clarity and Structure**')[1].split('**')[0].strip() if '**2. Clarity and Structure**' in critique else 'No feedback provided'}".
               - Simplify complex descriptions and ensure concise bullet points for quick readability.

            3. **Skills Presentation**:
               - Highlight technical and soft skills relevant to the role.
               - Incorporate suggestions like "{critique.split('**3. Skills Presentation**')[1].split('**')[0].strip() if '**3. Skills Presentation**' in critique else 'No feedback provided'}".
               - Link specific skills to concrete achievements or projects to demonstrate their practical application.

            4. **Professionalism**:
               - Maintain a professional tone and error-free presentation.
               - Address any issues with grammar, tone, or formatting based on feedback such as "{critique.split('**4. Professionalism**')[1].split('**')[0].strip() if '**4. Professionalism**' in critique else 'No feedback provided'}".

            5. **Keyword Optimization for ATS**:
               - Optimize for applicant tracking systems by naturally incorporating keywords from the job description.
               - Avoid keyword stuffing; ensure that each mention is tied to a specific skill or experience to maintain credibility.

            ### Improvement Actions:
            - **Specific Examples**: For any critique pointing out missing or underdeveloped content, provide detailed examples or elaborations. For instance, if observability tools are mentioned, ensure projects involving telemetry or performance monitoring are highlighted.
            - **Quantifiable Achievements**: Include measurable outcomes (e.g., reduced downtime by X%) where applicable. If such metrics are not explicitly mentioned, consider emphasizing qualitative impacts.
            - **Iteration-Specific Changes**: Each iteration must introduce new improvements based on the critique. Refrain from repeating similar changes without adding new value.

            ### Context:
            - **Job Description**:  
            {job_description_text}

            - **Current CV**:  
            {cv_content}

            - **Original CV Version**:  
            {original_cv}

            - **Critique**:  
            {critique}

            ### Focus:
            - Ensure dynamic and targeted improvements in each iteration.
            - Strictly adhere to factual correctness. Do not invent achievements or experiences that are not present in the original CV.
            - Continuously enhance the CV until all critique points are adequately addressed and grades improve.

            ### Iteration Goal:
            At the end of each iteration, the improved CV should demonstrate noticeable progress in alignment with the job description and critique feedback.
            """

            print("improvement_prompt")

            # Add the improvement prompt to the user's history
            self._add_to_history("user", improvement_prompt)

            # Generate the next version of the CV
            cv_content = self.cover_letter_gen.ai_model.get_response(improvement_prompt, history=self.history , temperature=1.2)

            # Store the improved CV in the assistant's response history
            self._add_to_history("assistant", cv_content)

            # Update the previous grade
            previous_grade = grade

            # Final formatting enforcement
            enforcement_prompt = """
            Ensure the final CV adheres strictly to the following format:

            ```plaintext
            {{Name}}
            Contact Information
            Ø  Phone: {{Contact.Cellular}} | Email: {{Contact.Email}}
            Ø  LinkedIn: {{LinkedIn}} {% if GitHub %}Ø  GitHub: {{GitHub}}{% endif %}

            Summary
            {{Summary}}

            Work Experience
            {% for job in Experience %}
            · {{job.Title}} | ({{job.Duration}})
            {% for resp in job.Responsibilities %}
            Ø  {{resp}}
            {% endfor %}{% endfor %}

            Skills
            {% for category, category_skills in Skills.items() %}
            ·         {{category}}:  {% for skill in category_skills %}{{skill}}{% endfor %}
            {% endfor %}

            Education
            {% for edu in Education %}
            ·         {{edu.Degree}} | {{edu.Institution}} | {{edu.Year}} {% if edu.Thesis %}| {{edu.Thesis}}{% endif %}
            {% endfor %}

            Projects
            {% for project in Projects %}
            · {{project.Title}}: {{project.Description}} {% if project.Link %}Ø  Link: {{project.Link}}{% endif %}
            {% endfor %}

            Publications
            {% for publication in Publications %}
            ·         {{publication}}
            {% endfor %}
            ```
            Apply this format to the final CV version.
            """

            self._add_to_history("user", enforcement_prompt)
            final_cv = self.cover_letter_gen.ai_model.get_response(enforcement_prompt, history=self.history,
                                                                   temperature=0.1)

        grades_df.to_csv(os.path.join("Output", "Grades", company_name_and_job_name +"_BasicIterativeAgent__grades.csv"), index= False)
        return final_cv, critique




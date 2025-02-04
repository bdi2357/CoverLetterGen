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
        company_name_and_job_name = extract_company_name_and_job_name(job_description_text,self.cover_letter_gen.ai_model.api_key)
        company_name_and_job_name = company_name_and_job_name.replace("/","_").replace("|","_")
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
                company_name_and_job_name = company_name_and_job_name.replace("|","_")
                print("$"*77)
                print(company_name_and_job_name)
                print(os.path.join("Output","Grades",company_name_and_job_name + "_BasicIterativeAgent_grades.csv"))

                grades_df.to_csv(os.path.join("Output","Grades",company_name_and_job_name + "_BasicIterativeAgent_grades.csv"), index=False)

                break

            # Use the critique to guide CV improvements
            improvement_prompt = f"""
            You are tasked with improving the candidate's CV iteratively. Your goal is to align the CV with the job description, ensure factual correctness, and enhance readability and impact. In each iteration, you must address the critique points and ensure measurable improvements in the following categories, while ensuring that all claims are substantiated with real, verifiable results.

            ### Key Improvement Areas:

            1. **Relevance to the Job**:
               - Ensure alignment with the job description by incorporating role-specific skills, tools, and technologies where factually applicable.
               - **Example 1**:  
                 CV Text: "Increased portfolio returns by 10% by developing advanced algorithmic trading strategies."  
                 Critique: "Provide more specifics on the strategies and how they were developed (e.g., models, algorithms, or techniques used)."  
                 **Improvement**: "Developed and deployed an end-to-end portfolio optimization software based on customer constraints and customizable cost functions, which improved asset allocation and increased portfolio returns by 10%. The software was tested in live market conditions, leading to a measurable increase in investment performance."

            2. **Clarity and Structure**:
               - Follow a clear and logical structure with consistent formatting.
               - **Example 1**:  
                 CV Text: "Developed innovative portfolio management tools, reducing analysis time by 30%."  
                 Critique: "Specify what kind of tools were developed and how they improved the workflow or decision-making."  
                 **Improvement**: "Developed portfolio management tools that integrated machine learning algorithms to predict market movements, reducing analysis time by 30%. The tools allowed portfolio managers to make faster, more accurate decisions on asset allocation."

            3. **Skills Presentation**:
               - Highlight technical and soft skills relevant to the role.
               - **Example 1**:  
                 CV Text: "Technical Skills: Python, R, C++, TensorFlow, PyTorch."  
                 Critique: "Link the technical skills with concrete examples from past projects to demonstrate how they were applied."  
                 **Improvement**: "Technical Skills: Python (Developed algorithmic trading strategies using TensorFlow), R (Analyzed financial time-series data), C++ (Optimized high-frequency trading systems for real-time execution), TensorFlow (Built predictive models for market trends), PyTorch (Created neural network models for asset price prediction)."

            4. **Professionalism**:
               - Maintain a professional tone and error-free presentation.
               - **Example 1**:  
                 CV Text: "Developed trading strategies for multiple asset classes."  
                 Critique: "Clarify the types of assets and the impact of the strategies."  
                 **Improvement**: "Developed algorithmic trading strategies for equities, forex, and commodities using advanced optimization techniques, resulting in improved profitability across all asset classes. These strategies were integrated into a multi-asset trading platform and tested against historical data."

            5. **Quantifiable Achievements (with Evidence)**:
               - Incorporate quantifiable achievements to demonstrate the impact of your work, but ensure that they are based on solid, verifiable results. Focus on **specific projects**, **methodologies**, and **delivered solutions** that align with job requirements.
               - **Example 1**:  
                 CV Text: "Achieved a 25% improvement in asset allocation efficiency."  
                 Critique: "Be more specific about the methods used to achieve this result and provide evidence for the improvement."  
                 **Improvement**: "Developed and delivered end-to-end portfolio optimization software, incorporating customer constraints and customizable cost functions. The software enabled real-time asset allocation adjustments, improving efficiency by 25% in portfolio management. This improvement was verified through backtesting and implemented in client-facing solutions."

               - **Example 2**:  
                 CV Text: "Led cross-functional teams for various financial projects."  
                 Critique: "Provide more details on the projects and their results."  
                 **Improvement**: "Led cross-functional teams in the development of a real-time trading algorithm, optimizing execution speed by 30% and improving trade accuracy by 20%. The system was deployed in live trading environments and showed measurable improvements in execution efficiency."

            ### Improvement Actions:
            - **Specific Examples**: For any critique pointing out missing or underdeveloped content, provide detailed examples or elaborations. For instance, when mentioning portfolio optimization, specify the techniques used (e.g., genetic algorithms, Markowitz portfolio theory) and how they were delivered (e.g., as client-facing software or within an internal tool).
            - **Quantifiable Achievements with Solid Evidence**: Include measurable outcomes (e.g., increased efficiency, improved returns, reduced time-to-market) where applicable, but only if these metrics can be substantiated with real-world deliverables (e.g., project outcomes, backtesting results, client feedback).
            - **Iteration-Specific Changes**: Each iteration must introduce new improvements based on the critique. Avoid repeating similar changes without adding new value.

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
            At the end of each iteration, the improved CV should demonstrate noticeable progress in alignment with the job description and critique feedback, supported by **real, verifiable project results and achievements**.
            """

            print("improvement_prompt")

            # Add the improvement prompt to the user's history
            self._add_to_history("user", improvement_prompt)

            # Generate the next version of the CV
            #cv_content = self.cover_letter_gen.ai_model.get_response(improvement_prompt, history=self.history , temperature=0.99)
            cv_content = self.cover_letter_gen.ai_model.get_response(improvement_prompt, history=None,temperature=0.99)
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

        print("^"*77)
        print(company_name_and_job_name)
        print(os.path.join("Output", "Grades", company_name_and_job_name.replace("|","_") +"_BasicIterativeAgent__grades.csv"))
        grades_df.to_csv(os.path.join("Output", "Grades", company_name_and_job_name.replace("|","_") +"_BasicIterativeAgent__grades.csv"), index= False)
        return final_cv, critique




# basic_iterative.py

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
            cover_letter = self.cover_letter_gen.get_response(improvement_prompt, history=self.history)

            # Add improved cover letter as an assistant response
            self._add_to_history("assistant", cover_letter)

            previous_grade = grade

        return cover_letter, critique

    def improve_cv(self, original_cv, personal_info, job_history, skills, job_description_text):
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

        # Combine initial CV sections
        cv_content = f"{personal_info}\n\n{job_history}\n\n{skills}"

        for iteration in range(self.max_iterations):
            # Obtain a detailed critique and grade for the current CV
            critique, grade = self.cover_letter_gen.create_critique(
                cv_content, original_cv, job_description_text, history=self.history
            )

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
                break

            # Use the critique to guide CV improvements
            improvement_prompt = f"""
            Based on the provided job description, CV, original version, and critique, improve the CV to address the following areas. Use specific suggestions from the critique to guide improvements in each category:

            ### References to Critique Suggestions:
            - **Relevance to the Job**: Incorporate suggestions such as "{critique.split('**1. Relevance to the Job**')[1].split('**')[0].strip()}".
            - **Clarity and Structure**: "{critique.split('**2. Clarity and Structure**')[1].split('**')[0].strip()}".
            - **Skills Presentation**: "{critique.split('**3. Skills Presentation**')[1].split('**')[0].strip()}".
            - **Professionalism**: "{critique.split('**4. Professionalism**')[1].split('**')[0].strip()}".
            - **Overall Impression**: "{critique.split('**5. Overall Impression**')[1].split('**')[0].strip()}".

            ### Action Points:
            1. **Relevance to the Job**  
               - Align content with critical job-specific terminology and technologies, such as LangChain, AWS Bedrock, and observability, as per the critique feedback.
               - Expand on relevant experiences in projects or roles that demonstrate direct problem-solving capabilities (e.g., reducing MTTR or enhancing telemetry analysis).

            2. **Clarity and Structure**  
               - Follow a logical and clearly defined CV structure, including sections like **Summary**, **Experience**, and **Skills**. Ensure bullet points are consistently formatted and section headings visually distinct.
               - Implement any structural improvements suggested in the critique to enhance readability and flow.

            3. **Skills and Measurable Achievements**  
               - Where metrics or KPIs are available, highlight them (e.g., improved performance by X%, reduced downtime by Y%). 
               - When exact metrics aren't available, emphasize qualitative results (e.g., improved system scalability) in alignment with critique feedback.

            4. **Professionalism**  
               - Ensure a professional tone and consistency in grammar and formatting throughout. Address any specific feedback from the critique (e.g., redundant information or repeated sections).
               - Validate GitHub links or external references to ensure they are correct and active.

            5. **Keyword Optimization for ATS**  
               - Ensure all key technologies and job-related jargon, as emphasized in the job description, are embedded naturally in relevant sections. 
               - Optimize keyword distribution to improve ATS compatibility while maintaining readability for human reviewers.

            **Inputs**:
            - **Job Description**:  
            {job_description_text}

            - **CV**:  
            {cv_content}

            - **Original CV Version**:  
            {original_cv}

            - **Critique**:  
            {critique}

            **Focus Areas**:
            Use the critique suggestions dynamically to enhance both ATS and human readability. Ensure all structural and content recommendations are implemented for maximum impact.
            """

            # Add the improvement prompt to the user's history
            self._add_to_history("user", improvement_prompt)

            # Generate the next version of the CV
            cv_content = self.cover_letter_gen.ai_model.get_response(improvement_prompt, history=self.history)

            # Store the improved CV in the assistant's response history
            self._add_to_history("assistant", cv_content)

            # Update the previous grade
            previous_grade = grade

        return cv_content, critique




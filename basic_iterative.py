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
            Based on the following detailed critique, refine the CV to address the highlighted weaknesses.
            Focus on improving clarity, relevance, and alignment with the job description.

            **Job Description**:
            {job_description_text}

            **Original CV**:
            {original_cv}

            **Current CV Version**:
            {cv_content}

            **Detailed Critique**:
            {critique}

            Revise the CV by incorporating specific improvements suggested in each section. 
            Keep the formatting consistent and ensure quantifiable achievements are emphasized where relevant.
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




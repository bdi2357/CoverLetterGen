# basic_iterative.py

class BasicIterativeAgent:
    def __init__(self, cover_letter_gen, max_iterations=10, improvement_threshold=0.05):
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
            critique, grade = self.cover_letter_gen.create_critique(cover_letter, cv_text, job_description_text,
                                                                    history=self.history)
            total_reward += grade
            self.grades.append(grade)
            print(f"Iteration {iteration + 1}, Grade: {grade}, Cumulative Reward: {total_reward}")

            # Add critique to history
            self._add_to_history("user", critique)
            self._add_to_history("assistant", critique)

            improvement = grade - previous_grade
            if improvement < self.improvement_threshold:
                print(f"No significant improvement, stopping early after iteration {iteration + 1}.")
                break

            if grade >= 9:
                print("Achieved satisfactory grade.")
                break

            # Use the same prompt for improvements (constant)
            #cover_letter = self.cover_letter_gen.generate_cover_letter(self.history[-2]["content"],history=self.history)
            cover_letter = self.cover_letter_gen.generate_cover_letter(cv_text,job_description_text)

            # Add improved cover letter to history
            self._add_to_history("user", cover_letter)
            self._add_to_history("assistant", cover_letter)

            previous_grade = grade

        return cover_letter,critique

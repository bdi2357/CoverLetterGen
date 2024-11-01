import logging
import os,re
from ai_interaction import OpenAIModel, CoverLetterGenerator
from basic_iterative import BasicIterativeAgent  # Import BasicIterativeAgent
#from actor_critic import ActorCriticAgent  # Import ActorCriticAgent
from data_handling import load_and_extract_text, extract_applicant_name
from utilities import create_pdf
from dotenv import load_dotenv
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('.env', override=True)


class CVParserAI:
    def __init__(self, client, model_name="gpt-3.5-turbo-0125"):
        self.client = client
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
        messages = [
            {"role": "system", "content": "You are a helpful but terse AI assistant who gets straight to the point."}
        ]
        if history:
            messages.extend(history)

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

    def parse_cv_sections(self, cv_content):
        """
        Parses the CV content by asking the AI model to structure it into defined sections.

        Args:
            cv_content (str): The full text of the CV.

        Returns:
            dict: A dictionary with section names as keys and section content as values.
        """
        prompt = f"""
        Here is a CV document:

        {cv_content}

        Please organize this content into structured sections:
        - Name
        - Contact Information
        - LinkedIn
        - Professional Summary
        - Work Experience
        - Education
        - Skills
        - Publications

        Return each section in a clear and structured dictionary format.
        """

        response = self.get_response(prompt, temperature=0.2)
        print("HERE")
        if response:
            # Attempt to parse the response assuming it returns a dictionary-like format
            try:
                # Using eval safely with limited scope
                parsed_response = eval(response, {"__builtins__": {}}, {})
                if isinstance(parsed_response, dict):
                    return parsed_response
                else:
                    logging.warning("Response was not in dictionary format.")
                    return {}
            except Exception as e:
                logging.error(f"Failed to parse response as dictionary: {e}")
                return {}
        else:
            return {}


# Example usage
if __name__ == "__main__":
    load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Set up OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Assume `openai` is the OpenAI client object initialized with your API key
    parser = CVParserAI(client)

    cv_content = """
    Itay Ben-Dan

Address: Haarava 20, Herzliya, Israel 46100
Contact: +972544539284, itaybd@gmail.com
LinkedIn: Itay Ben-Dan LinkedIn Profile

Professional Summary:

Seasoned AI Developer with a strong foundation in machine learning, data engineering, and financial system analytics. Recognized for developing AI solutions, implementing NLP techniques, and unifying diverse data into a standardized format. Skilled in Python, TensorFlow, and PyTorch.

Work Experience:

2017-Present: AI Consultant and Head of Research, Finzor Ltd.
- Developed AI models for portfolio management and investment analysis tools.
- Unified data from diverse sources into standard formats.
- Led a team in the full cycle of software product development.

2016-2017: Principal AI Developer, Palo Alto Networks
- Applied AI in reverse engineering and malware analysis.
- Developed adaptive models for anti-malware systems.

2015-2016: Senior Data Scientist, SparkBeyond
- Utilized big data for predictive analytics and machine learning.
- Implemented automatic feature generation methods for time series analysis.

2011-2015: Senior Quantitative Researcher, WorldQuant
- Developed automated computational methods for quant-driven strategies.
- Applied predictive analytics across various assets.

2010-2011: Senior Software Engineer, Broadcom
- Designed network and packet processing methods.
- Implemented advanced automated testing methods.

Education:

2009: Ph.D. in Mathematics, Technion, Haifa
- Specialized in Discrete Geometry

2004: M.Sc. in Mathematics, Technion, Haifa
- Focused on Game Theory

2002: B.Sc. in Mathematics and Computer Science, Technion, Haifa
- Graduated Cum Laude

Skills:

- Programming Languages: Python, R, C++, Java
- Machine Learning Frameworks: TensorFlow, PyTorch, Scikit-learn
- Data Analysis Tools: Pandas, NumPy, SQL
- Other Technologies: Docker, Kubernetes, AWS, Git, Linux

Publications:

- Points with Large Quadrant Depth. JoCG 2(1): 128-143 (2011)
- Points with large quadrant depth. Symposium on Computational Geometry 2010: 358-364
- On a problem about quadrant depth. Comput. Geom. 43(6-7): 587-592 (2010)
- Points with large alphadepth. J. Comb. Theory, Ser. A 116(3): 747-755 (2009)
    """
    parsed_sections = parser.parse_cv_sections(cv_content)
    print(parsed_sections)


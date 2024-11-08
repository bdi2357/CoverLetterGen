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
import time
load_dotenv('.env', override=True)

import json
import logging

class CVParserAI:
    def __init__(self, client, model_name="gpt-4o-mini"):
        self.client = client
        self.model_name = model_name

    def get_response(self, prompt, history=None, temperature=0.01):
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

    def sanitize_response(self, response):
        """
        Sanitize the response to extract the valid JSON block.

        Args:
            response (str): The response from the model.

        Returns:
            str: The sanitized JSON string.
        """
        try:
            start = response.index('{')
            end = response.rindex('}') + 1
            return response[start:end]
        except ValueError as e:
            logging.error(f"Failed to sanitize response: {e}")
            return "{}"  # Return an empty JSON object if parsing fails

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

        Organize this content into structured sections in JSON format with the following fields:
        - "Name": (Name of the individual)
        - "Contact": (Contact information)
        - "LinkedIn": (LinkedIn profile link)
        - "Summary": (Professional summary)
        - "Work Experience": (Experience details)
        - "Education": (Education details)
        - "Skills": (Skills list)
        - "Projects": (Projects list)
        - "Publications": (Publications list)

        Return only a valid JSON dictionary with each section name as the key and the corresponding content as the value.
        """

        response = self.get_response(prompt, temperature=0.01)
        if response:
            sanitized_response = self.sanitize_response(response)
            try:
                parsed_response = json.loads(sanitized_response)
                if isinstance(parsed_response, dict):
                    return parsed_response
                else:
                    logging.warning("Response is not a valid dictionary.")
                    return {}
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error: {e}")
                return {}
        else:
            logging.error("No response received from the model.")
            return {}

# Example usage
if __name__ == "__main__":
    start = time.time()
    load_dotenv('.env', override=True)
    openai_api_key = os.getenv('OPENAI_API_KEY')

    # Set up OpenAI client
    client = OpenAI(api_key=openai_api_key)

    # Assume `openai` is the OpenAI client object initialized with your API key
    parser = CVParserAI(client)
    print("Initialization time is %0.2f" %(time.time() - start))
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
    cv_content2 ="""
    **Itay Ben-Dan**  
    Haarava 20, Herzliya, P.O. Box 5990, Herzliya, Israel 46100  
    Cell: +972544539284  
    Email: itaybd@gmail.com  
    LinkedIn: [itay-ben-dan](https://www.linkedin.com/in/itay-ben-dan-99b6041a/)  
    GitHub: [BDI2357](https://github.com/BDI2357)
    
    ---
    
    **Professional Summary**  
    Accomplished Full Stack AI and Machine Learning Engineer with over a decade of experience translating algorithmic trading strategies into robust, deployable code. My extensive background includes designing, coding, deploying, and optimizing strategies in options, futures, and crypto markets, complemented by expert knowledge in AI-driven analytics and NLP solutions.
    
    ---
    
    **Work Experience**
    
    **Algorithmic Trading & AI Solutions Consultant**  
    _2017-Present_  
    - Developed and deployed end-to-end algorithmic trading strategies, focusing on options selling, futures scalping, and crypto trading.
    - Conducted comprehensive backtesting and statistical analyses, enhancing strategy performance and robustness.
    - Led the integration of strategies into user-friendly interfaces for retail trading platforms.
    
    **Founder & Head of Research, Finzor Ltd.**  
    _2017-Present_  
    - Created scalable AI-powered trading systems, ensuring reliability and seamless integration.
    - Directed strategic initiatives from conception to execution, emphasizing user experience.
    
    **Principal Machine Learning Engineer, Palo Alto Networks**  
    _2016-2017_  
    - Utilized machine learning for enhanced cybersecurity, specializing in anomaly detection and threat identification.
    
    **Senior Quantitative Researcher, WorldQuant**  
    _2011-2015_  
    - Innovated quantitative algorithms with rigorous backtesting across diverse asset classes, achieving top performance metrics.
    
    ---
    
    **Education**  
    - **Ph.D. in Mathematics** (Discrete Geometry), Technion, Haifa, 2009  
    - **M.Sc. in Mathematics** (Game Theory), Technion, Haifa, 2004    
    - **B.Sc. in Mathematics and Computer Science**, Technion, Haifa, 2002, Cum Laude  
    
    ---
    
    **Technical Skills**  
    - **Programming Languages:** Python, R, C++, Java  
    - **Machine Learning Frameworks:** TensorFlow, PyTorch, Scikit-learn  
    - **NLP & Data Processing:** Pandas, NumPy, SQL  
    - **Deployment & DevOps:** Docker, Kubernetes, AWS  
    - **Trading Tools:** Backtrader, QuantConnect, PyAlgoTrade  
    
    ---
    
    **Projects**
    
    **AI Invoice Reconciliation System**  
    - Developed AI models for automating invoice reconciliation, improving data consistency across financial systems.
    - Implemented NLP solutions for extracting critical data from invoices.
    
    **Algorithmic Trading Deployment Platform**  
    - Created a deployment platform for retail clients, focused on accessibility and user engagement.
    
    **TreeModelVis**  
    - Developed a tool to visualize and interpret decision paths in tree-based models.  
    - [GitHub Repository](https://github.com/bdi2357/TreeModelVis)
    
    ---
    
    **Publications**  
    - Authored articles on computational geometry enhancing analytical methodologies in scientific journals.
    
    ---
    
    **Contact**  
    - **Email:** itaybd@gmail.com  
    - **Phone:** +972544539284  
    
    ---
    
    """
    print("HERE2")
    parsed_sections = parser.parse_cv_sections(cv_content2)
    print(parsed_sections)
    print(parsed_sections.keys())
    print("total time is %0.2f" %(time.time() - start))



import os
from openai import OpenAI
from dotenv import load_dotenv
from data_handling import load_and_extract_text
# Load environment variables from .env file
load_dotenv('.env', override=True)
openai_api_key = os.getenv('OPENAI_API_KEY')

# Set up the OpenAI client
client = OpenAI(api_key=openai_api_key)


def get_llm_response(prompt):
    """
    Function to get a response from OpenAI GPT model using the provided prompt.
    """
    try:
        if not isinstance(prompt, str):
            raise ValueError("Input must be a string enclosed in quotes.")
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant specialized in extracting information from CVs."
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.0
        )
        response = completion.choices[0].message.content
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def extract_information_from_cv(cv_text):
    """
    Extracts applicant's name, email, phone, address, GitHub, LinkedIn, and skills from the provided CV text.

    Args:
        cv_text (str): The full text of the CV.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    prompt = f"""
    Extract the following information from the given CV text:
    - Full name of the applicant
    - Email address
    - Phone number
    - Physical address
    - GitHub profile (if present)
    - LinkedIn profile (if present)
    - Key skills (list any technical skills, programming languages, tools, or expertise areas)
    - Homepage (if present)
    - Projects (if present)
    - Publications (if present)

    If any of the information is missing, simply omit it from the result. Provide the output in a structured format.

    Here is the CV text:
    \"{cv_text}\"
    """

    response = get_llm_response(prompt)

    if response:
        # Parse the response into a dictionary (assume that the GPT response is structured)
        extracted_info = parse_extracted_info(response)
        for key, item in extracted_info.items():
            print(key,"\n",item)
        return extracted_info
    else:
        return {}
def parse_extracted_info(response):
    """
    Parses the structured response from GPT into a dictionary for easy access to the fields.

    Args:
        response (str): The text response from GPT.

    Returns:
        dict: A dictionary containing the extracted information.
    """
    # Initialize an empty dictionary to hold the extracted information
    info_dict = {}

    # Split the response by lines
    lines = response.split("\n")

    # Loop through lines and parse key-value pairs (Name, Email, etc.)
    for line in lines:
        if line.strip():  # Skip empty lines
            key_value = line.split(":")
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].strip()
                info_dict[key] = value

    return info_dict


def extract_and_print_cv_info(cv_text):
    """
    Extracts information from the CV and prints it in a readable format.

    Args:
        cv_text (str): The full text of the CV.
    """
    info = extract_information_from_cv(cv_text)

    # Print the extracted information
    print("Extracted Information:")
    for key, value in info.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    # Example usage: Replace this with your actual CV text
    sample_cv_text = """
    Itay Ben-Dan
    Haarava 20, Herzliya
    P. O. Box 5990, Herzliya, Israel 46100
    Cellular: +972544539284
    Email: itaybd@gmail.com
    LinkedIn: linkedin.com/in/itaybendan
    GitHub: github.com/itaybendan
    Professional Summary...
    """

    # Extract and print the CV information
    #extract_and_print_cv_info(sample_cv_text)
    sample_pdf_path = os.path.join("Data", 'CV_GPT_N.pdf')
    original_cv = load_and_extract_text(sample_pdf_path)
    extract_and_print_cv_info(original_cv)

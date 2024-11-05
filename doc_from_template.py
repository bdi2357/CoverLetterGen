from docxtpl import DocxTemplate
import os,re
from docxtpl import DocxTemplate
from docx_generate import load_cv_sections_from_file
# Load the Word document template
import ast

def is_python_object(input_str):
    """
    Determines if a given string represents a Python object (e.g., a dictionary or list)
    that can be parsed using `ast.literal_eval`.

    Args:
        input_str (str): The input string to evaluate.

    Returns:
        bool: True if the string represents a Python object, False otherwise.
    """
    try:
        # Try to parse the string with `ast.literal_eval`, which safely evaluates literals
        parsed_value = ast.literal_eval(input_str)
        # If parsing succeeds, it means `input_str` is likely a Python object
        return True
    except (ValueError, SyntaxError):
        # If parsing fails, it's likely a regular string and not a Python object
        return False

def parse_input(input_str):
    """
    Parses the input string. If it represents a Python object, evaluates it to return the object.
    If it is a plain string, returns it as-is.

    Args:
        input_str (str): The input string to parse.

    Returns:
        any: The evaluated Python object if `input_str` is a Python object; otherwise, the original string.
    """
    if is_python_object(input_str):
        try:
            # Use `ast.literal_eval` to safely evaluate the Python object
            return ast.literal_eval(input_str)
        except (ValueError, SyntaxError) as e:
            print(f"Failed to evaluate as Python object: {e}")
            return input_str  # Return the original string if evaluation fails
    else:
        # Return as-is if it's not a Python object
        return input_str
def flatten_section(section):
    """
    Flattens a section of the CV content into a string format, handling nested dictionaries and lists.
    """
    if isinstance(section, dict):
        # If it's a dictionary, format each key-value pair
        return "\n".join(f"{k}: {flatten_section(v)}" for k, v in section.items())
    elif isinstance(section, list):
        # If it's a list, format each item in the list on a new line
        return "\n".join(flatten_section(item) for item in section)
    else:
        # If it's already a string, return it as is
        return str(section)
def flatten_dict(sections):
    return {key: flatten_section(value) for key, value in sections.items()}


def format_section(section_data):
    """
    Recursively format section data to a readable string. Handles dictionaries, lists, and regular strings.
    """
    if not section_data:
        return ""

    # Handle list of dictionaries, like experience or education entries
    if isinstance(section_data, list):
        formatted_items = []
        for item in section_data:
            if isinstance(item, dict):
                # Detect if it's an "Experience" or "Education" type entry by checking expected keys
                if "Position" in item and "Duration" in item:
                    # Format "Experience" entries
                    position = item.get("Position", "")
                    duration = item.get("Duration", "")
                    responsibilities = item.get("Responsibilities", [])

                    # Format position and duration
                    formatted_entry = f"{duration}: {position}"

                    # Add each responsibility as a bullet point
                    if responsibilities:
                        responsibility_text = "\n".join([f" ● {resp}" for resp in responsibilities])
                        formatted_entry += f"\n{responsibility_text}"

                    formatted_items.append(formatted_entry)

                elif "Degree" in item and "Institution" in item:
                    # Format "Education" entries
                    degree = item.get("Degree", "")
                    institution = item.get("Institution", "")
                    year = item.get("Year", "")

                    # Format degree, institution, and year
                    formatted_entry = f"{year}: {degree}, {institution}"
                    formatted_items.append(formatted_entry)

                else:
                    # General case for other types of dictionaries
                    formatted_entry = "\n".join([f"{k}: {v}" for k, v in item.items()])
                    formatted_items.append(formatted_entry)
            else:
                # For other list items, add them directly
                formatted_items.append(f" ● {item}")
        return "\n\n".join(formatted_items)

    # For dictionaries, format each key-value pair
    elif isinstance(section_data, dict):
        formatted_items = []
        for key, value in section_data.items():
            if isinstance(value, list):
                # Format lists with bullets
                formatted_value = "\n".join([f"  - {v}" for v in value])
                formatted_items.append(f"{key}:\n{formatted_value}")
            else:
                # Add key-value pairs normally
                formatted_items.append(f"{key}: {value}")
        return "\n".join(formatted_items)

    # For strings and other types, return as is
    return str(section_data)
def generate_cv(file_name, sections, template_path):
    """
    Generate and save a CV document based on structured content sections.

    Args:
        file_name (str): Destination path for the generated CV.
        sections (dict): Extracted sections of the CV, e.g., {"Name": ..., "Experience": ...}
        template_path (str): Path to the template file.
    """
    doc = DocxTemplate(template_path)

    # Prepare data for the template
    data = {}
    for section, content in sections.items():
        formatted_content = format_section(parse_input(content))
        if section == "Experience":
            print("content\n", formatted_content)
        if section == "Education":
            print("Education\n", formatted_content)
            print("Education\n", content)
        if formatted_content:  # Only add non-empty sections
            data[section] = formatted_content

    # Render and save the document
    doc.render(data)
    output_path = f"{file_name}.docx"
    doc.save(output_path)
    print(f"Generated CV document saved as {output_path}")

if __name__ == "__main__":
    #template_path = os.path.join("Templates", "ClassicResume.docx")
    template_path = os.path.join("Templates", "StylishResume.docx")
    output_path = "Improved_CV_Final.docx"

    sections = load_cv_sections_from_file("Output\Sections\CV_N.txt")
    print(sections)
    sections = flatten_dict(sections)
    print("*"*55)
    print(sections)
    print(sections.keys())
    expr = [k for k in sections.keys()  if k.lower().find("experience")> -1]
    if len(expr)>0:
        sections["Experience"] = sections.pop(expr[0])
    print("=" * 55)
    print(sections)
    if not os.path.exists(template_path):
        print(f"Template file not found at: {template_path}")
    else:
        generate_cv("Itay_Ben_Dan_CV_Final10", sections, template_path)

    experience_data = [
        {
            'Position': 'Machine Learning and Data Science Consultant',
            'Duration': '2017-Present',
            'Responsibilities': [
                'Automated invoice reconciliation using AI, enhancing accuracy in financial operations.',
                'Unified varied data sources into standardized formats, boosting processing efficiency.',
                'Developed NLP solutions for extracting insights from unstructured financial data.'
            ]
        },
        {
            'Position': 'Founder and Head of Research, Finzor Ltd.',
            'Duration': '2017-Present',
            'Responsibilities': [
                'Delivered innovative portfolio management solutions, revolutionizing investment analysis.',
                'Led a high-performing team in creating scalable, production-ready software tools.'
            ]
        },
        {
            'Position': 'Principal Machine Learning Engineer, Palo Alto Networks',
            'Duration': '2016-2017',
            'Responsibilities': [
                'Enhanced malware analysis with advanced ML models, refining adaptive security measures.',
                'Innovated dynamic solutions for real-time updates in anti-malware systems.'
            ]
        },
        {
            'Position': 'Senior Data Scientist, SparkBeyond',
            'Duration': '2015-2016',
            'Responsibilities': [
                'Developed predictive analytics solutions for time series analysis in finance.',
                'Implemented automatic feature generation, improving model efficiency.'
            ]
        }
    ]

    # Convert the experience section to a readable format
    formatted_experience = format_section(experience_data)
    print(formatted_experience)
    formatted_experience = format_section(eval(sections["Experience"]))
    print("="*60)
    print(formatted_experience)
    for k in sections.keys():
        print(k,type(sections[k]))




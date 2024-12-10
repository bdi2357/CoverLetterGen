from docxtpl import DocxTemplate
import os,re
from docxtpl import DocxTemplate
#from docx_generate import load_cv_sections_from_file
# Load the Word document template

def load_cv_sections_from_file(file_path):
    """
    Loads CV sections from a structured text file back into a dictionary,
    and deserializes nested structures like dictionaries or lists.

    Args:
        file_path (str): The path of the file containing the CV sections.

    Returns:
        dict: A dictionary with section names as keys and section content as values.
    """
    sections = {}
    current_section = None
    content = []

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Check if the line is a section header (e.g., "Name:", "Skills:")
            if line.strip().endswith(":"):
                # Save previous section if any
                if current_section:
                    raw_content = "\n".join(content).strip()
                    sections[current_section] = parse_section(raw_content)

                # Start a new section
                current_section = line.strip()[:-1]  # Remove colon
                content = []
            else:
                # Add lines to the current section content
                content.append(line.strip())

        # Save the last section
        if current_section:
            raw_content = "\n".join(content).strip()
            sections[current_section] = parse_section(raw_content)

    return sections


def parse_section(content):
    """
    Attempts to parse a section as a Python literal (e.g., dict, list).
    Falls back to returning the raw string if parsing fails.

    Args:
        content (str): The section content.

    Returns:
        object: Parsed Python object (e.g., dict, list) or raw string.
    """
    try:
        # Try to parse as a Python literal (e.g., dict, list)
        return ast.literal_eval(content)
    except (ValueError, SyntaxError):
        # If parsing fails, return the raw string
        return content


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


import ast
import re

def flatten_section(section):
    """
    Flattens a section of the CV content into a string format, handling nested dictionaries and lists,
    even when they are improperly serialized as strings.
    """
    if isinstance(section, str):
        # Attempt to parse as dict or list if it resembles one
        try:
            # If it is a valid Python literal (e.g., dict, list)
            section = ast.literal_eval(section)
        except (ValueError, SyntaxError):
            # If it resembles a flattened dict-like structure, attempt to reparse manually
            if ':' in section and '\n' in section:
                section = parse_as_dict(section)
            else:
                return section

    if isinstance(section, dict):
        # If it's a dictionary, format each key-value pair
        return "\n".join(f"{k}: {flatten_section(v)}" for k, v in section.items())
    elif isinstance(section, list):
        # If it's a list, format each item in the list on a new line
        return "\n".join(flatten_section(item) for item in section)
    else:
        # If it's already a string or another basic type, return it as is
        return str(section)

def parse_as_dict(text):
    """
    Parses a text block resembling a flattened dictionary into an actual dictionary.
    """
    parsed_dict = {}
    lines = text.split('\n')
    current_key = None
    for line in lines:
        if ':' in line:
            # Extract key-value pairs
            key, value = line.split(':', 1)
            current_key = key.strip()
            parsed_dict[current_key] = value.strip()
        elif current_key:
            # Handle multiline values
            parsed_dict[current_key] += ' ' + line.strip()
    return parsed_dict

def flatten_dict(sections):
    """
    Flattens the entire dictionary of sections.
    """
    return {key: flatten_section(value) for key, value in sections.items()}

"""
def format_section(section_data):
    #Recursively format section data to a readable string. Handles dictionaries, lists, and regular strings.
    
    if not section_data:
        return ""
    print("In format section")
    # Handle list of dictionaries, like experience or education entries
    if isinstance(section_data, list):
        formatted_items = []
        for item in section_data:
            if isinstance(item, dict):
                print("in dict")
                # Detect if it's an "Experience" or "Education" type entry by checking expected keys
                if "Position" in item and "Duration" in item:
                    print("Im position")
                    # Format "Experience" entries
                    position = item.get("Position", "")
                    duration = item.get("Duration", "")
                    responsibilities = item.get("Responsibilities", [])

                    # Format position and duration
                    formatted_entry = f"{duration}: {position}"

                    # Add each responsibility as a bullet point
                    if responsibilities:
                        print("HERE2")
                        print("responsibilities", len(responsibilities))
                        formatted_entry += "\n" + "\n".join(f"  - {resp}" for resp in responsibilities)
                        
                        #responsibility_text = "\n".join([f" ● {resp}" for resp in responsibilities])
                        #formatted_entry += f"\n{responsibility_text}"
                        

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
                    print("no position")
                    print(item)
                    print(formatted_entry)
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
"""
def format_section(section_data):
    """
    Recursively format section data to a readable string. Passes raw lists and dicts for Jinja2.
    """

    if not section_data:
        return ""

    # Preserve lists and dictionaries for Jinja2
    if isinstance(section_data, list):
        return section_data  # Pass raw for Jinja2

    elif isinstance(section_data, dict):
        return section_data  # Pass raw for Jinja2

    # Fallback: Plain string for non-iterable
    return str(section_data)

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
def generate_cv(file_name, sections, template_path):
    """
    Generate and save a CV document with properly structured data for Jinja2 templates.
    """
    doc = DocxTemplate(template_path)

    # Prepare data for template
    data = {}
    for section, content in sections.items():
        parsed_content = parse_input(content)  # Parse raw data
        formatted_content = format_section(parsed_content)  # Format or preserve raw
        data[section] = formatted_content
    # Render and save
    doc.render(data)
    output_path = f"{file_name}.docx"
    doc.save(output_path)
    print(f"Generated CV document saved as {output_path}")

def sections2cv(template_path,sections_path,dest_cv_path):
    if not os.path.exists(template_path):
        print(f"sections file not found at: {sections_path}")
    else:
        sections = load_cv_sections_from_file(sections_path)
    expr = [k for k in sections.keys() if k.lower().find("experience") > -1]
    if len(expr) > 0:
        sections["Experience"] = sections.pop(expr[0])
    if not os.path.exists(template_path):
        print(f"Template file not found at: {template_path}")
    else:
        generate_cv(dest_cv_path, sections, template_path)




if __name__ == "__main__":

    template_path = os.path.join("Templates", "Final_Revised_Template_V2.docx")
    #sections = load_cv_sections_from_file("Output\Sections\CV_N.txt")
    sections_path =  os.path.join("Output","Sections","Start_io_DataScientist_sections.txt")
    dest_cv_path = os.path.join("Output", "CV", "CV_Start_io_DataScientist")
    sections2cv(template_path, sections_path, dest_cv_path)

    sections_cover_letter = {'Name': 'Itay Ben-Dan', 'Contact': {'Cellular': '+972544539284', 'Email': 'itaybd@gmail.com'}, 'LinkedIn': 'https://www.linkedin.com/in/itay-ben-dan-99b6041a/', 'GitHub': 'https://github.com/BDI2357', 'CoverLetter': 'Dear Hiring Manager,\n\nAs a Machine Learning and Data Science Consultant with a strong background in AI applications for the finance industry, I have developed advanced models, such as a financial transaction analysis system using large language models, to automate and optimize complex processes. My proficiency in Python, TensorFlow, and NLP techniques, combined with experience in unifying data across various sources, aligns well with your requirement for automating invoice reconciliation. I am eager to contribute my skills in building intelligent systems and improving financial workflows at your company during UK working hours.\n\nBest regards,\nItay Ben-Dan'}
    dest_cover_letter_path = os.path.join("Output", "CoverLetter", "CoverLetterTest")
    template_path = os.path.join("Templates", "StylishCoverLetter.docx")
    generate_cv(dest_cover_letter_path,sections_cover_letter,template_path)


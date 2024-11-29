from jinja2 import Template

def parse_skills_section(skills_raw):
    """
    Parses a raw skills section into a dictionary format.
    Args:
        skills_raw (list): The raw skills section content.
    Returns:
        dict: A dictionary with categories as keys and lists of skills as values.
    """
    skills_dict = {}
    current_category = None

    for line in skills_raw:
        if line.endswith(":"):  # Indicates a new category
            current_category = line[:-1].strip()
            skills_dict[current_category] = []
        elif current_category and line.startswith("●"):
            skill = line[1:].strip()  # Remove the bullet and strip whitespace
            skills_dict[current_category].append(skill)
        elif current_category:
            skills_dict[current_category][-1] += f" {line.strip()}"  # Append continuation lines

    return skills_dict

def format_combined_cv_with_prompt(structured_cv):
    """
    Formats a structured CV dictionary into a professional CV using a Jinja2 template.
    Args:
        structured_cv (dict): A dictionary containing structured CV data.
    Returns:
        str: The formatted CV as a string.
    """
    # Ensure the Skills section is correctly parsed into a dictionary
    if isinstance(structured_cv.get("Skills"), list):
        structured_cv["Skills"] = parse_skills_section(structured_cv["Skills"])
    print("=====")
    for key in structured_cv.keys():
        print(key)
        print(">"*88)
        print(structured_cv[key])
    prompt_template = """
{{Name}}  
Contact Information  
 Phone: {{Contact.Cellular}} | Email: {{Contact.Email}}  
 LinkedIn: {{LinkedIn}}{% if GitHub %}  
 GitHub: {{GitHub}}{% endif %}  

Summary  
{{Summary}}  

Work Experience  
{% for job in Experience %}  
• {{job.Title}} | ({{job.Duration}})  
{% for resp in job.Responsibilities %}  
 {{resp}}  
{% endfor %}  
{% endfor %}  

Skills  
{% for category, category_skills in Skills.items() %}  
• {{category}}: {% for skill in category_skills %} {{skill}} {% endfor %}  
{% endfor %}  

Education  
{% for edu in Education %}  
• {{edu.Degree}} | {{edu.Institution}} | {{edu.Year}} {% if edu.Thesis %} | {{edu.Thesis}} {% endif %}  
{% endfor %}  

Projects  
{% for project in Projects %}  
• {{project.Title}}: {{project.Description}}  
{% if project.Link %}  
 Link: {{project.Link}}  
{% endif %}  
{% endfor %}  

Publications  
{% for publication in Publications %}  
• {{publication}}  
{% endfor %}
    """

    try:
        # Load and render the template
        template = Template(prompt_template)
        formatted_cv = template.render(**structured_cv)
        return formatted_cv.strip()
    except Exception as e:
        return f"Error generating CV: {str(e)}"

if __name__ == "__main__":
    # Example usage
    structured_cv_example = {
        "Name": "John Doe",
        "Contact": {"Cellular": "+1234567890", "Email": "john.doe@example.com"},
        "LinkedIn": "https://linkedin.com/in/johndoe",
        "GitHub": "https://github.com/johndoe",
        "Summary": "Experienced data scientist with a strong focus on machine learning and AI applications.",
        "Experience": [
            {
                "Title": "Senior Data Scientist",
                "Duration": "2020-Present",
                "Responsibilities": [
                    "Developed predictive models for customer behavior analysis.",
                    "Implemented automated data pipelines for large-scale data processing.",
                ],
            },
            {
                "Title": "Data Scientist",
                "Duration": "2017-2020",
                "Responsibilities": [
                    "Built machine learning models for fraud detection.",
                    "Collaborated with cross-functional teams to deliver end-to-end data solutions.",
                ],
            },
        ],
        "Skills": {
            "Programming": ["Python", "R", "SQL"],
            "Machine Learning": ["Supervised Learning", "Unsupervised Learning", "Deep Learning"],
        },
        "Education": [
            {"Degree": "M.Sc. in Data Science", "Institution": "University of Example", "Year": "2017", "Thesis": ""},
            {"Degree": "B.Sc. in Computer Science", "Institution": "Example College", "Year": "2015", "Thesis": ""},
        ],
        "Projects": [
            {
                "Title": "Customer Churn Prediction",
                "Description": "Developed a machine learning model to predict customer churn with 90% accuracy.",
                "Link": "https://github.com/johndoe/churn-prediction",
            },
            {
                "Title": "Image Classification",
                "Description": "Created a deep learning pipeline for multi-class image classification.",
                "Link": "",
            },
        ],
        "Publications": [
            "Doe J., et al. (2020). Predicting Customer Behavior with ML. Journal of Data Science.",
            "Doe J., et al. (2019). Advances in Deep Learning for Image Classification. Data Conference Proceedings.",
        ],
    }

    # Generate the CV
    formatted_cv = format_combined_cv_with_prompt(structured_cv_example)
    print(formatted_cv)

import re
import json
import os
import re
import os
import json
#from docxtpl import DocxTemplate
import re
import os
import json


# from docxtpl import DocxTemplate

def parse_cv_critique_to_dict(text,title, name):
    """
    Parses CV critique text into a dictionary format.

    Args:
        text (str): The critique text in a structured format.

    Returns:
        dict: A dictionary structured for the CV critique.
    """
    critique_dict = {
        "title": title,
        "name" : name,
        "sections": [],
        "actionable_feedback": []
    }

    section_pattern = r"\*\*(\d+\.\s.*)\*\*"
    feedback_pattern = r"\*\*Actionable Feedback\*?\*?:?\*?\*?\s*([\s\S]+?)(?=\n\n|$)"

    print("Splitting text into sections using section pattern...")
    sections = re.split(section_pattern, text)
    print(f"Sections found: {len(sections) // 2}")

    for i in range(1, len(sections), 2):
        section_title = sections[i].strip()
        content_block = sections[i + 1].strip()

        print(f"Processing section: {section_title}")
        grade_match = re.search(r"Grade:\s*([\d.]+)#", content_block)
        grade = grade_match.group(1) if grade_match else "N/A"
        print(f"Grade extracted: {grade}")

        content_string = "\n".join(
            [line.strip() for line in content_block.splitlines() if line.strip() and not line.startswith("- Grade")])
        print(f"Content string created.")

        critique_dict["sections"].append({
            "Title": section_title,
            "Grade": grade,
            "Content": content_string
        })

    print("Searching for actionable feedback...")
    feedback_match = re.search(feedback_pattern, text, re.DOTALL)
    if feedback_match:
        feedback_lines = [line.strip("- ").strip() for line in feedback_match.group(1).splitlines() if
                          line.strip() and line.startswith("-")]
        critique_dict["actionable_feedback"] = feedback_lines
        print("Actionable feedback found.")
    else:
        print("No actionable feedback found.")

    print("Parsing complete.")
    return critique_dict


def generate_document_from_template(parsed_data, template_path, output_path):
    """
    Generates a Word document using the parsed critique data and a template.

    Args:
        parsed_data (dict): The parsed critique data.
        template_path (str): Path to the Word template.
        output_path (str): Path to save the generated Word document.
    """
    print("Loading template...")
    template = DocxTemplate(template_path)

    print("Rendering template with parsed data...")
    render_data = {
        "title": parsed_data["title"],
        "Sections": [
            {"Title": section["Title"], "Grade": section["Grade"], "Content": section["Content"]}
            for section in parsed_data["sections"]
        ],
        "actionable_feedback": parsed_data["actionable_feedback"]
    }

    template.render(render_data)
    print("Saving generated document...")
    template.save(output_path)
    print(f"Document saved to: {output_path}")
def parse_cover_letter_critique_to_dict(text,title,name):
    """
    Parses cover letter critique text into a dictionary format.

    Args:
        text (str): The critique text in a structured format.

    Returns:
        dict: A dictionary structured for the cover letter critique.
    """
    critique_dict = {
        "title": title,
        "name" : name,
        "sections": []
    }

    section_pattern = r"\*\*#(.*?)Grade:\s*(\d+)#\*\*\s*(.*?)\n(?=(\*\*#|$))"

    print("Finding sections using section pattern...")
    matches = re.finditer(section_pattern, text, re.DOTALL)

    for match in matches:
        section_title = match.group(1).strip()
        grade = match.group(2).strip()
        content_block = match.group(3).strip()

        print(f"Processing section: {section_title}")
        print(f"Grade extracted: {grade}")

        content_string = "\n".join([line.strip() for line in content_block.splitlines() if line.strip()])
        print(f"Content string created.")

        critique_dict["sections"].append({
            "Title": section_title,
            "Grade": grade,
            "Content": content_string
        })

    print("Parsing complete.")
    return critique_dict


def process_cv_critique_files(directory):
    """
    Process all CV critique text files in a directory and parse them.

    Args:
        directory (str): Path to the directory containing CV critique text files.
    """
    for filename in os.listdir(directory):
        if filename.endswith("_crtitque.txt"):
            filepath = os.path.join(directory, filename)
            print(f"Processing file: {filename}")

            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read()

            parsed_data = parse_cv_critique_to_dict(content,"","")

            output_filename = filename.replace(".txt", "_parsed.json")
            output_filepath = os.path.join(directory, output_filename)

            with open(output_filepath, "w", encoding="utf-8") as output_file:
                json.dump(parsed_data, output_file, indent=4)

            print(f"Parsed data saved to: {output_filepath}\n")


# Example usage
# process_cv_critique_files("C:\Users\itayb\PycharmProjects\CoverLetterGen\Output\CritiqueFinal")

# template_path = "/mnt/data/Critique_Template_n1.docx"
# output_document_path = "/mnt/data/Generated_CV_Critique_Template_Filled.docx"
# parsed_data = parse_cv_critique_to_dict(text2)
# generate_document_from_template(parsed_data, template_path, output_document_path)

text = """**1. Relevance to the Job**  
- The CV effectively highlights skills and experiences directly aligned with the job description, such as deep learning, AI, and auction optimization. The candidate's experience in programmatic advertising and RTB algorithms is particularly relevant to Rise's focus on AI-powered auction optimization.  
- Grade: **#Relevance to the Job Grade: 9##**  

**2. Clarity and Structure**  
- The CV is well-organized and easy to read, with clear sections and logical flow. The use of bullet points enhances readability, making it easy to identify key achievements and responsibilities.  
- Grade: **#Clarity and Structure Grade: 9##**  

**3. Skills Presentation**  
- Technical skills are well-highlighted, with relevant programming languages and ML frameworks clearly listed. The addition of a 'Soft Skills' section improves the presentation by emphasizing teamwork and mentoring abilities.  
- Grade: **#Skills Presentation Grade: 9##**  

**4. Professionalism**  
- The CV maintains a professional tone and is free of grammatical errors. The language is clear and concise, with appropriate formatting throughout.  
- Grade: **#Professionalism Grade: 9##**  

**5. Overall Impression**  
- The CV presents the candidate as a strong fit for the role, with relevant experience and skills. The emphasis on deep learning, AI, and auction optimization aligns well with the job requirements. The inclusion of both technical and soft skills enhances the overall presentation.  
- Grade: **#Overall Grade: 9.0#**  

**Actionable Feedback**:  
- Consider providing more specific examples of how the candidate has led innovation initiatives or stayed ahead of technological advancements in deep learning and AI.  
- Highlight any quantifiable achievements or impacts in previous roles to further strengthen the CV.:
"""

text2 = """**1. Relevance to the Job**  
- The CV effectively emphasizes skills and experiences directly aligned with the job description, such as algorithmic trading, machine learning, and optimization. The candidate's Ph.D. background and experience in developing trading strategies are highly relevant to DRW's requirements.  
- Grade: **#Relevance to the Job Grade: 9##**

**2. Clarity and Structure**  
- The CV is easy to read, well-organized, and logically structured. The layout enhances readability with clear sections for contact information, summary, work experience, skills, education, projects, and publications.  
- Grade: **#Clarity and Structure Grade: 9##**

**3. Skills Presentation**  
- The candidate's technical and soft skills are adequately highlighted and relevant. The CV effectively links skills to specific achievements, demonstrating practical application. However, further emphasis on soft skills in context could enhance this section.  
- Grade: **#Skills Presentation Grade: 8##**

**4. Professionalism**  
- The CV is professional in tone, free of errors, and written in clear language. The formatting is consistent, and the tone is appropriate for the role.  
- Grade: **#Professionalism Grade: 9##**

**5. Overall Impression**  
- The CV presents the candidate as a strong fit for the role, with a solid technical background and relevant project experience. Key strengths include alignment with job requirements and demonstration of relevant skills. The main area for improvement is the explicit connection of soft skills to specific achievements.  
- Grade: **#Overall Grade: 8.8#**

**Actionable Feedback:**
- Consider providing more context or examples of how soft skills have been applied in past roles to enhance the skills presentation.
- Ensure that all sections are consistently formatted and that any additional information is directly relevant to the job description.:
"""
text3 = """ **1. Relevance to the Job**  
     - The CV effectively highlights the candidate's experience in machine learning, data science, and software development, which aligns well with the job description. The emphasis on NLP and GEN AI is a significant improvement, directly addressing the job's focus on legal tech and AI. However, more explicit examples of working with legal tech or justice-related projects could further enhance relevance.  
     - Grade: **#Relevance to the Job Grade: 8#**

     **2. Clarity and Structure**  
     - The CV is well-organized with clear sections and a logical flow. The professional summary is concise and focused, and the use of bullet points aids readability. The separation of sections is clear, enhancing the overall structure.  
     - Grade: **#Clarity and Structure Grade: 9#**

     **3. Skills Presentation**  
     - The CV presents a comprehensive list of technical skills relevant to the role, including programming languages, ML frameworks, and cloud technologies. The addition of soft skills such as communication and problem-solving is beneficial. However, linking these skills to specific achievements or projects could further strengthen this section.  
     - Grade: **#Skills Presentation Grade: 8#**

     **4. Professionalism**  
     - The CV maintains a professional tone and is free of grammatical errors. The formatting is consistent, and unnecessary repetitions have been removed. The language is clear and concise, contributing to a professional presentation.  
     - Grade: **#Professionalism Grade: 9#**

     **5. Overall Impression**  
     - The CV presents the candidate as a strong fit for the role, with relevant experience and skills in machine learning and AI. The improvements made in emphasizing NLP and GEN AI experience are notable. Further detailing specific achievements related to legal tech could enhance the overall impression.  
     - Grade: **#Overall Grade: 8#**

     **Actionable Feedback**:  
     - Include specific examples or projects related to legal tech or justice system innovations to further align with the job description.
     - Link technical and soft skills to concrete achievements or projects to demonstrate their practical application.
     - Consider adding any relevant certifications or additional training in NLP or GEN AI to bolster qualifications"""
#print(parse_cv_critique_to_dict(text3))

if __name__ == "__main__":
    # Example text input
    example_text = """
    AI Critique Response: **#Relevance to the Job Grade: 9#**
    The cover letter is highly relevant to the job, highlighting key skills and experiences aligned with the AI Developer role. It mentions expertise in Python, ML frameworks, NLP techniques, and financial transaction analysis, directly matching the job requirements. A minor improvement could include explicitly mentioning familiarity with ERP software or accounting principles.
    
    **#Form and Structure Grade: 8#**
    The cover letter is concise and well-organized, with a clear introduction, relevant experience, and a closing statement. It could improve by including specific references to the company or more tailored examples of past work related to invoice reconciliation.
    
    **#Reliability Grade: 9#**
    The letter appears reliable, with claims supported by detailed professional experience in the CV. The background in developing AI solutions, particularly in finance, illustrates expertise in relevant models and tools. Enhancing reliability could involve briefly mentioning notable achievements or impacts from past projects.
    
    **#Professional Matching Grade: 9#**
    The candidate's qualifications and experience strongly match the professional requirements of the role. A PhD in Mathematics and extensive work in AI applications fit the specialized nature of the position. Minor enhancements could include a direct mention of experience with data privacy practices which align with job expectations.
    
    **#Overall Grade: 9#**
    The cover letter effectively communicates qualifications and suitability for the AI Developer role, demonstrating relevant skills and experience. Key strengths include its alignment with job requirements and clear expression of availability. A slightly more personalized touch, specific references to the company, and mention of data privacy experience could bring further impact.
    
    Iteration 1, Grade: 9.0, Cumulative Reward: 9.0
    """



    # Parse the example text
    parsed_dict = parse_cv_critique_to_dict(example_text, "cv_critique", "Itay Ben-Dan")

    # Display the resulting dictionary


    print(json.dumps(parsed_dict, indent=4))

    os.listdir()

    #process_critique_files(os.path.join("Output","CritiqueFinal"))

    text = """ **1. Relevance to the Job**  
     - The CV effectively highlights the candidate's experience in machine learning, data science, and software development, which aligns well with the job description. The emphasis on NLP and GEN AI is a significant improvement, directly addressing the job's focus on legal tech and AI. However, more explicit examples of working with legal tech or justice-related projects could further enhance relevance.  
     - Grade: **#Relevance to the Job Grade: 8#**
    
     **2. Clarity and Structure**  
     - The CV is well-organized with clear sections and a logical flow. The professional summary is concise and focused, and the use of bullet points aids readability. The separation of sections is clear, enhancing the overall structure.  
     - Grade: **#Clarity and Structure Grade: 9#**
    
     **3. Skills Presentation**  
     - The CV presents a comprehensive list of technical skills relevant to the role, including programming languages, ML frameworks, and cloud technologies. The addition of soft skills such as communication and problem-solving is beneficial. However, linking these skills to specific achievements or projects could further strengthen this section.  
     - Grade: **#Skills Presentation Grade: 8#**
    
     **4. Professionalism**  
     - The CV maintains a professional tone and is free of grammatical errors. The formatting is consistent, and unnecessary repetitions have been removed. The language is clear and concise, contributing to a professional presentation.  
     - Grade: **#Professionalism Grade: 9#**
    
     **5. Overall Impression**  
     - The CV presents the candidate as a strong fit for the role, with relevant experience and skills in machine learning and AI. The improvements made in emphasizing NLP and GEN AI experience are notable. Further detailing specific achievements related to legal tech could enhance the overall impression.  
     - Grade: **#Overall Grade: 8#**
    
     **Actionable Feedback**:  
     - Include specific examples or projects related to legal tech or justice system innovations to further align with the job description.
     - Link technical and soft skills to concrete achievements or projects to demonstrate their practical application.
     - Consider adding any relevant certifications or additional training in NLP or GEN AI to bolster qualifications"""
    print(parse_cv_critique_to_dict(text,"",""))

    process_cv_critique_files(os.path.join("Output","CritiqueFinal"))

from docxtpl import DocxTemplate
import os,re
from docxtpl import DocxTemplate

# Load the Word document template


def generate_cv(output_path, data, template_path):
    # Load the template
    doc = DocxTemplate(template_path)
    # Render the template with data
    doc.render(data)
    # Save the populated document
    doc.save(f"{output_path}.docx")

if __name__ == "__main__":
    template_path = os.path.join("Templates", "Basic professional resume.docx")
    output_path = "Improved_CV_Final.docx"

    cv_data = {
        "name": "Itay Ben-Dan",
        "email": "itaybd@gmail.com",
        "phone": "+972544539284",
        "website": "itaybd.example.com",
        "experience": "Machine Learning Consultant with extensive experience in AI...",
        "skills": "Python, TensorFlow, NLP, Data Analysis",
        "projects": "TreeModelVis, Financial Data Reconciliation",
        "education": "PhD in Mathematics, Technion, Haifa"
    }
    if not os.path.exists(template_path):
        print(f"Template file not found at: {template_path}")
    else:
        generate_cv("Itay_Ben_Dan_CV_Final", cv_data, template_path)
        print("Generated CV document saved as Itay_Ben_Dan_CV_Final.docx")



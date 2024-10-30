from docxtpl import DocxTemplate
import os,re
from docxtpl import DocxTemplate

# Load the Word document template
template_path = "Basic professional resume.docx"
output_path = "Improved_CV_Final.docx"
def generate_cv(data, output_path, template_path):
    
doc = DocxTemplate(template_path)

# Data to populate the template
data = {
    "name": "Itay Ben-Dan",
    "email": "itaybd@gmail.com",
    "phone": "+972544539284",
    "website": "linkedin.com/in/itaybendan",
    "experience": """2017-Present: Machine Learning and Data Science Consultant
    - Developed and deployed AI models for predictive analysis and automated invoice reconciliation.
    - Standardized diverse financial data into structured formats.

    2011-2015: Senior Quantitative Researcher, WorldQuant
    - Created computational models for quantitative strategies in finance.""",
    "skills": """Python, R, C++, Java
    TensorFlow, PyTorch, Scikit-learn
    Pandas, NumPy, SQL""",
    "projects": """TreeModelVis: Developed a visualization tool for tree-based models to aid decision-making.""",
    "education": """2009: Ph.D. in Mathematics, Technion, Haifa
    2004: M.Sc. in Mathematics, Technion, Haifa"""
}

# Render the data into the template
doc.render(data)

# Save the populated document
doc.save(output_path)
print(f"Generated CV document saved as {output_path}")
if __name__ == "__main__":
    template_path = os.path.join("Templates","Basic professional resume.docx")
    generate_cv("Itay_Ben_Dan_CV_Final", cv_data,template_path)

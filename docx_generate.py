from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def generate_cv_document(file_name, finalized_content_cv):
    """
    Generates a DOCX file for the CV based on the provided content with enhanced graphical presentation.

    Parameters:
    - file_name (str): Name (including path) of the DOCX file to be saved.
    - finalized_content_cv (str): The complete content of the CV to be added to the document.
    """
    doc = Document()

    # Set the font style and size for the document
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Separate sections by double newlines and process each section
    sections = finalized_content_cv.split('\n\n')
    for section in sections:
        # Identify and format each section based on its header or inferred content type
        if "Professional Summary" in section:
            add_formatted_section(doc, 'Professional Summary', section, heading_level=1)
        elif "Skills" in section:
            add_formatted_section(doc, 'Key Skills', section, heading_level=1, bullet_points=True)
        elif "Experience" in section or "Work Experience" in section:
            add_formatted_section(doc, 'Professional Experience', section, heading_level=1, bullet_points=True)
        elif "Education" in section:
            add_formatted_section(doc, 'Education', section, heading_level=1)
        else:
            # Generic paragraph if no specific section matches
            doc.add_paragraph(section.strip())

    # Save the document
    doc.save(file_name)
    print(f"CV document saved at: {file_name}")

def add_formatted_section(doc, heading, content, heading_level=2, bullet_points=False):
    """
    Helper function to add formatted sections to the DOCX document with graphical formatting.

    Parameters:
    - doc (Document): The DOCX document.
    - heading (str): Section heading.
    - content (str): Section content.
    - heading_level (int): The level of heading.
    - bullet_points (bool): Whether to add bullet points to the content.
    """
    # Add the section heading
    doc.add_heading(heading, level=heading_level)

    # Adjust the font for section headings
    heading_run = doc.paragraphs[-1].runs[0]
    heading_run.font.size = Pt(14)
    heading_run.bold = True

    # Add section content with bullet points if needed
    if bullet_points:
        items = content.split('\n')[1:]  # Exclude the first line (heading)
        for item in items:
            paragraph = doc.add_paragraph(item.strip(), style='List Bullet')
            paragraph_formatting(paragraph)
    else:
        # Plain text without bullet points
        paragraph = doc.add_paragraph(content.split('\n', 1)[-1].strip())
        paragraph_formatting(paragraph)

def paragraph_formatting(paragraph):
    """
    Helper function to apply graphical formatting to a paragraph.

    Parameters:
    - paragraph (Paragraph): The paragraph to format.
    """
    # Adjust paragraph spacing and alignment
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph_format = paragraph.paragraph_format
    paragraph_format.space_before = Pt(6)
    paragraph_format.space_after = Pt(6)

    # Add a line break element for cleaner formatting if needed
    line_break = OxmlElement('w:br')
    paragraph._p.append(line_break)

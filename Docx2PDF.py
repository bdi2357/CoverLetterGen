import win32com.client
import os

def docx_to_pdf(input_path, output_path):
    """
    Convert a DOCX file to PDF using win32com.

    Args:
        input_path (str): The path to the input DOCX file.
        output_path (str): The path to save the output PDF file.
    """
    word = win32com.client.Dispatch('Word.Application')
    doc = word.Documents.Open(os.path.abspath(input_path))
    doc.SaveAs(os.path.abspath(output_path), FileFormat=17)  # 17 is for wdFormatPDF
    doc.Close()
    word.Quit()


if __name__ == "__main__":
    input_path = os.path.join("Output","CV","CV_Rise_DataScientist.docx")
    output_path = os.path.join("Output","CV","CV_Rise_DataScientist.pdf")
    docx_to_pdf(input_path, output_path)
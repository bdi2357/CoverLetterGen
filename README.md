
# Cover Letter Generator and CV Adapter

This project provides tools for generating professional cover letters and adapting CVs to specific job descriptions using AI-based language models like OpenAI's GPT and other compatible models. It is designed to streamline the job application process by creating personalized documents that highlight relevant skills and experiences.

## Features

- **Cover Letter Generation:** Automatically generate personalized cover letters based on the CV and job description provided.
- **CV Adaptation:** Modify and adapt a CV to align with specific job requirements using language models.
- **Multi-format Output:** Generate both PDF and DOCX files with professional formatting.
- **Iterative Improvement:** Refine the generated cover letter through multiple iterations based on AI feedback.
- **Support for Multiple AI Models:** Allows integration with different AI models like OpenAI's GPT and GeminiModel.

## File Structure

The main components of the project are as follows:

1. **main.py**: The entry point of the application, which handles the generation and improvement of cover letters using AI models.

2. **ai_interaction.py**: Defines the interaction with the AI models (e.g., OpenAI GPT and GeminiModel) used to generate and improve cover letters and CVs.

3. **basic_iterative.py**: Contains iterative processes for refining the AI-generated cover letters based on feedback.

4. **cv_info_extractor.py**: Extracts relevant information from the CV, such as the applicant's name, contact details, skills, and experience.

5. **data_handling.py**: Includes functions for handling CV data, including loading, cleaning, and extracting text from files.

6. **docx_generate_a.py**: Handles the generation of DOCX files for the adapted CV and cover letter, ensuring proper formatting and styling.

7. **utilities.py**: Provides utility functions for creating PDFs and DOCX files, removing control characters, and handling document formatting.

## Usage

### Prerequisites

- Python 3.7+
- Required Python libraries as mentioned in `requirements.txt` (e.g., `openai`, `docx`, `reportlab`).

### Installation

1. Clone this repository.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Generate a Cover Letter:**
   Run the following command to generate a cover letter using a CV and job description:
   ```bash
   python main.py <path_to_cv_file> <job_description_text>
   ```

2. **Adapt a CV to a Job Description:**
   The CV will be automatically adapted to align with the job description provided, focusing on the relevant skills, experience, and qualifications.

### AI Model Integration

The project supports different AI models. You can specify the desired model by setting the `llm_provider` parameter in the `main.py` file:
- `openai`: Uses OpenAI's GPT models (e.g., GPT-4, GPT-3.5).
- `gemini`: Uses the GeminiModel for generating cover letters and adapting CVs.

### Output

- The final cover letter will be saved as a PDF file in the `Output` directory.
- The adapted CV will be saved as a DOCX file with enhanced formatting.

### Example

Here's an example of generating a cover letter for an AI Developer position:

```bash
python main.py Data/CV_GPT_rev.pdf "AI Developer job description text"
```

## Contribution

Feel free to contribute by submitting pull requests or reporting issues.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.


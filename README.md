# CoverLetterGen

*Automated, AI-powered cover letter and CV generator for tailored job applications.*

---

## 🚀 Overview

**CoverLetterGen** streamlines the job application process by generating professional cover letters and customized CVs tailored to specific job descriptions. Leveraging AI and flexible templates, it helps candidates and career coaches save time and increase application quality.

---

## ✨ Features

* **AI-driven cover letter generation** using OpenAI GPT models
* **Customizable CV and cover letter templates** (Word/.docx format)
* **Company and position extraction** from job descriptions
* **Batch processing** for multiple jobs and CVs
* **Output in both .docx and .pdf**
* **Easy command-line interface**

---

## 📦 Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/bdi2357/CoverLetterGen.git
   cd CoverLetterGen
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   *If `requirements.txt` is missing, install typical dependencies:*

   ```bash
   pip install python-docx openai
   ```

3. **(Optional) Set up OpenAI API key:**

   ```bash
   export OPENAI_API_KEY=your-key-here
   ```

---

## ⚡ Usage

### **Basic Example:**

Generate a tailored cover letter for a job description:

```bash
python main.py --cv data/sample_cv.docx --jd data/job_description.txt --output Output/cover_letter.docx
```

#### **Arguments:**

* `--cv`      : Path to your CV file (.docx)
* `--jd`      : Path to the job description text file
* `--output`  : Output path for the generated cover letter (.docx)
* `--template`: (Optional) Path to a custom cover letter template

### **Batch Processing:**

```bash
python batch_generate.py --cv_folder data/cvs/ --jd_folder data/jobs/ --output_folder Output/
```

---

## 📝 Custom Templates

Place your custom .docx template in the `Templates/` folder, and use the `--template` argument:

```bash
python main.py --cv ... --jd ... --template Templates/custom_template.docx
```

---

## 📁 Project Structure

```
CoverLetterGen/
├── main.py
├── batch_generate.py
├── ai_interaction.py
├── cover_letter_wrapper.py
├── cv_info_extractor.py
├── Templates/
├── Output/
├── data/
├── requirements.txt
└── README.md
```

---

## 🖼️ Example

* **Input:** `sample_cv.docx`, `job_description.txt`
* **Output:** `cover_letter.docx` in the Output/ folder

*Add a screenshot, diagram, or animated GIF here to show the workflow (optional).*

---

## 🤝 Contributing

Contributions, bug reports, and feature suggestions are welcome! Please open an issue or submit a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Credits & Acknowledgments

* Built using [python-docx](https://github.com/python-openxml/python-docx), [OpenAI GPT](https://platform.openai.com/)
* Inspired by the need to automate and personalize job applications

---

## 💡 Contact

For questions or suggestions, open an issue or contact the maintainer via GitHub.

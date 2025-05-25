# CoverLetterGen: AI-Powered Cover Letters & CVs for Business

## 💼 Transform Document Workflows with AI

**CoverLetterGen** automates the tedious and repetitive process of creating tailored cover letters and CVs, freeing up time for candidates and organizations alike. Built on state-of-the-art AI, it ensures every document is customized and professional, unlocking new productivity for HR teams, job boards, recruiters, and talent platforms.

*Automated, AI-powered cover letter and CV generator for tailored job applications.*

---

## 🖼️ Example Workflow

**1. Upload your CV and job description.**
![CV Input](Data/Screenshots/Screenshot(205).png)
*Sample CV as seen in PDF viewer.*

**2. Run CoverLetterGen (CLI or GUI).**

**3. Instantly receive a  tailored critique and improved CV.**
![Critique Output](Data/Screenshots/Screenshot(206).png)
*Automated CV critique with grades, strengths, and areas for improvement.*

**4. See measurable improvement after applying feedback.**
![Improved Critique Output](Data/Screenshots/Screenshot(209).png)
*The system helps improve your CV’s rating (from 8.5 to 9.0 in this example).*

## 🚀 Why CoverLetterGen? (For Teams & Partners)

* **Save Time:** Instantly generate custom cover letters and CVs—at scale—for job applicants, talent pools, or outbound recruiting.
* **Increase Quality:** AI-generated content adapts to each role and company, improving application standards and candidate experience.
* **Integrate Anywhere:** Use as a CLI, back-end batch process, or build on top for portals and workflow tools.
* **Customizable:** Bring your own templates, brand language, or prompt tuning.

**Typical Use Cases:**

* Job boards or HR SaaS that want to offer document generation as a feature
* Recruitment agencies seeking high-quality, automated outreach
* Enterprises with large-scale hiring or internal mobility programs

For partnership, integration, or demo, [contact the maintainer](#-contact).

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

## 🤝 Partnership & Contact

Interested in using CoverLetterGen for your company, platform, or workflow? Want to discuss a partnership or a pilot integration? Reach out via [GitHub issues](https://github.com/bdi2357/CoverLetterGen/issues) or email the maintainer directly: **[itaybd@gmail.com](mailto:itaybd@gmail.com)**

---

## 🙏 Credits & Acknowledgments

* Built using [python-docx](https://github.com/python-openxml/python-docx), [OpenAI GPT](https://platform.openai.com/)
* Inspired by the need to automate and personalize job applications

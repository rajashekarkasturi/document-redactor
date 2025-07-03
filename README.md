# 📃 Document Redactor 
A web application built on top of streamlit UI to redact PDFs **in-memory**.

## Demo

[![REDACT_PDF](https://img.youtube.com/vi/9phB1zFqphQ/0.jpg)](https://www.youtube.com/watch?v=9phB1zFqphQ)

### Local Demo

This demo on my local instance, demonstrates the working of PDF Redaction with features incorporating..
1. Selecting `REDACTION_PATTERNS`, `PAGE_RANGES`, `CUSTOM_TEXT` and `IMAGES` with a single click.
2. After you hit process, It shows preview of the Original and Redacted in side-by-side view.
3. You have the option to download the redacted PDF.

### Live Demo

* The Live demo is published on streamlit cloud at: <https://document-redactor-fetkppfjp3tptqjdkobidq.streamlit.app/>
* **Note:** Streamlit Cloud's Content Security Policy (CSP) is blocking all inline content loaded via data: URIs. so, there is issue in **rendering PDF's** after the processing.
* But, The functionality is intact and once you select the `REDACTION_CONFIGURATION` and hit process. You should be able to download the the redacted pdf.

## Local Setup

* Verified on Windows
* Ensure you've python 3.8+ and git installed in your system.

### 1. Clone the Repository
```bash
$> git clone https://github.com/rajashekarkasturi/document-redactor.git
$> cd document-redactor/
```

### 2. Create virtual environment and install dependencies

* This setup ensures to have isolated python environment for the project. While there is more robust way with [uv](https://docs.astral.sh/uv/guides/projects/), venv can get the job done.

```bash
$> python -m venv .venv
$> .venv\Scripts\activate
$> python -m pip install -r requirements.txt
```

### 3. Run the application
1. Launch the Streamlit app:
```bash
streamlit run app.py
```
2. Open your web browser and navigate to the local URL provided by Streamlit (usually http://localhost:8501).
3. Use the sidebar to configure redaction settings. (There is a sample PDF available to test under [sample_docs](./sample_docs/) )
4. Upload one or more PDF files to see the redaction in action.


## Learnings & Key Takeaways from the usecase

### Technology Validation:

- Given my experience in building GenAI applications with `Streamlit` for rapid prototyping and creating interactive demos, I focused mainly on the core logic for the current usecase. Though streamlit has limitation for single-threaded, synchronous nature, making it less suitable as a web frontend for long-running, heavy background tasks without architectural changes.

- `PyMuPDF` lived up to its reputation for performance and efficiency. It handled a 300-page test document with ease, and its redaction annotation feature is both effective and irreversible, which is critical for security.

### Performance Insights:

* The redaction process is primarily CPU-bound, driven by text searching (regex) and PDF rendering. For bulk processing of very large documents, a single process will become a bottleneck.
In-memory processing is **fast but memory-intensive**. A scalable solution must carefully manage memory, especially in a multi-user environment.


### Future Scope & Production-Ready Enhancements

This usecase provides a solid foundation. To evolve it into a robust, production-grade enterprise solution.
Key areas to focus

1. Re-architect the backend logic into a standalone RESTful API using FastAPI. This help the processing engine from the frontend, allowing for multiple clients (e.g., a React frontend, mobile app, or other microservices) and better separation of concerns.

2. **Containerization & Orchestration**: Containerize the API and worker services using Docker and prepare them for deployment on an orchestration platform like Kubernetes for auto-scaling.

3. **Advanced Intelligence: GenAI & OCR Integration**
GenAI for Superior PII Detection: Replace or augment regex-based PII detection with fine-tuned Named Entity Recognition (NER) models from platforms like Hugging Face or spaCy. This would drastically improve accuracy, reduce false positives/negatives, and allow for the detection of more nuanced sensitive data (e.g., company-specific project codenames).
OCR for Scanned Documents: Integrate an OCR engine (Tesseract, Amazon Textract, Google Vision API or Opensource Vision Models) to process image-based (scanned) PDFs. The OCR output would be fed into the redaction engine, making the solution universally applicable to all PDF types.
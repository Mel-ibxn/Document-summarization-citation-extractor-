# AI Legal Document Summarizer & Citation Extractor

A Streamlit app that extracts text from legal documents, generates an AI summary, and identifies citation-like references. It accepts PDF, DOCX, and TXT uploads and lets you choose a short, medium, or long summary.

## Features

- Extracts text from PDF, DOCX, and TXT files.
- Cleans extracted text while preserving paragraph breaks.
- Generates summaries with the `facebook/bart-large-cnn` model.
- Splits long input into chunks before summarizing.
- Finds likely case names, sections, acts, years, and courts using regular expressions.
- Displays the results in the app and lets you download them as a text file.

## Requirements

- Python installed and available in your terminal.
- Internet access the first time the summarizer runs, so Transformers can download the model and tokenizer.
- The dependencies listed in [`requirements.txt`](requirements.txt).

## Setup on Windows

Open PowerShell in the project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, you can install and run the app using the virtual environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Run the app

With the virtual environment activated:

```powershell
streamlit run app.py
```

Streamlit will print a local URL in the terminal. Open that URL in your browser, upload a PDF, DOCX, or TXT file, choose a summary length, and select **Process Document**. The first summary may take longer while the model is downloaded and loaded.

The summarizer uses CUDA when PyTorch detects a compatible GPU; otherwise, it runs on the CPU.

## Run the tests

From the project folder, with the virtual environment activated:

```powershell
python tests\run_all_tests.py
```

The tests cover document text cleaning and extraction, citation extraction, and basic summarization behavior. Summarization tests may download and load the model on the first run.

## Project structure

```text
app.py                    Streamlit user interface
document_processor.py     PDF, DOCX, and TXT text extraction and cleaning
summarizer.py             BART-based, chunked summarization
citation_extractor.py     Regular-expression citation extraction
requirements.txt          Python dependencies
tests/                    Unit tests and test runner
test_documents/           Sample legal text
```

## Limitations

- Citation extraction is pattern-based and may miss citations or return false positives. Verify extracted references against the source document.
- The summarizer's output can omit or misstate details. It is not legal advice and should not replace review by a qualified legal professional.
- Scanned PDFs without an extractable text layer may produce no text; this app does not perform OCR.
- Documents are processed by the application and model libraries. Do not upload confidential or sensitive documents unless you have confirmed that your environment and data-handling practices are appropriate.

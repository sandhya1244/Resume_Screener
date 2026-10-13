# Resume Screener

Flask web app that ranks resumes (PDF, DOCX, TXT) against a job description.

## Features
- Text extraction from PDF / DOCX / TXT
- Score (0-100) = 50% required-skill match + 35% TF-IDF cosine similarity + 15% experience years
- Auto-detects required skills from the JD if you leave the field blank
- Extracts email / phone, shows matched, missing and extra skills
- CSV export, drag-and-drop upload, dark UI

## Run
```bash
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py                                      # open http://127.0.0.1:5000
```

## Structure
```
app.py            Flask routes (/ and POST /api/screen)
screener.py       extraction + scoring logic (edit SKILLS and weights here)
templates/        frontend
samples/          test job description + resumes
```

## Ideas to extend
SQLite storage for history, login, spaCy/sentence-transformers for semantic matching, OCR (pytesseract) for scanned PDFs.

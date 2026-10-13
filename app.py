from flask import Flask, jsonify, render_template, request
from screener import extract_text, screen

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB per request


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/screen")
def api_screen():
    jd = request.form.get("jd", "").strip()
    required = request.form.get("skills", "").split(",")
    files = request.files.getlist("files")
    if not jd or not files:
        return jsonify(error="Provide a job description and at least one resume."), 400
    resumes, errors = [], []
    for f in files:
        try:
            text = extract_text(f.filename, f.read())
            if text.strip():
                resumes.append((f.filename.rsplit(".", 1)[0], text))
            else:
                errors.append(f"{f.filename}: no readable text (scanned PDF?)")
        except Exception as e:  # corrupt/unsupported file
            errors.append(f"{f.filename}: {e}")
    return jsonify(results=screen(jd, required, resumes), errors=errors)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

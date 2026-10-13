"""Core resume screening logic: text extraction, skill detection, scoring."""
import io
import re
from docx import Document
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILLS = """python java javascript typescript c++ c# go rust php ruby kotlin swift sql nosql mysql postgresql
mongodb redis react angular vue node.js django flask fastapi spring html css tailwind aws azure gcp docker
kubernetes terraform jenkins git ci/cd linux rest graphql microservices machine learning deep learning nlp
pandas numpy scikit-learn tensorflow pytorch spark hadoop kafka airflow tableau power bi excel data analysis
agile scrum jira communication leadership testing selenium devops""".replace("\n", " ").split(" ")
SKILLS = sorted(set(s for s in SKILLS if s) | {"machine learning", "deep learning", "data analysis", "power bi"})


def extract_text(filename: str, data: bytes) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]
    if ext == "pdf":
        return "\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages)
    if ext == "docx":
        return "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
    return data.decode("utf-8", errors="ignore")


def _has(text: str, skill: str) -> bool:
    return re.search(r"(?<![\w+#])" + re.escape(skill) + r"(?![\w+#])", text) is not None


def find_skills(text: str) -> list:
    t = text.lower()
    return [s for s in SKILLS if _has(t, s)]


def years_of_experience(text: str) -> int:
    nums = [int(n) for n in re.findall(r"(\d{1,2})\+?\s*(?:years|yrs)", text.lower())]
    return max(nums) if nums else 0


def contact(text: str) -> dict:
    email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
    phone = re.search(r"\+?\d[\d\s().-]{8,}\d", text)
    return {"email": email.group(0) if email else "", "phone": phone.group(0).strip() if phone else ""}


def screen(jd: str, required: list, resumes: list) -> list:
    """resumes: [(name, text)]. Returns candidates sorted by score (0-100)."""
    required = [r.strip().lower() for r in required if r.strip()] or find_skills(jd)
    need_years = years_of_experience(jd)
    texts = [t for _, t in resumes]
    sim = [0.0] * len(texts)
    if texts and jd.strip():
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
        m = vec.fit_transform([jd] + texts)
        sim = cosine_similarity(m[0:1], m[1:])[0]

    out = []
    for (name, text), s in zip(resumes, sim):
        low = text.lower()
        hit = [r for r in required if _has(low, r)]
        miss = [r for r in required if r not in hit]
        skill_score = len(hit) / len(required) if required else 0
        yrs = years_of_experience(text)
        exp_score = min(yrs / need_years, 1) if need_years else (1 if yrs else 0.5)
        total = 0.5 * skill_score + 0.35 * min(float(s) * 2.5, 1) + 0.15 * exp_score
        score = round(total * 100)
        out.append({
            "name": name, "score": score,
            "verdict": "Strong match" if score >= 70 else "Possible match" if score >= 45 else "Weak match",
            "matched": hit, "missing": miss, "extra_skills": [k for k in find_skills(text) if k not in required][:8],
            "years": yrs, "similarity": round(float(s) * 100), **contact(text),
        })
    return sorted(out, key=lambda c: c["score"], reverse=True)

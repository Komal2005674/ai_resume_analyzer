import sys
from pathlib import Path

from docx import Document
from pypdf import PdfReader
from sklearn.metrics import accuracy_score, classification_report


PROJECT_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = PROJECT_DIR / "sample_resumes"
sys.path.insert(0, str(PROJECT_DIR))

from job_matcher import rank_roles
from skill_extractor import extract_skills


def read_resume(path):
    if path.suffix.lower() == ".docx":
        document = Document(path)
        return "\n".join(p.text for p in document.paragraphs)

    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raise ValueError(f"Unsupported file: {path.name}")


def analyze(filename):
    path = SAMPLES_DIR / filename
    text = read_resume(path)
    skills = extract_skills(text)
    top_role = rank_roles(text, skills)[0]
    print(f"{filename}: {top_role['role']} ({top_role['score']:.1f}%)")
    return top_role


def score_for_role(skills, role_name):
    results = rank_roles("Test resume", skills)
    return next(result["score"] for result in results if result["role"] == role_name)


test_cases = [
    ("Sample_Data_Analyst_Resume.docx", "Data Analyst"),
    ("Sample_NLP_Resume.docx", "NLP Engineer"),
    ("Sample_Computer_Vision_Resume.docx", "Computer Vision Engineer"),
]

expected = []
predicted = []

print("Role ranking checks:")
for filename, correct_role in test_cases:
    result = analyze(filename)
    expected.append(correct_role)
    predicted.append(result["role"])

print()
print("Top-1 accuracy on three fictional resumes:")
print(f"{accuracy_score(expected, predicted):.1%}")
print(classification_report(expected, predicted, zero_division=0))

print("PDF/DOCX consistency check:")
nlp_docx = analyze("Sample_NLP_Resume.docx")
nlp_pdf = analyze("Sample_NLP_Resume.pdf")
print(
    "Same first role and score:",
    nlp_docx["role"] == nlp_pdf["role"]
    and nlp_docx["score"] == nlp_pdf["score"],
)

print()
print("Name-change check:")
name_file = SAMPLES_DIR / "Sample_Computer_Vision_Resume_Name_Test.docx"
if name_file.exists():
    original = analyze("Sample_Computer_Vision_Resume.docx")
    changed = analyze(name_file.name)
    print(
        "Same first role and score:",
        original["role"] == changed["role"]
        and original["score"] == changed["score"],
    )
else:
    print("Name test file is not in sample_resumes; check skipped.")

print()
print("Skill-change check for Data Analyst:")
without_sql = ["Python", "Excel", "Pandas", "Power BI"]
with_sql = without_sql + ["SQL"]
score_without = score_for_role(without_sql, "Data Analyst")
score_with = score_for_role(with_sql, "Data Analyst")
print(f"Without SQL: {score_without:.1f}%")
print(f"With SQL: {score_with:.1f}%")
print("Score increased after adding SQL:", score_with > score_without)

print()
print("These results cover only the included fictional samples.")
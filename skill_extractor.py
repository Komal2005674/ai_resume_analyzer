import re
from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).parent / "data" / "skill_dictionary.csv"

PERSONAL_FIELD = re.compile(
    r"^\s*(?:name|full name|email|e-mail|phone|mobile|contact|"
    r"address|date of birth|dob|age|gender|sex|nationality|"
    r"marital status|religion)\s*:",
    re.IGNORECASE,
)

SECTION_HEADING = re.compile(
    r"^\s*(?:profile|professional summary|summary|objective|"
    r"education|technical skills|skills|projects|experience|"
    r"work experience|internships|certifications)\s*:?\s*$",
    re.IGNORECASE,
)


def load_skills():
    return pd.read_csv(DATA_PATH).fillna("")


def job_related_text(text):
    """Remove common personal-detail lines before looking for skills."""
    lines = text.splitlines()

    # Resume headings and names commonly appear before the first section.
    first_section = next(
        (i for i, line in enumerate(lines[:15]) if SECTION_HEADING.match(line)),
        0,
    )
    lines = lines[first_section:]

    kept_lines = []
    for line in lines:
        if PERSONAL_FIELD.match(line):
            continue
        if "@" in line and re.search(r"\S+@\S+\.\S+", line):
            continue
        kept_lines.append(line)

    return "\n".join(kept_lines)


def extract_skills(text):
    skills_df = load_skills()
    searchable_text = job_related_text(text).lower()
    found = []

    for _, row in skills_df.iterrows():
        skill = str(row["skill"]).strip()
        aliases = str(row["aliases"]).strip()

        search_terms = [skill] + [
            alias.strip() for alias in aliases.split("|") if alias.strip()
        ]

        for term in search_terms:
            pattern = r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)"
            if re.search(pattern, searchable_text):
                found.append(skill)
                break

    return sorted(set(found), key=str.lower)


def skills_by_category(found_skills):
    skills_df = load_skills()
    grouped = {}

    for _, row in skills_df.iterrows():
        if row["skill"] in found_skills:
            category = row["category"]
            grouped.setdefault(category, []).append(row["skill"])

    return grouped
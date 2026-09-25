from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DATA_PATH = Path(__file__).parent / "data" / "job_roles.csv"


def load_roles():
    roles = pd.read_csv(DATA_PATH).fillna("")

    required_columns = {"role", "required_skills", "description"}
    missing_columns = required_columns - set(roles.columns)

    if missing_columns:
        raise ValueError(
            "job_roles.csv is missing columns: "
            + ", ".join(sorted(missing_columns))
        )

    return roles


def role_skills(role_row):
    return [
        skill.strip()
        for skill in str(role_row["required_skills"]).split("|")
        if skill.strip()
    ]


def rank_roles(resume_text, found_skills):
    """
    Rank roles using job-related skills only.

    resume_text is kept in the function arguments so app.py does not need
    to change. The raw resume text is not used in scoring.
    """
    roles_df = load_roles()

    if roles_df.empty:
        raise ValueError("The job role dataset is empty.")

    detected_skills = {skill.lower() for skill in found_skills}

    # Only detected job skills are converted to a TF-IDF vector.
    # Name and other personal resume details cannot enter this comparison.
    skill_text = " ".join(found_skills)

    role_texts = [
        f"{row['required_skills'].replace('|', ' ')} "
        f"{row['description']}"
        for _, row in roles_df.iterrows()
    ]

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([skill_text] + role_texts)
    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:],
    ).flatten()

    results = []

    for index, (_, row) in enumerate(roles_df.iterrows()):
        required = role_skills(row)

        matched = [
            skill
            for skill in required
            if skill.lower() in detected_skills
        ]

        missing = [
            skill
            for skill in required
            if skill.lower() not in detected_skills
        ]

        skill_coverage = (
            len(matched) / len(required)
            if required else 0.0
        )
        text_similarity = float(similarities[index])

        score = round(
            100 * (
                0.7 * skill_coverage
                + 0.3 * text_similarity
            ),
            1,
        )

        results.append(
            {
                "role": row["role"],
                "score": score,
                "matched": matched,
                "missing": missing,
                "description": row["description"],
            }
        )

    return sorted(
        results,
        key=lambda result: result["score"],
        reverse=True,
    )
import re


HEADINGS = {
    "education": {
        "education", "academic background",
        "academic qualifications", "qualifications",
    },
    "projects": {
        "projects", "academic projects",
        "personal projects", "project experience",
    },
    "experience": {
        "experience", "work experience",
        "professional experience", "internship", "internships",
    },
    "skills": {
        "skills", "technical skills",
        "core skills", "technologies",
    },
}

OTHER_HEADINGS = {
    "summary", "profile", "objective", "certifications",
    "achievements", "languages", "contact", "declaration",
}

ALL_HEADINGS = {
    heading
    for names in HEADINGS.values()
    for heading in names
}


def extract_sections(resume_text):
    sections = {
        "education": [],
        "projects": [],
        "experience": [],
        "skills": [],
    }

    current_section = None

    for raw_line in resume_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        normalized = re.sub(r"[:\s]+", " ", line.lower()).strip()

        # This sentence is a note on our fictional test resume,
        # not part of the candidate's experience.
        if normalized.startswith("this fictional sample"):
            current_section = None
            continue

        if normalized in ALL_HEADINGS:
            current_section = next(
                category
                for category, names in HEADINGS.items()
                if normalized in names
            )
            continue

        if normalized in OTHER_HEADINGS:
            current_section = None
            continue

        if current_section:
            sections[current_section].append(line)

    return {
        name: "\n".join(lines[:15]).strip()
        for name, lines in sections.items()
    }
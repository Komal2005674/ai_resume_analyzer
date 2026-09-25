import pandas as pd
import streamlit as st

from job_matcher import rank_roles
from resume_parser import extract_resume_text
from roadmap_generator import generate_roadmap
from section_extractor import extract_sections
from skill_extractor import extract_skills, skills_by_category
from text_cleaner import clean_text


st.set_page_config(
    page_title="CareerLens | AI Resume Analyzer",
    page_icon="🎯",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {
        background: #f4f7fc;
        color: #17233b;
    }

    .block-container {
        max-width: 1120px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        padding: 36px 40px;
        border-radius: 24px;
        background: linear-gradient(120deg, #14213d, #245c9c);
        color: white;
        margin-bottom: 26px;
        box-shadow: 0 12px 28px rgba(20, 33, 61, 0.16);
    }

    .hero-small {
        color: #a9dbff;
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .hero-title {
        color: white;
        font-size: 44px;
        line-height: 1.12;
        font-weight: 800;
        margin: 10px 0 12px;
    }

    .hero-text {
        color: #e5efff;
        font-size: 17px;
        max-width: 680px;
        margin: 0;
    }

    .section-title {
        font-size: 23px;
        font-weight: 750;
        color: #17233b;
        margin: 24px 0 13px;
    }

    .result-card {
        background: white;
        border: 1px solid #e4eaf4;
        border-radius: 18px;
        padding: 22px;
        margin: 10px 0;
        min-height: 135px;
        box-shadow: 0 5px 18px rgba(24, 47, 81, 0.05);
    }

    .card-label {
        color: #677993;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
    }

    .card-title {
        color: #17233b;
        font-size: 19px;
        font-weight: 750;
        margin: 10px 0;
    }

    .card-score {
        color: #146cb5;
        font-size: 26px;
        font-weight: 800;
    }

    .skill-tag {
        display: inline-block;
        padding: 7px 12px;
        margin: 4px 5px 4px 0;
        border-radius: 999px;
        background: #e7f1ff;
        color: #15558b;
        font-size: 14px;
        font-weight: 600;
    }

    .step-box {
        background: white;
        border-left: 4px solid #2582c6;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 9px 0;
        color: #17233b;
    }

    [data-testid="stFileUploader"] {
        background: white;
        padding: 18px;
        border: 1px solid #e4eaf4;
        border-radius: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-small">Your career insight dashboard</div>
        <div class="hero-title">CareerLens 🎯</div>
        <p class="hero-text">
            Discover job roles that fit your resume, see the skills
            you already have, and plan what to learn next.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Start with your resume")
st.caption("Upload a text-based PDF or DOCX file. Maximum size: 5 MB.")

uploaded_file = st.file_uploader(
    "Choose a resume",
    type=["pdf", "docx"],
    label_visibility="collapsed",
)

if uploaded_file is None:
    st.info("Upload a resume to see your analysis.")
    st.stop()

try:
    raw_text = extract_resume_text(uploaded_file)
    resume_sections = extract_sections(raw_text)
    cleaned_text = clean_text(raw_text)
    found_skills = extract_skills(cleaned_text)
    results = rank_roles(cleaned_text, found_skills)

    st.success(f"Resume analyzed: {uploaded_file.name}")
    st.caption(
        "Scores are estimates for learning and career guidance, "
        "not hiring decisions."
    )

    st.markdown(
        '<div class="section-title">Your top job matches</div>',
        unsafe_allow_html=True,
    )

    columns = st.columns(3)

    for index, (column, result) in enumerate(
        zip(columns, results[:3]), start=1
    ):
        with column:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="card-label">Recommendation {index}</div>
                    <div class="card-title">{result["role"]}</div>
                    <div class="card-score">{result["score"]}% match</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-title">Match comparison</div>',
        unsafe_allow_html=True,
    )

    chart_data = pd.DataFrame(
        {
            "Job role": [result["role"] for result in results],
            "Match score": [result["score"] for result in results],
        }
    ).set_index("Job role")

    st.bar_chart(chart_data)

    st.markdown(
        '<div class="section-title">Skills found in your resume</div>',
        unsafe_allow_html=True,
    )

    grouped_skills = skills_by_category(found_skills)

    if grouped_skills:
        for category, skills in grouped_skills.items():
            st.write(f"**{category}**")
            tags = "".join(
                f'<span class="skill-tag">{skill}</span>'
                for skill in skills
            )
            st.markdown(tags, unsafe_allow_html=True)
    else:
        st.warning(
            "No skills from the project dictionary were found "
            "in this resume."
        )

    st.markdown(
        '<div class="section-title">Explore a target role</div>',
        unsafe_allow_html=True,
    )

    selected_role = st.selectbox(
        "Select the role you want to analyze",
        [result["role"] for result in results],
    )

    selected = next(
        result
        for result in results
        if result["role"] == selected_role
    )

    st.metric(
        "Estimated match for this role",
        f'{selected["score"]}%',
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### ✅ Skills detected")
        if selected["matched"]:
            for skill in selected["matched"]:
                st.write(f"• {skill}")
        else:
            st.write("No required skills detected.")

    with right:
        st.markdown("#### 📌 Skills to learn or show in your resume")
        if selected["missing"]:
            for skill in selected["missing"]:
                st.write(f"• {skill}")
        else:
            st.write("All listed skills were detected.")

    st.markdown(
        '<div class="section-title">Your learning roadmap</div>',
        unsafe_allow_html=True,
    )

    roadmap = generate_roadmap(selected["missing"])

    for step in roadmap:
        st.markdown(
            f'<div class="step-box">{step}</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-title">Resume details detected</div>',
        unsafe_allow_html=True,
    )

    for title, key in [
        ("Education", "education"),
        ("Projects", "projects"),
        ("Experience", "experience"),
    ]:
        with st.expander(title):
            if resume_sections[key]:
                st.text(resume_sections[key])
            else:
                st.write(
                    "This section was not identified automatically. "
                    "Check the extracted text below."
                )

    report_lines = [
        "CAREERLENS RESUME ANALYSIS",
        f"Resume: {uploaded_file.name}",
        f"Target role: {selected['role']}",
        f"Estimated match: {selected['score']}%",
        "",
        "Skills detected:",
        ", ".join(found_skills) if found_skills else "None",
        "",
        "Education:",
        resume_sections["education"] or "Not identified",
        "",
        "Projects:",
        resume_sections["projects"] or "Not identified",
        "",
        "Experience:",
        resume_sections["experience"] or "Not identified",
        "",
        "Target role skills detected:",
        ", ".join(selected["matched"])
        if selected["matched"] else "None",
        "",
        "Skills to learn or show in your resume:",
        ", ".join(selected["missing"])
        if selected["missing"] else "None",
        "",
        "Top recommended roles:",
    ]

    for result in results[:3]:
        report_lines.append(
            f'{result["role"]}: {result["score"]}%'
        )

    report_lines.extend(["", "Learning roadmap:"])
    report_lines.extend(roadmap)
    report_lines.extend(
        [
            "",
            "These scores are estimates, not hiring decisions.",
            "A missing keyword does not prove a person lacks a skill.",
        ]
    )

    st.download_button(
        "⬇️ Download my analysis",
        "\n".join(report_lines),
        file_name="career_analysis.txt",
        mime="text/plain",
        use_container_width=True,
    )

    with st.expander("View extracted resume text"):
        st.text(raw_text)

except Exception as error:
    st.error("The analysis could not be completed.")
    st.code(str(error))
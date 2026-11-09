import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.skill_extractor import extract_skills


def match_jobs(resume_text, jobs_df):

    if not resume_text or not resume_text.strip():
        return pd.DataFrame()

    required_columns = [
        "job_title",
        "required_skills",
        "job_description"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in jobs_df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in jobs.csv: {missing_columns}"
        )

    jobs = jobs_df.copy()

    for col in required_columns:
        jobs[col] = jobs[col].fillna("").astype(str)

    # Prepare job descriptions
    job_texts = (
        jobs["job_title"] + " "
        + jobs["required_skills"] + " "
        + jobs["job_description"]
    )

    # TF-IDF matching
    documents = [resume_text] + job_texts.tolist()

    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform(documents)

    similarities = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    ).flatten()

    jobs["match_score"] = (similarities * 100).round(2)

    # Extract skills from the resume
    resume_skills = {
        skill.lower().strip()
        for skill in extract_skills(resume_text)
    }

    matched_results = []
    missing_results = []
    coverage_results = []

    # Analyze skill gaps for every job
    for _, job in jobs.iterrows():

        required_skills = [
            skill.strip()
            for skill in re.split(
                r"[,;|]",
                job["required_skills"]
            )
            if skill.strip()
        ]

        matched = [
            skill for skill in required_skills
            if skill.lower() in resume_skills
        ]

        missing = [
            skill for skill in required_skills
            if skill.lower() not in resume_skills
        ]

        coverage = (
            len(matched) / len(required_skills) * 100
            if required_skills else 0
        )

        matched_results.append(matched)
        missing_results.append(missing)
        coverage_results.append(round(coverage, 2))

    jobs["matched_skills"] = matched_results
    jobs["missing_skills"] = missing_results
    jobs["skill_coverage"] = coverage_results

    # Sort by text similarity
    jobs = jobs.sort_values(
        "match_score",
        ascending=False
    )

    return jobs.reset_index(drop=True)
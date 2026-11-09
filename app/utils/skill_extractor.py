import pandas as pd
import os


def extract_skills(resume_text):

    # Find the skills dataset
    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )

    skills_path = os.path.join(
        base_dir,
        "data",
        "skills.csv"
    )

    # Load skills
    skills_df = pd.read_csv(skills_path)

    # Convert resume text to lowercase
    resume_text_lower = resume_text.lower()

    found_skills = []

    # Search for each skill
    for skill in skills_df["skill"]:

        skill = str(skill).strip()

        if skill and skill.lower() in resume_text_lower:

            found_skills.append(skill)

    return found_skills
import os
import re
from io import BytesIO
from html import escape

import pandas as pd
import streamlit as st
from pypdf import PdfReader

from app.utils.job_matcher import match_jobs


# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="CareerPilotAI | Career Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
JOBS_PATH = os.path.join(DATA_DIR, "jobs.csv")
SKILLS_PATH = os.path.join(DATA_DIR, "skills.csv")


# ============================================================
# CUSTOM CSS
# Keep all CSS inside this triple-quoted string.
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    :root {
        --bg: #07111f;
        --panel: #0d1b2d;
        --panel-soft: #102239;
        --border: rgba(148, 181, 219, 0.16);
        --text: #edf5ff;
        --muted: #9aafc9;
        --teal: #39e6c1;
        --blue: #5b8cff;
        --purple: #a78bfa;
        --gold: #ffd166;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 4%, rgba(35, 113, 160, 0.16), transparent 27%),
            radial-gradient(circle at 88% 12%, rgba(119, 76, 198, 0.15), transparent 26%),
            var(--bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(7, 17, 31, 0.88);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b192b 0%, #081321 100%);
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] * {
        color: var(--text);
    }

    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.025em;
    }

    p, label, span, li {
        color: inherit;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0.3rem 0 1.6rem;
    }

    .brand-icon {
        width: 46px;
        height: 46px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        background: linear-gradient(135deg, #39e6c1, #5b8cff);
        color: #07111f;
        font-size: 24px;
        font-weight: 800;
        box-shadow: 0 8px 30px rgba(57, 230, 193, 0.15);
    }

    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.32rem;
        font-weight: 700;
        line-height: 1.2;
        color: var(--text);
    }

    .brand-caption {
        color: var(--muted);
        font-size: 0.76rem;
        margin-top: 4px;
    }

    .eyebrow {
        color: var(--teal);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        margin-bottom: 0.65rem;
    }

    .hero-card {
        position: relative;
        overflow: hidden;
        padding: 2.5rem;
        border: 1px solid rgba(91, 140, 255, 0.24);
        border-radius: 26px;
        background:
            radial-gradient(circle at 85% 10%, rgba(167, 139, 250, 0.22), transparent 35%),
            linear-gradient(135deg, rgba(18, 42, 69, 0.98), rgba(10, 25, 43, 0.98));
        box-shadow: 0 18px 55px rgba(0, 0, 0, 0.16);
        margin-bottom: 1.5rem;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: clamp(2.4rem, 5vw, 4.3rem);
        line-height: 1.06;
        font-weight: 700;
        letter-spacing: -0.06em;
        margin-bottom: 1rem;
        color: var(--text);
    }

    .hero-gradient {
        background: linear-gradient(90deg, #39e6c1 0%, #5b8cff 52%, #b79aff 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .hero-description {
        color: #b3c6dd;
        max-width: 650px;
        font-size: 1.03rem;
        line-height: 1.8;
        margin-bottom: 1.3rem;
    }

    .hero-pill {
        display: inline-block;
        padding: 0.55rem 0.9rem;
        border: 1px solid rgba(57, 230, 193, 0.28);
        border-radius: 999px;
        color: var(--teal);
        background: rgba(57, 230, 193, 0.08);
        font-size: 0.82rem;
        font-weight: 600;
    }

    .section-heading {
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text);
        font-size: 1.45rem;
        font-weight: 700;
        margin: 1.6rem 0 0.35rem;
    }

    .section-subtitle {
        color: var(--muted);
        margin-bottom: 1.1rem;
        font-size: 0.93rem;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(17, 38, 61, 0.96), rgba(10, 25, 42, 0.96));
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 1.25rem 1.3rem;
        min-height: 135px;
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.84rem;
        margin-bottom: 0.75rem;
    }

    .metric-value {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.1;
    }

    .metric-note {
        color: var(--teal);
        font-size: 0.78rem;
        margin-top: 0.55rem;
    }

    .feature-card {
        height: 100%;
        padding: 1.35rem;
        border-radius: 18px;
        border: 1px solid var(--border);
        background: rgba(13, 27, 45, 0.88);
    }

    .feature-icon {
        width: 44px;
        height: 44px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 13px;
        background: rgba(91, 140, 255, 0.14);
        font-size: 1.35rem;
        margin-bottom: 1rem;
    }

    .feature-title {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 1.06rem;
        margin-bottom: 0.5rem;
    }

    .feature-description {
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.65;
    }

    .content-card {
        padding: 1.35rem;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: rgba(13, 27, 45, 0.86);
        margin-bottom: 1rem;
    }

    .small-label {
        color: var(--muted);
        text-transform: uppercase;
        font-size: 0.74rem;
        letter-spacing: 0.1em;
        font-weight: 700;
    }

    .skill-badge {
        display: inline-block;
        padding: 0.38rem 0.72rem;
        margin: 0.25rem 0.25rem 0.25rem 0;
        border-radius: 999px;
        border: 1px solid rgba(57, 230, 193, 0.25);
        background: rgba(57, 230, 193, 0.08);
        color: #8ef5df;
        font-size: 0.8rem;
    }

    .skill-badge.missing {
        border-color: rgba(255, 209, 102, 0.3);
        background: rgba(255, 209, 102, 0.08);
        color: var(--gold);
    }

    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        border: 7px solid var(--teal);
        background: rgba(57, 230, 193, 0.06);
        margin: 0.5rem auto 1rem;
    }

    .score-number {
        color: var(--text);
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1;
    }

    .score-caption {
        color: var(--muted);
        font-size: 0.72rem;
        margin-top: 0.35rem;
    }

    .footer {
        border-top: 1px solid var(--border);
        padding-top: 1rem;
        margin-top: 2.5rem;
        color: #8298b3;
        font-size: 0.78rem;
        text-align: center;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 11px;
        border: 1px solid rgba(57, 230, 193, 0.35);
        background: linear-gradient(100deg, #39e6c1, #6aa7ff);
        color: #061321;
        font-weight: 700;
        min-height: 2.7rem;
        transition: transform 0.15s ease, filter 0.15s ease;
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-1px);
        border-color: rgba(57, 230, 193, 0.65);
        color: #061321;
    }

    input, textarea, [data-baseweb="select"] > div {
        background-color: #0b1b2e !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }

    [data-testid="stFileUploader"] {
        border: 1px dashed rgba(91, 140, 255, 0.45);
        border-radius: 16px;
        padding: 0.7rem;
        background: rgba(13, 27, 45, 0.55);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }

    hr {
        border-color: var(--border);
    }

    @media (max-width: 700px) {
        .hero-card {
            padding: 1.4rem;
        }
        .hero-title {
            font-size: 2.4rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA LOADING
# ============================================================
@st.cache_data
def load_jobs():
    """Load job listings from data/jobs.csv."""
    if not os.path.exists(JOBS_PATH):
        return pd.DataFrame()

    try:
        return pd.read_csv(JOBS_PATH)
    except Exception as exc:
        st.warning(f"Could not read jobs.csv: {exc}")
        return pd.DataFrame()


@st.cache_data
def load_skill_list():
    """Load skill reference data from data/skills.csv."""
    if not os.path.exists(SKILLS_PATH):
        return []

    try:
        skills_df = pd.read_csv(SKILLS_PATH)
        if skills_df.empty:
            return []

        # Use a column named 'skill' if available; otherwise use the first column.
        skill_column = next(
            (col for col in skills_df.columns if str(col).strip().lower() == "skill"),
            skills_df.columns[0],
        )
        return [
            str(value).strip()
            for value in skills_df[skill_column].dropna().tolist()
            if str(value).strip()
        ]
    except Exception as exc:
        st.warning(f"Could not read skills.csv: {exc}")
        return []


# ============================================================
# RESUME HELPERS
# ============================================================
def extract_resume_text(uploaded_file):
    """Extract text from a PDF or plain-text resume."""
    if uploaded_file is None:
        return ""

    filename = uploaded_file.name.lower()

    try:
        file_bytes = uploaded_file.getvalue()

        if filename.endswith(".pdf"):
            reader = PdfReader(BytesIO(file_bytes))
            pages = []
            for page in reader.pages:
                pages.append(page.extract_text() or "")
            return "\n".join(pages).strip()

        if filename.endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore").strip()

        st.error("Please upload a PDF or TXT resume.")
        return ""

    except Exception as exc:
        st.error(f"Could not read the uploaded resume: {exc}")
        return ""


def extract_skills(text, known_skills=None):
    """Find skills in text using case-insensitive whole-word matching."""
    if not text:
        return []

    if known_skills is None:
        known_skills = load_skill_list()

    found = []
    normalized_text = text.lower()

    for skill in known_skills:
        skill = str(skill).strip()
        if not skill:
            continue

        # Escape special regex characters and allow flexible spaces in skill names.
        pattern = re.escape(skill.lower()).replace(r"\ ", r"\s+")
        if re.search(r"(?<!\w)" + pattern + r"(?!\w)", normalized_text):
            if skill not in found:
                found.append(skill)

    return found


def normalize_match_score(value):
    """Convert a matching score into a percentage from 0 to 100."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0

    # If the helper returns a fraction, convert it to a percentage.
    if 0 <= score <= 1:
        score *= 100

    return max(0.0, min(score, 100.0))


def render_skill_badges(skills, missing=False):
    """Display skills as small colored badges."""
    if not skills:
        st.caption("No skills to display yet.")
        return

    badge_class = "skill-badge missing" if missing else "skill-badge"
    badges = "".join(
        f'<span class="{badge_class}">{escape(str(skill))}</span>'
        for skill in skills
    )
    st.markdown(badges, unsafe_allow_html=True)


def display_score_circle(score, label="Match score"):
    """Render a simple score circle."""
    safe_score = max(0, min(int(round(score)), 100))
    st.markdown(
        f"""
        <div class="score-circle">
            <div class="score-number">{safe_score}%</div>
            <div class="score-caption">{escape(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer():
    st.markdown(
        '<div class="footer">CareerPilotAI · Navigate your next career move with confidence.</div>',
        unsafe_allow_html=True,
    )


def render_metric(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{escape(str(label))}</div>
            <div class="metric-value">{escape(str(value))}</div>
            <div class="metric-note">{escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_column(df, possible_names):
    """Return the first matching column name, ignoring case and spaces."""
    if df.empty:
        return None

    normalized = {str(col).strip().lower(): col for col in df.columns}
    for candidate in possible_names:
        key = candidate.strip().lower()
        if key in normalized:
            return normalized[key]
    return None


def run_job_matching(resume_text, jobs_df):
    """Call the project's existing job matcher and return its DataFrame."""
    try:
        result = match_jobs(resume_text, jobs_df)
        if isinstance(result, pd.DataFrame):
            return result
        return pd.DataFrame(result)
    except Exception as exc:
        st.error(
            "The job matcher could not process these listings. "
            "Check app/utils/job_matcher.py and the columns in data/jobs.csv."
        )
        st.exception(exc)
        return pd.DataFrame()


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown(
        """
        <div class="brand-row">
            <div class="brand-icon">✦</div>
            <div>
                <div class="brand-name">CareerPilotAI</div>
                <div class="brand-caption">Your personal career copilot</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Workspace")

    page = st.radio(
        "Navigation",
        [
            "Home",
            "Resume Analyzer",
            "Job Matching",
            "Skill Gap Analysis",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Your career toolkit**")
    st.caption("Upload your resume, explore job matches, and identify skills to learn.")
    st.markdown("---")
    st.caption("CareerPilotAI · Version 1.0")


# ============================================================
# SHARED SESSION STATE
# ============================================================
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_name" not in st.session_state:
    st.session_state.resume_name = ""

if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

if "matched_jobs" not in st.session_state:
    st.session_state.matched_jobs = pd.DataFrame()


# ============================================================
# HOME DASHBOARD
# ============================================================
if page == "Home":
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">✨ Your career starts here</div>
            <div class="hero-title">
                Career<span class="hero-gradient">PilotAI</span>
            </div>
            <div class="hero-description">
                Your intelligent career companion. Analyze your resume,
                discover matching jobs, and build the skills employers need.
            </div>
            <div class="hero-pill">🚀 Make your next move with confidence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    jobs_df = load_jobs()
    skills = load_skill_list()

    total_jobs = len(jobs_df)
    total_skills = len(skills)
    resume_status = "Uploaded" if st.session_state.resume_text else "Not yet"
    resume_skill_count = len(st.session_state.resume_skills)

    st.markdown('<div class="section-heading">Your career overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">A quick look at your workspace and progress.</div>',
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric("Job listings", total_jobs, "Available opportunities")
    with metric_cols[1]:
        render_metric("Skills library", total_skills, "Skills in your reference file")
    with metric_cols[2]:
        render_metric("Resume status", resume_status, "Your current workspace")
    with metric_cols[3]:
        render_metric("Detected skills", resume_skill_count, "From your last analysis")

    st.markdown('<div class="section-heading">Explore your toolkit</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-subtitle">Choose a feature to get started.</div>',
        unsafe_allow_html=True,
    )

    feature_cols = st.columns(3)
    feature_data = [
        (
            "📄",
            "Resume Analyzer",
            "Upload a PDF or TXT resume and identify skills mentioned in it.",
        ),
        (
            "🎯",
            "Job Matching",
            "Compare your resume with available job listings and view match scores.",
        ),
        (
            "🧭",
            "Skill Gap Analysis",
            "Compare your detected skills with a selected job's required skills.",
        ),
    ]

    for col, feature in zip(feature_cols, feature_data):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{feature[0]}</div>
                    <div class="feature-title">{feature[1]}</div>
                    <div class="feature-description">{feature[2]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    left, right = st.columns([1, 1])

    with left:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("#### Start with your resume")
        st.write("Upload your resume to extract skills and prepare for job matching.")
        if st.button("Open Resume Analyzer", use_container_width=True):
            st.session_state["requested_page"] = "Resume Analyzer"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("#### Find your next opportunity")
        st.write("See which listings align best with your resume.")
        if st.button("Open Job Matching", use_container_width=True):
            st.session_state["requested_page"] = "Job Matching"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


# ============================================================
# RESUME ANALYZER
# ============================================================
elif page == "Resume Analyzer":
    st.markdown('<div class="eyebrow">Resume intelligence</div>', unsafe_allow_html=True)
    st.title("Resume Analyzer")
    st.markdown(
        '<div class="section-subtitle">Upload your resume to extract text and identify skills.</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "txt"],
        help="PDF and TXT files are supported.",
        key="resume_upload",
    )

    if uploaded_file is not None:
        if st.button("Analyze Resume", type="primary"):
            with st.spinner("Reading your resume..."):
                resume_text = extract_resume_text(uploaded_file)

            if resume_text:
                skills = extract_skills(resume_text)
                st.session_state.resume_text = resume_text
                st.session_state.resume_name = uploaded_file.name
                st.session_state.resume_skills = skills
                st.session_state.matched_jobs = pd.DataFrame()
                st.success("Resume analyzed successfully.")
            else:
                st.error(
                    "No readable text was found. If your PDF is a scanned image, "
                    "it may need OCR before text can be extracted."
                )

    if st.session_state.resume_text:
        st.markdown('<div class="section-heading">Analysis results</div>', unsafe_allow_html=True)

        result_cols = st.columns(3)
        with result_cols[0]:
            render_metric("Resume file", st.session_state.resume_name or "Loaded", "Current resume")
        with result_cols[1]:
            render_metric("Characters", f"{len(st.session_state.resume_text):,}", "Extracted text length")
        with result_cols[2]:
            render_metric("Skills found", len(st.session_state.resume_skills), "Matched against skills library")

        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("#### Skills identified")
        render_skill_badges(st.session_state.resume_skills)
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("View extracted resume text"):
            st.text_area(
                "Extracted text",
                value=st.session_state.resume_text,
                height=280,
                disabled=True,
            )

        resume_txt = st.session_state.resume_text.encode("utf-8")
        st.download_button(
            "Download extracted text",
            data=resume_txt,
            file_name="extracted_resume.txt",
            mime="text/plain",
        )
    else:
        st.info("Upload a resume above and select **Analyze Resume** to begin.")

    render_footer()


# ============================================================
# JOB MATCHING
# ============================================================
elif page == "Job Matching":
    st.markdown('<div class="eyebrow">Opportunity discovery</div>', unsafe_allow_html=True)
    st.title("Job Matching")
    st.markdown(
        '<div class="section-subtitle">Find listings that align with your resume and skills.</div>',
        unsafe_allow_html=True,
    )

    jobs_df = load_jobs()

    if not st.session_state.resume_text:
        st.warning("Analyze your resume first. Open **Resume Analyzer** from the sidebar.")
    elif jobs_df.empty:
        st.error(
            f"No job listings were loaded. Make sure this file exists and contains data:\n\n"
            f"`{JOBS_PATH}`"
        )
    else:
        st.markdown(
            f'<div class="content-card"><span class="small-label">Resume loaded</span>'
            f'<h3>{escape(st.session_state.resume_name or "Resume")}</h3>'
            f'<p style="color:#9aafc9;">{len(st.session_state.resume_skills)} skills detected.</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if st.button("Find Matching Jobs", type="primary"):
            with st.spinner("Comparing your resume with job listings..."):
                st.session_state.matched_jobs = run_job_matching(
                    st.session_state.resume_text,
                    jobs_df,
                )

        matches = st.session_state.matched_jobs

        if not matches.empty:
            score_col = safe_column(
                matches,
                ["match_score", "match percentage", "match_percent", "score", "similarity"],
            )

            if score_col:
                matches = matches.copy()
                matches["_display_score"] = matches[score_col].apply(normalize_match_score)
                matches = matches.sort_values("_display_score", ascending=False)

            st.markdown('<div class="section-heading">Your job matches</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-subtitle">Review the most relevant opportunities below.</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f'<div class="metric-card"><div class="metric-label">Listings evaluated</div>'
                f'<div class="metric-value">{len(matches)}</div>'
                f'<div class="metric-note">Based on the current jobs dataset</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown("<br>", unsafe_allow_html=True)

            title_col = safe_column(matches, ["job_title", "title", "role", "position", "job"])
            company_col = safe_column(matches, ["company", "company_name", "employer", "organization"])
            location_col = safe_column(matches, ["location", "city", "job_location"])
            description_col = safe_column(matches, ["description", "job_description", "details"])
            required_col = safe_column(
                matches,
                ["required_skills", "skills", "skills_required", "job_skills"],
            )

            for rank, (_, row) in enumerate(matches.head(20).iterrows(), start=1):
                title = str(row[title_col]) if title_col else f"Job opportunity {rank}"
                company = str(row[company_col]) if company_col else "Company not specified"
                location = str(row[location_col]) if location_col else "Location not specified"

                with st.container(border=True):
                    job_left, job_right = st.columns([4, 1])

                    with job_left:
                        st.markdown(f"### {rank}. {title}")
                        st.caption(f"{company} · {location}")

                        if description_col and pd.notna(row[description_col]):
                            description = str(row[description_col])
                            st.write(description[:450] + ("..." if len(description) > 450 else ""))

                        if required_col and pd.notna(row[required_col]):
                            st.markdown("**Skills / requirements**")
                            render_skill_badges(
                                [part.strip() for part in re.split(r"[,;|]", str(row[required_col])) if part.strip()]
                            )

                    with job_right:
                        if "_display_score" in row.index:
                            display_score_circle(row["_display_score"], "Match")
                        elif score_col:
                            display_score_circle(normalize_match_score(row[score_col]), "Match")
                        else:
                            st.metric("Rank", rank)

            csv_bytes = matches.drop(columns=["_display_score"], errors="ignore").to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download job matches as CSV",
                data=csv_bytes,
                file_name="careerpilot_job_matches.csv",
                mime="text/csv",
            )
        elif st.session_state.get("job_match_attempted", False):
            st.info("No matches were returned. Check your job data and matcher implementation.")

    render_footer()


# ============================================================
# SKILL GAP ANALYSIS
# ============================================================
elif page == "Skill Gap Analysis":
    st.markdown('<div class="eyebrow">Plan your next learning step</div>', unsafe_allow_html=True)
    st.title("Skill Gap Analysis")
    st.markdown(
        '<div class="section-subtitle">Compare the skills in your resume with a target job.</div>',
        unsafe_allow_html=True,
    )

    jobs_df = load_jobs()
    user_skills = st.session_state.resume_skills

    if not st.session_state.resume_text:
        st.warning("Analyze your resume first. Open **Resume Analyzer** from the sidebar.")
    else:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("#### Skills from your resume")
        render_skill_badges(user_skills)
        st.markdown("</div>", unsafe_allow_html=True)

        required_col = safe_column(
            jobs_df,
            ["required_skills", "skills_required", "job_skills", "skills"],
        )
        title_col = safe_column(jobs_df, ["job_title", "title", "role", "position", "job"])
        company_col = safe_column(jobs_df, ["company", "company_name", "employer", "organization"])

        if jobs_df.empty or required_col is None:
            st.info(
                "Your jobs.csv needs a column containing required skills "
                "(for example, `required_skills` or `skills`)."
            )
            manual_skills = st.text_input(
                "Enter target job skills separated by commas",
                placeholder="Python, SQL, Machine Learning, Power BI",
            )
            target_skills = [item.strip() for item in manual_skills.split(",") if item.strip()]
            selected_job_label = "Custom job"
        else:
            options = []
            row_by_label = {}

            for index, row in jobs_df.iterrows():
                title = str(row[title_col]) if title_col else f"Job {index + 1}"
                company = str(row[company_col]) if company_col else "Company not specified"
                label = f"{title} — {company}"
                options.append(label)
                row_by_label[label] = row

            selected_job_label = st.selectbox("Choose a target job", options)
            selected_row = row_by_label[selected_job_label]
            raw_required = selected_row[required_col]
            target_skills = (
                [part.strip() for part in re.split(r"[,;|]", str(raw_required)) if part.strip()]
                if pd.notna(raw_required)
                else []
            )

        if st.button("Analyze Skill Gap", type="primary"):
            user_normalized = {str(skill).strip().lower() for skill in user_skills}
            target_normalized = {}
            for skill in target_skills:
                clean_skill = str(skill).strip()
                if clean_skill:
                    target_normalized[clean_skill.lower()] = clean_skill

            matched_skills = [
                original
                for key, original in target_normalized.items()
                if key in user_normalized
            ]
            missing_skills = [
                original
                for key, original in target_normalized.items()
                if key not in user_normalized
            ]

            total_required = len(target_normalized)
            coverage = (
                round((len(matched_skills) / total_required) * 100)
                if total_required
                else 0
            )

            st.session_state.skill_gap_result = {
                "job": selected_job_label,
                "matched": matched_skills,
                "missing": missing_skills,
                "coverage": coverage,
            }

        gap_result = st.session_state.get("skill_gap_result")

        if gap_result:
            st.markdown('<div class="section-heading">Your skill gap report</div>', unsafe_allow_html=True)
            st.write(f"**Target role:** {gap_result['job']}")

            gap_cols = st.columns([1, 2, 2])
            with gap_cols[0]:
                display_score_circle(gap_result["coverage"], "Skill coverage")
            with gap_cols[1]:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown("#### ✅ Skills you have")
                render_skill_badges(gap_result["matched"])
                st.markdown("</div>", unsafe_allow_html=True)
            with gap_cols[2]:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.markdown("#### 🎯 Skills to develop")
                render_skill_badges(gap_result["missing"], missing=True)
                st.markdown("</div>", unsafe_allow_html=True)

            if gap_result["missing"]:
                st.markdown("### Suggested next step")
                st.write(
                    "Prioritize one missing skill at a time. Learn the fundamentals, "
                    "build a small project using it, and add the project to your portfolio."
                )
            else:
                st.success("Great! All skills listed for this target role were found in your resume.")

            report_lines = [
                "CareerPilotAI - Skill Gap Report",
                f"Target role: {gap_result['job']}",
                f"Skill coverage: {gap_result['coverage']}%",
                "",
                "Skills found in resume:",
                *[f"- {skill}" for skill in gap_result["matched"]],
                "",
                "Skills to develop:",
                *[f"- {skill}" for skill in gap_result["missing"]],
            ]
            st.download_button(
                "Download skill gap report",
                data="\n".join(report_lines).encode("utf-8"),
                file_name="careerpilot_skill_gap_report.txt",
                mime="text/plain",
            )

    render_footer()


# ============================================================
# NAVIGATION BUTTON SUPPORT
# ============================================================
# Streamlit's radio controls page navigation. The dashboard buttons
# above are kept as helpful prompts; selecting a page in the sidebar
# remains the reliable navigation method.
if "requested_page" in st.session_state:
    requested_page = st.session_state.pop("requested_page")
    if requested_page != page:
        st.info(f"To open **{requested_page}**, select it from the sidebar navigation.")



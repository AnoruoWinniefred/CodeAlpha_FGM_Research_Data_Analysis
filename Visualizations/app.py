import os
from pathlib import Path

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="FGM Research in Nigeria",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clinical navy + teal palette
NAVY = "#15344B"
TEAL = "#167D8D"
TEAL_LIGHT = "#E5F3F4"
BG = "#F4F7FA"
TEXT = "#243746"
MUTED = "#647789"
BORDER = "#DFE7ED"
WHITE = "#FFFFFF"


# ==================================================
# 2. CUSTOM DASHBOARD STYLING
# ==================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BG};
        color: {TEXT};
    }}

    [data-testid="stHeader"] {{
        background-color: transparent;
    }}

    [data-testid="stSidebar"] {{
        background-color: {WHITE};
        border-right: 1px solid {BORDER};
    }}

    .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1500px;
    }}

    h1, h2, h3 {{
        color: {NAVY} !important;
        letter-spacing: -0.3px;
    }}

    p, li, label {{
        color: {TEXT};
    }}

    .hero {{
        background: linear-gradient(120deg, {NAVY}, {TEAL});
        padding: 30px 32px;
        border-radius: 16px;
        margin-bottom: 22px;
        color: white;
    }}

    .hero h1 {{
        color: white !important;
        margin: 0 0 8px 0;
        font-size: 2.15rem;
    }}

    .hero p {{
        color: #E1F0F3 !important;
        margin: 0;
        font-size: 1rem;
    }}

    .eyebrow {{
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #BDE6E8;
        margin-bottom: 8px;
    }}

    .research-question {{
        background: {WHITE};
        border: 1px solid {BORDER};
        border-left: 5px solid {TEAL};
        padding: 20px 24px;
        border-radius: 10px;
        margin-bottom: 24px;
    }}

    .research-question p {{
        margin-bottom: 0;
    }}

    .section-intro {{
        color: {MUTED};
        font-size: 0.96rem;
        margin-top: -8px;
        margin-bottom: 18px;
    }}

    .metric-card {{
        background: {WHITE};
        border: 1px solid {BORDER};
        border-top: 4px solid {TEAL};
        border-radius: 12px;
        padding: 18px 20px;
        min-height: 112px;
    }}

    .metric-label {{
        color: {MUTED};
        font-size: 0.83rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}

    .metric-value {{
        color: {NAVY};
        font-size: 2rem;
        font-weight: 750;
        line-height: 1.15;
    }}

    .finding-card {{
        background: {WHITE};
        border: 1px solid {BORDER};
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0 18px 0;
    }}

    .finding-label {{
        color: {TEAL};
        font-size: 0.76rem;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
    }}

    .finding-card p {{
        margin-bottom: 0;
        line-height: 1.65;
    }}

    div[data-testid="stDownloadButton"] button {{
        background-color: {TEAL};
        color: white;
        border: 0;
        border-radius: 8px;
        font-weight: 600;
    }}

    div[data-testid="stDownloadButton"] button:hover {{
        background-color: {NAVY};
        color: white;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 10px;
    }}

    hr {{
        border-color: {BORDER};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 3. LOAD THE EXISTING DATASET
# ==================================================

@st.cache_data
def load_data(csv_path, modified_time):
    data = pd.read_csv(
        csv_path,
        dtype={"pmid": str},
    )

    data.columns = data.columns.str.strip()

    required = [
        "publication_year",
        "screening_decision",
        "study_location",
        "research_type",
        "title",
        "abstract",
    ]

    missing = [column for column in required
               if column not in data.columns]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    data["publication_year"] = pd.to_numeric(
        data["publication_year"],
        errors="coerce",
    )

    for column in [
        "screening_decision",
        "study_location",
        "research_type",
        "title",
        "abstract",
    ]:
        data[column] = (
            data[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    return data


possible_paths = [
    Path.cwd() / "fgm_articles_screening.csv",
    Path(__file__).resolve().parent / "fgm_articles_screening.csv",
    Path(__file__).resolve().parent.parent / "fgm_articles_screening.csv",
]

csv_path = next(
    (path for path in possible_paths if path.is_file()),
    None,
)

if csv_path is None:
    st.error(
        "Could not find fgm_articles_screening.csv. "
        "Place it in the project folder or beside app.py."
    )
    st.stop()

try:
    df = load_data(
        str(csv_path),
        csv_path.stat().st_mtime,
    )
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()


# Preserve the existing screening logic
decisions = df["screening_decision"].str.lower()

included = df[decisions.eq("include")].copy()

excluded_count = int(decisions.eq("exclude").sum())
review_count = int(decisions.eq("needs review").sum())


# ==================================================
# 4. HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Public Health Research Analytics</div>
        <h1>FGM Research in Nigeria</h1>
        <p>
            Exploring publication patterns, study locations,
            research methods and themes in PubMed-indexed literature.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="research-question">
        <div class="finding-label">Research question</div>
        <p>
            How has research on female genital mutilation (FGM)
            in Nigeria evolved over time, and what geographical
            or thematic gaps exist in the published literature?
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 5. SIDEBAR FILTERS
# ==================================================

st.sidebar.markdown(f"## Dashboard controls")
st.sidebar.caption("Filter the included studies by publication year.")

years = sorted(
    included["publication_year"]
    .dropna()
    .astype(int)
    .unique()
)

if years:
    selected_years = st.sidebar.slider(
        "Publication year range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years))),
    )

    analysis_df = included[
        included["publication_year"].between(
            selected_years[0],
            selected_years[1],
        )
    ].copy()
else:
    analysis_df = included.copy()

st.sidebar.divider()
st.sidebar.markdown("**Screening summary**")
st.sidebar.write(f"Records screened: {len(df):,}")
st.sidebar.write(f"Included: {len(included):,}")
st.sidebar.write(f"Excluded: {excluded_count:,}")
st.sidebar.write(f"Needs review: {review_count:,}")

st.sidebar.caption(
    "The year filter affects the research charts, "
    "not the screening totals."
)


# ==================================================
# 6. KEY METRICS
# ==================================================

st.markdown("## Dataset overview")
st.markdown(
    '<p class="section-intro">'
    'A snapshot of the screening results.</p>',
    unsafe_allow_html=True,
)

metrics = [
    ("Records screened", len(df)),
    ("Included studies", len(included)),
    ("Excluded records", excluded_count),
    ("Needs review", review_count),
]

metric_columns = st.columns(4)

for column, (label, value) in zip(metric_columns, metrics):
    column.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(
    f"Currently displaying charts for "
    f"{len(analysis_df):,} included records in the selected year range."
)

st.divider()

# ==================================================
# ARTICLE SCREENING & ELIGIBILITY
# ==================================================

st.markdown("## Article Screening & Eligibility")
st.markdown(
    "Explore the records screened for this review, inspect article "
    "details, and check documented screening reasons."
)

# Standardise the existing screening labels for filtering
screening_df = df.copy()
screening_df["_decision"] = (
    screening_df["screening_decision"]
    .astype(str)
    .str.strip()
    .str.lower()
)

decision_labels = {
    "include": "Included",
    "exclude": "Excluded",
    "needs review": "Needs review",
}

screening_df["_decision_label"] = (
    screening_df["_decision"].map(decision_labels)
    .fillna("Other / check label")
)

# Screening summary
s1, s2, s3 = st.columns(3)

s1.metric(
    "Included",
    int(screening_df["_decision"].eq("include").sum())
)
s2.metric(
    "Excluded",
    int(screening_df["_decision"].eq("exclude").sum())
)
s3.metric(
    "Needs review",
    int(screening_df["_decision"].eq("needs review").sum())
)

st.caption(
    "These counts cover all screened records and are not affected "
    "by the publication-year filter in the sidebar."
)

st.markdown("### Find an article")

filter_col, search_col = st.columns([1, 2])

with filter_col:
    chosen_decision = st.selectbox(
        "Screening decision",
        [
            "All decisions",
            "Included",
            "Excluded",
            "Needs review",
            "Other / check label",
        ],
        key="screening_decision_filter",
    )

with search_col:
    search_text = st.text_input(
        "Search title or PMID",
        placeholder="Enter an article title or PMID...",
        key="screening_article_search",
    )

filtered = screening_df.copy()

if chosen_decision != "All decisions":
    filtered = filtered[
        filtered["_decision_label"] == chosen_decision
    ]

search_text = search_text.strip()

if search_text:
    title_match = filtered["title"].str.contains(
        search_text, case=False, na=False, regex=False
    )

    if "pmid" in filtered.columns:
        pmid_match = filtered["pmid"].astype(str).str.contains(
            search_text, case=False, na=False, regex=False
        )
        filtered = filtered[title_match | pmid_match]
    else:
        filtered = filtered[title_match]

st.write(f"**{len(filtered):,} matching records**")

# Build a readable table
table_columns = []

for column in [
    "pmid",
    "title",
    "publication_year",
    "screening_decision",
    "study_location",
    "research_type",
]:
    if column in filtered.columns:
        table_columns.append(column)

if filtered.empty:
    st.info("No records match these filters. Try another search.")
else:
    st.dataframe(
        filtered[table_columns],
        use_container_width=True,
        hide_index=True,
    )

    # Let viewers inspect one record at a time
    st.markdown("### Inspect an article")

    article_options = {
        f"{row.get('title', 'Untitled')} | "
        f"PMID: {row.get('pmid', 'Not recorded')} | "
        f"Record {idx}": idx
        for idx, row in filtered.iterrows()
    }

    selected_article = st.selectbox(
        "Choose an article",
        options=list(article_options.keys()),
        key="screening_article_detail",
    )

    article = filtered.loc[article_options[selected_article]]

    st.markdown(f"**Title:** {article.get('title', 'Not recorded')}")
    st.write(
        f"**Decision:** "
        f"{article.get('screening_decision', 'Not recorded')}"
    )
    st.write(
        f"**Publication year:** "
        f"{article.get('publication_year', 'Not recorded')}"
    )
    st.write(f"**PMID:** {article.get('pmid', 'Not recorded')}")

    abstract = str(article.get("abstract", "")).strip()

    with st.expander("Read abstract"):
        if abstract and abstract.lower() != "nan":
            st.write(abstract)
        else:
            st.info("No abstract is available in this record.")

    # Show exclusion reason only if it exists in the dataset
    reason_columns = [
        "exclusion_reason",
        "screening_reason",
        "reason_for_exclusion",
    ]

    reason_column = next(
        (col for col in reason_columns if col in df.columns),
        None,
    )

    if reason_column:
        reason = str(article.get(reason_column, "")).strip()

        st.write("**Documented screening reason:**")
        if reason and reason.lower() != "nan":
            st.write(reason)
        else:
            st.caption("No reason recorded for this article.")

    # Link to the original record when available
    article_url = str(article.get("article_url", "")).strip()

    if article_url.startswith(("https://", "http://")):
        st.markdown(f"[Open original article record]({article_url})")

st.divider()


# ==================================================
# 7. REUSABLE CHART AND FINDING HELPERS
# ==================================================

def show_bar_chart(
    series,
    title,
    xlabel,
    ylabel="Category",
    horizontal=True,
):
    if series.empty:
        st.info("No data available for this chart.")
        return

    fig, ax = plt.subplots(figsize=(8, 4.8))

    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    if horizontal:
        series = series.sort_values()
        bars = ax.barh(
            series.index.astype(str),
            series.values,
            color=TEAL,
            height=0.68,
        )
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(axis="x", alpha=0.22)
        ax.bar_label(bars, padding=4, fontsize=9)
    else:
        bars = ax.bar(
            series.index.astype(str),
            series.values,
            color=TEAL,
            width=0.65,
        )
        ax.set_ylabel(xlabel)
        ax.set_xlabel(ylabel)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(axis="y", alpha=0.22)
        ax.bar_label(bars, padding=3, fontsize=9)

    ax.set_title(
        title,
        color=NAVY,
        fontsize=13,
        fontweight="bold",
        loc="left",
        pad=14,
    )

    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def show_finding(label, message):
    st.markdown(
        f"""
        <div class="finding-card">
            <div class="finding-label">{label}</div>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# H1: PUBLICATION TRENDS
# ==================================================

st.markdown("## 01 · Publication trends")
st.markdown(
    '<p class="section-intro">'
    'Hypothesis H1: The annual number of included publications '
    'varies over the study period.</p>',
    unsafe_allow_html=True,
)

annual = (
    analysis_df.dropna(subset=["publication_year"])
    .groupby("publication_year")
    .size()
    .sort_index()
)

if not annual.empty:
    fig, ax = plt.subplots(figsize=(10, 4.8))

    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    ax.plot(
        annual.index,
        annual.values,
        color=TEAL,
        marker="o",
        markersize=7,
        linewidth=2.5,
        markerfacecolor=WHITE,
        markeredgewidth=2,
    )

    ax.fill_between(
        annual.index,
        annual.values,
        color=TEAL,
        alpha=0.10,
    )

    ax.set_title(
        "Annual Publications on FGM in Nigeria",
        color=NAVY,
        fontsize=14,
        fontweight="bold",
        loc="left",
        pad=14,
    )
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Included articles")
    ax.set_xticks(annual.index)
    ax.tick_params(axis="x", rotation=45, colors=MUTED)
    ax.tick_params(axis="y", colors=MUTED)
    ax.grid(axis="y", alpha=0.25)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)

    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    peak_year = int(annual.idxmax())
    peak_count = int(annual.max())
    low_count = int(annual.min())

    st.markdown(
        f"**Highest annual count:** {peak_count} in {peak_year}  "
        f"| **Lowest annual count:** {low_count}"
    )

    show_finding(
        "What the data shows",
        f"Within the selected year range, the highest annual count "
        f"is {peak_count} in {peak_year}, while the lowest annual "
        f"count is {low_count}. The counts fluctuate across years.",
    )

    if int(annual.index.max()) == 2026:
        st.info(
            "2026 is an incomplete publication year. "
            "Its count should not be compared directly with "
            "completed years."
        )
else:
    st.info("No publication-year data available.")

st.caption(
    "These counts describe the included records retrieved for this "
    "project; they do not represent all FGM research."
)

st.divider()


# ==================================================
# H2: GEOGRAPHICAL DISTRIBUTION
# ==================================================

st.markdown("## 02 · Geographical distribution")
st.markdown(
    '<p class="section-intro">'
    'Hypothesis H2: Included studies are unevenly distributed '
    'across the locations reported in the dataset.</p>',
    unsafe_allow_html=True,
)

locations = analysis_df["study_location"].replace(
    "", "Not recorded"
)

unverified = locations.str.lower().str.contains(
    r"not verified|not specified|not recorded|"
    r"not classified|unknown",
    regex=True,
)

location_counts = locations[~unverified].value_counts().head(12)

left, right = st.columns([3, 2])

with left:
    show_bar_chart(
        location_counts,
        "Most frequently recorded study locations",
        "Number of articles",
        "Study location",
    )

with right:
    st.markdown("### Location coverage")

    if not location_counts.empty:
        top_location = location_counts.index[0]
        top_count = int(location_counts.iloc[0])

        show_finding(
            "Most frequent recorded label",
            f"{top_location}: {top_count} included articles.",
        )
    else:
        st.info("No verified location labels available.")

    st.write(
        "National labels such as 'Nigeria' are not directly "
        "equivalent to specific states or communities. These "
        "categories should be interpreted cautiously."
    )

unverified_count = int(unverified.sum())

st.caption(
    f"{unverified_count} included records have missing, "
    "unverified or unspecified location labels under this rule. "
    "A low count for a location does not by itself prove a research gap."
)

st.divider()


# ==================================================
# H3: RESEARCH METHODS
# ==================================================

st.markdown("## 03 · Research methods")
st.markdown(
    '<p class="section-intro">'
    'Hypothesis H3: Some research methods are more frequently '
    'represented than others.</p>',
    unsafe_allow_html=True,
)


def group_method(value):
    t = str(value).lower().strip()

    if not t or "not classified" in t:
        return "Needs classification"

    if any(x in t for x in [
        "quantitative/qualitative",
        "mixed methods",
        "mixed-methods",
    ]):
        return "Mixed methods"

    if "literature review" in t or "systematic review" in t:
        return "Literature review"

    if "quasi-experimental" in t:
        return "Quasi-experimental"

    if "qualitative" in t:
        return "Qualitative"

    if "cohort" in t or "longitudinal" in t:
        return "Longitudinal / cohort"

    if any(x in t for x in [
        "secondary", "ndhs", "dhs data", "mics data",
    ]):
        return "Secondary survey / data analysis"

    if "cross-sectional" in t:
        return "Cross-sectional quantitative"

    if "quantitative" in t:
        return "Other quantitative"

    return "Needs manual review"


analysis_df["method_group"] = analysis_df["research_type"].apply(
    group_method
)

method_counts = analysis_df["method_group"].value_counts()

left, right = st.columns([3, 2])

with left:
    show_bar_chart(
        method_counts,
        "Research methods represented",
        "Number of articles",
        "Method group",
    )

with right:
    st.markdown("### Method profile")

    if not method_counts.empty:
        show_finding(
            "Most frequent preliminary category",
            f"{method_counts.index[0]}: "
            f"{int(method_counts.iloc[0])} articles.",
        )

    st.write(
        "These groups are derived from the existing method labels. "
        "Some labels may overlap conceptually, so manual review "
        "is needed before making strong claims about method gaps."
    )

st.divider()


# ==================================================
# H4: RESEARCH THEMES
# ==================================================

st.markdown("## 04 · Research themes")
st.markdown(
    '<p class="section-intro">'
    'Hypothesis H4: Included studies cover multiple research '
    'themes, and their representation may vary over time.</p>',
    unsafe_allow_html=True,
)

st.warning(
    "Theme counts are exploratory keyword matches, not validated "
    "content analysis. One article may match multiple themes, "
    "and keyword matches do not establish an article's main focus."
)


def assign_theme(row):
    text = (
        f"{row.get('title', '')} "
        f"{row.get('abstract', '')}"
    ).lower()

    themes = {
        "Prevalence and determinants": [
            "prevalence", "associated factors", "determinants",
            "risk factors", "national survey",
        ],
        "Knowledge and attitudes": [
            "knowledge", "attitude", "perception", "beliefs",
        ],
        "Health consequences": [
            "complications", "health consequences", "obstetric",
            "sexual health", "mental health",
        ],
        "Culture and social factors": [
            "social norm", "cultural", "community", "tradition",
        ],
        "Interventions and prevention": [
            "intervention", "prevention", "programme",
            "program", "campaign", "abandonment",
        ],
        "Policy and law": [
            "legislation", "legal", "policy", "law", "enforcement",
        ],
    }

    matches = [
        theme
        for theme, keywords in themes.items()
        if any(keyword in text for keyword in keywords)
    ]

    return matches if matches else ["Manual review needed"]


analysis_df["preliminary_themes"] = analysis_df.apply(
    assign_theme,
    axis=1,
)

theme_rows = [
    (theme, row["publication_year"], row["title"])
    for _, row in analysis_df.iterrows()
    for theme in row["preliminary_themes"]
    if theme != "Manual review needed"
]

if theme_rows:
    theme_data = pd.DataFrame(
        theme_rows,
        columns=["theme", "publication_year", "title"],
    )

    theme_counts = (
        theme_data["theme"]
        .value_counts()
        .sort_values()
    )

    show_bar_chart(
        theme_counts,
        "Preliminary keyword-based research themes",
        "Articles matching theme",
        "Research theme",
    )

    st.caption(
        "Theme counts can exceed the number of included articles "
        "because an article may match more than one theme."
    )
else:
    st.info(
        "No theme keyword matches were found in the selected "
        "year range. Review article titles and abstracts manually."
    )

manual_review_count = int(
    analysis_df["preliminary_themes"].apply(
        lambda themes: "Manual review needed" in themes
    ).sum()
)

show_finding(
    "Manual review needed",
    f"{manual_review_count} articles in the selected year range "
    "did not match the current keyword rules. Other articles may "
    "also need review to verify their assigned themes.",
)

with st.expander("Review article-level theme assignments"):
    theme_table = analysis_df[
        ["publication_year", "title", "preliminary_themes"]
    ].copy()

    theme_table["preliminary_themes"] = theme_table[
        "preliminary_themes"
    ].apply(lambda themes: "; ".join(themes))

    st.dataframe(
        theme_table,
        use_container_width=True,
        hide_index=True,
    )

st.divider()


# ==================================================
# 8. DATA QUALITY AND LIMITATIONS
# ==================================================

st.markdown("## Dataset and limitations")

st.markdown(
    '<p class="section-intro">'
    'Important context for interpreting these descriptive results.</p>',
    unsafe_allow_html=True,
)

limit_left, limit_right = st.columns(2)

with limit_left:
    st.markdown("### Dataset")
    st.write(f"**Records screened:** {len(df):,}")
    st.write(f"**Included records:** {len(included):,}")
    st.write(f"**Excluded records:** {excluded_count:,}")
    st.write(f"**Records needing review:** {review_count:,}")

with limit_right:
    st.markdown("### Interpretation cautions")
    st.markdown(
        """
        - Results depend on the PubMed search strategy and screening criteria.
        - Publication counts do not measure FGM prevalence in Nigeria.
        - Geographic labels use varying levels of detail.
        - Research-method groupings need consistent classification.
        - Keyword-based themes require manual validation.
        - The 2026 publication year is incomplete.
        """
    )

st.download_button(
    label="Download included records as CSV",
    data=included.to_csv(index=False).encode("utf-8"),
    file_name="fgm_included_articles.csv",
    mime="text/csv",
    use_container_width=False,
)

st.caption(
    "Source: Project screening dataset of PubMed-indexed records. "
    "Findings describe this dataset and should not be generalized "
    "to all FGM research without further validation."
)

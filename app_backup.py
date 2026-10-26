
import os
import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------
st.set_page_config(
    page_title="FGM Research in Nigeria",
    page_icon="📊",
    layout="wide"
)

st.title("FGM Research in Nigeria")
st.caption(
    "A descriptive analysis of PubMed-indexed literature | 2015–2026"
)

st.markdown("""
**Research question**

How has research on female genital mutilation (FGM) in Nigeria
evolved over time, and what geographical or thematic gaps exist
in the published literature?
""")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "fgm_articles_screening.csv",
        dtype={"pmid": str}
    )
    df.columns = df.columns.str.strip()

    required = [
        "publication_year",
        "screening_decision",
        "study_location",
        "research_type",
        "title",
        "abstract"
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df["publication_year"] = pd.to_numeric(
        df["publication_year"], errors="coerce"
    )

    for col in [
        "screening_decision", "study_location",
        "research_type", "title", "abstract"
    ]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

# Adjust this if your CSV uses different decision labels.
included = df[
    df["screening_decision"].str.lower().eq("include")
].copy()

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.sidebar.header("Dashboard filters")

years = sorted(
    included["publication_year"].dropna().astype(int).unique()
)

if years:
    selected_years = st.sidebar.slider(
        "Publication year range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years)))
    )

    analysis_df = included[
        included["publication_year"].between(
            selected_years[0], selected_years[1]
        )
    ].copy()
else:
    analysis_df = included.copy()

st.sidebar.caption(
    "Charts use included studies unless otherwise stated."
)

# --------------------------------------------------
# KEY METRICS
# --------------------------------------------------
c1, c2, c3, c4 = st.columns(4)

c1.metric("Records screened", f"{len(df):,}")
c2.metric("Included studies", f"{len(included):,}")
c3.metric("Excluded records", f"{(df['screening_decision'].str.lower() == 'exclude').sum():,}")
c4.metric("Needs review", f"{(df['screening_decision'].str.lower() == 'needs review').sum():,}")

st.divider()

# --------------------------------------------------
# CHART HELPER
# --------------------------------------------------
def show_bar_chart(series, title, xlabel, ylabel="Category",
                   horizontal=True):
    if series.empty:
        st.info("No data available for this chart.")
        return

    fig, ax = plt.subplots(figsize=(8, 4.5))

    if horizontal:
        series = series.sort_values()
        series.plot(kind="barh", ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    else:
        series.plot(kind="bar", ax=ax)
        ax.set_ylabel(xlabel)
        ax.set_xlabel(ylabel)
        plt.xticks(rotation=45, ha="right")

    ax.set_title(title)
    ax.grid(axis="x" if horizontal else "y", alpha=0.25)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# --------------------------------------------------
# H1: PUBLICATION TRENDS
# --------------------------------------------------
st.header("1. Publication trends over time")

st.markdown("""
**Research question:** How has the number of included PubMed-indexed
FGM studies concerning Nigeria changed over time?

**Hypothesis H1:** The annual number of included publications varies
over the study period.
""")

annual = (
    analysis_df.dropna(subset=["publication_year"])
    .groupby("publication_year")
    .size()
    .sort_index()
)

if not annual.empty:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(annual.index, annual.values, marker="o")
    ax.set_title("Annual Publications on FGM in Nigeria")
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Number of included articles")
    ax.set_xticks(annual.index)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    peak_year = int(annual.idxmax())
    peak_count = int(annual.max())
    low_count = int(annual.min())

    st.markdown(
        f"**What the data shows:** Within the selected year range, "
        f"the highest annual count is {peak_count} in {peak_year}; "
        f"the lowest is {low_count}. "
        "Use the chart to examine fluctuations across years."
    )

    if int(annual.index.max()) == 2026:
        st.info(
            "2026 is an incomplete publication year. "
            "Its count should not be compared directly with "
            "completed years without this limitation."
        )
else:
    st.info("No publication-year data available.")

st.caption(
    "Interpretation: These counts describe the included records "
    "retrieved for this project, not all FGM research published worldwide."
)

st.divider()

# --------------------------------------------------
# H2: STUDY LOCATIONS
# --------------------------------------------------
st.header("2. Geographical distribution")

st.markdown("""
**Research question:** Which Nigerian locations are represented
in the included studies?

**Hypothesis H2:** Included studies are unevenly distributed
across the locations reported in the dataset.
""")

locations = analysis_df["study_location"].replace(
    "", "Not recorded"
)

unverified = locations.str.lower().str.contains(
    r"not verified|not specified|not recorded|not classified|unknown",
    regex=True
)

location_counts = locations[~unverified].value_counts().head(12)

left, right = st.columns([3, 2])

with left:
    show_bar_chart(
        location_counts,
        "Most frequently recorded study locations",
        "Number of articles",
        "Study location"
    )

with right:
    st.markdown("**What the data shows**")
    if not location_counts.empty:
        top_location = location_counts.index[0]
        top_count = int(location_counts.iloc[0])
        st.write(
            f"The most frequent recorded location is "
            f"**{top_location}** ({top_count} articles)."
        )

    st.write(
        "Location labels vary in detail. A national label such as "
        "'Nigeria' is not directly equivalent to a specific state "
        "or community."
    )

unverified_count = int(unverified.sum())
st.caption(
    f"{unverified_count} included records have missing, unverified, "
    "or unspecified location labels under this rule. Review these "
    "records before drawing conclusions about geographical gaps."
)

st.divider()

# --------------------------------------------------
# H3: RESEARCH METHODS
# --------------------------------------------------
st.header("3. Research methods")

st.markdown("""
**Research question:** Which research methods are most commonly
represented in the included studies?

**Hypothesis H3:** Some research methods appear more frequently
than others.
""")

def group_method(value):
    t = value.lower()

    if not t or "not classified" in t:
        return "Needs classification"
    if "quantitative/qualitative" in t or "mixed methods" in t or "mixed-methods" in t:
        return "Mixed methods"
    if "literature review" in t or "systematic review" in t:
        return "Literature review"
    if "qualitative" in t:
        return "Qualitative"
    if "quasi-experimental" in t:
        return "Quasi-experimental"
    if "cohort" in t or "longitudinal" in t:
        return "Longitudinal / cohort"
    if "secondary" in t or "ndhs" in t or "dhs data" in t or "mics data" in t:
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
        "Method group"
    )

with right:
    st.markdown("**What the data shows**")
    if not method_counts.empty:
        st.write(
            f"The most frequent preliminary category is "
            f"**{method_counts.index[0]}** "
            f"({int(method_counts.iloc[0])} articles)."
        )
    st.write(
        "Method groups are based on text labels and are provisional. "
        "Some studies may fit more than one methodological description."
    )

st.divider()

# --------------------------------------------------
# H4: RESEARCH THEMES
# --------------------------------------------------
st.header("4. Research themes")

st.markdown("""
**Research question:** What topics are represented in the included
literature, and how does their representation vary over time?

**Hypothesis H4:** The included studies cover multiple research
themes, and the frequency of these themes may differ over time.
""")

st.warning(
    "Theme coding is not yet validated. Titles and abstracts need "
    "to be reviewed using a consistent coding framework before "
    "we can present theme counts as findings."
)

# Exploratory keyword coding only; categories may overlap conceptually.
def assign_theme(row):
    text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()

    themes = {
        "Prevalence and determinants": [
            "prevalence", "associated factors", "determinants",
            "risk factors", "national survey"
        ],
        "Knowledge and attitudes": [
            "knowledge", "attitude", "perception", "beliefs"
        ],
        "Health consequences": [
            "complications", "health consequences", "obstetric",
            "sexual health", "mental health"
        ],
        "Culture and social factors": [
            "social norm", "cultural", "community", "tradition"
        ],
        "Interventions and prevention": [
            "intervention", "prevention", "programme", "program",
            "campaign", "abandonment"
        ],
        "Policy and law": [
            "legislation", "legal", "policy", "law", "enforcement"
        ],
    }

    matches = [
        theme for theme, keywords in themes.items()
        if any(keyword in text for keyword in keywords)
    ]

    return "; ".join(matches) if matches else "Manual review needed"


analysis_df["preliminary_themes"] = analysis_df.apply(
    assign_theme, axis=1
)

st.write(
    f"**Articles needing manual theme review:** "
    f"{analysis_df['preliminary_themes'].eq('Manual review needed').sum()} "
    "in the selected year range."
)

with st.expander("View preliminary keyword-based theme assignments"):
    st.dataframe(
        analysis_df[
            ["publication_year", "title", "preliminary_themes"]
        ],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# --------------------------------------------------
# DATA QUALITY AND DOWNLOAD
# --------------------------------------------------
st.header("Dataset and limitations")

st.write(
    f"The current dataset contains {len(df)} screened records, "
    f"of which {len(included)} are marked Include."
)

st.write("""
- The results depend on the search strategy, screening criteria,
  and records retrieved from PubMed.
- Publication counts do not measure FGM prevalence in Nigeria.
- Inconsistent or unverified location labels can obscure geographic
  patterns.
- Research-method groupings and keyword-based themes require review.
- 2026 publication counts are incomplete.
""")

st.download_button(
    "Download included records as CSV",
    data=included.to_csv(index=False).encode("utf-8"),
    file_name="fgm_included_articles.csv",
    mime="text/csv"
)

st.success(
    "Dashboard loaded. Review the charts and classification caveats "
    "before reporting the findings."
)


# VISUALIZATION 1: Annual publication trend

import matplotlib.pyplot as plt


# Count included articles only
included = df[
    df["screening_decision"].str.strip().str.lower() == "include"
].copy()

included["publication_year"] = pd.to_numeric(
    included["publication_year"], errors="coerce"
)

annual_counts = (
    included.dropna(subset=["publication_year"])
    .groupby("publication_year")
    .size()
    .sort_index()
)

print(annual_counts)


plt.figure(figsize=(10, 5))

plt.plot(
    annual_counts.index,
    annual_counts.values,
    marker="o"
)

plt.title("Annual Publications on FGM in Nigeria")
plt.xlabel("Publication Year")
plt.ylabel("Number of Included Articles")
plt.xticks(annual_counts.index, rotation=45)
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

# Save the chart for GitHub

# --------------------------------------------------
# EXPORT ALL FOUR VISUALIZATIONS FOR GITHUB
# --------------------------------------------------

import os

# Save images in the same folder as this script
OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Visualizations"
)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_figure(fig, filename):
    """Save a chart as a high-resolution PNG."""
    fig.tight_layout()
    fig.savefig(
        os.path.join(OUTPUT_DIR, filename),
        dpi=300,
        bbox_inches="tight"
    )
    plt.close(fig)


# Use all included studies, not just the dashboard's
# currently selected year range.
export_df = included.copy()

# 1. ANNUAL PUBLICATION TREND
year_data = export_df.dropna(
    subset=["publication_year"]
).copy()

year_data["publication_year"] = (
    year_data["publication_year"].astype(int)
)

annual_counts = (
    year_data.groupby("publication_year")
    .size()
    .sort_index()
)

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    annual_counts.index,
    annual_counts.values,
    marker="o"
)
ax.set_title("Annual Publications on FGM in Nigeria")
ax.set_xlabel("Publication Year")
ax.set_ylabel("Number of Included Articles")
ax.set_xticks(annual_counts.index)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.3)
save_figure(fig, "publication_trend.png")


# 2. RESEARCH METHODS
def export_method_group(value):
    t = str(value).strip().lower()

    if not t or "not classified" in t:
        return "Needs classification"
    if any(x in t for x in [
        "mixed methods", "mixed-methods",
        "quantitative/qualitative"
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
        "secondary", "ndhs", "dhs data", "mics data"
    ]):
        return "Secondary survey / data analysis"
    if "cross-sectional" in t:
        return "Cross-sectional quantitative"
    if "quantitative" in t:
        return "Other quantitative"
    return "Needs manual review"


method_counts = (
    export_df["research_type"]
    .apply(export_method_group)
    .value_counts()
)

fig, ax = plt.subplots(figsize=(10, 6))
method_counts.sort_values().plot(
    kind="barh", ax=ax
)
ax.set_title("Research Methods in Included FGM Studies")
ax.set_xlabel("Number of Included Articles")
ax.set_ylabel("Research Method")
ax.grid(axis="x", alpha=0.25)
save_figure(fig, "research_methods.png")


# 3. STUDY LOCATIONS
location_data = export_df["study_location"].replace(
    "", "Not recorded"
)

unverified = location_data.str.lower().str.contains(
    r"not verified|not specified|not recorded|"
    r"not classified|unknown",
    regex=True
)

location_counts = (
    location_data[~unverified]
    .value_counts()
    .head(12)
)

fig, ax = plt.subplots(figsize=(10, 7))

if not location_counts.empty:
    location_counts.sort_values().plot(
        kind="barh", ax=ax
    )

ax.set_title("Most Frequently Recorded Study Locations")
ax.set_xlabel("Number of Included Articles")
ax.set_ylabel("Study Location")
ax.grid(axis="x", alpha=0.25)
save_figure(fig, "study_locations.png")


# 4. PRELIMINARY RESEARCH THEMES
def export_themes(row):
    text = (
        str(row.get("title", "")) + " " +
        str(row.get("abstract", ""))
    ).lower()

    theme_keywords = {
        "Prevalence and determinants": [
            "prevalence", "associated factors",
            "determinants", "risk factors",
            "national survey"
        ],
        "Knowledge and attitudes": [
            "knowledge", "attitude",
            "perception", "beliefs"
        ],
        "Health consequences": [
            "complications", "health consequences",
            "obstetric", "sexual health", "mental health"
        ],
        "Culture and social factors": [
            "social norm", "cultural",
            "community", "tradition"
        ],
        "Interventions and prevention": [
            "intervention", "prevention",
            "programme", "program", "campaign",
            "abandonment"
        ],
        "Policy and law": [
            "legislation", "legal",
            "policy", "law", "enforcement"
        ],
    }

    return [
        theme for theme, keywords in theme_keywords.items()
        if any(keyword in text for keyword in keywords)
    ]


theme_totals = {}

for _, article in export_df.iterrows():
    for theme in export_themes(article):
        theme_totals[theme] = theme_totals.get(theme, 0) + 1

theme_counts = pd.Series(
    theme_totals, dtype="int64"
).sort_values()

fig, ax = plt.subplots(figsize=(10, 6))

if not theme_counts.empty:
    theme_counts.plot(kind="barh", ax=ax)

ax.set_title("Preliminary Research Themes in FGM Studies")
ax.set_xlabel("Articles Matching Theme")
ax.set_ylabel("Research Theme")
ax.grid(axis="x", alpha=0.25)
save_figure(fig, "research_themes.png")


# Confirm which files were created
st.success(
    "Four visualizations exported to: " + OUTPUT_DIR
)

st.write("Saved chart files:")
for filename in [
    "publication_trend.png",
    "research_methods.png",
    "study_locations.png",
    "research_themes.png"
]:
    st.write("- " + filename)


from pathlib import Path
import re

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ==================================================
# 1. PAGE CONFIGURATION AND CONSTANTS
# ==================================================

st.set_page_config(
    page_title="FGM Research in Nigeria",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

NAVY = "#15344B"
TEAL = "#167D8D"
TEAL_LIGHT = "#E5F3F4"
BG = "#F4F7FA"
TEXT = "#243746"
MUTED = "#647789"
BORDER = "#DFE7ED"
WHITE = "#FFFFFF"

YEAR_START, YEAR_END = 2015, 2026

ALL_ZONES = ["North-Central", "North-East", "North-West",
             "South-East", "South-South", "South-West"]

ZONE_MAPPING = {
    "South-Eastern Nigeria": "South-East",
    "South-West Nigeria": "South-West",
    "North-Central Nigeria": "North-Central",
    "North-West Nigeria": "North-West",
}

THEME_KEYWORDS = {
    "Socio-cultural factors": [
        r"\bcultur", r"\btradition", r"\breligio", r"\bbelief",
        r"\battitude", r"\bperception", r"\bsocial norm",
        r"\bsocial rejection", r"\bsubjective norm", r"\bheritage",
        r"\bstigma"],
    "Prevention and interventions": [
        r"\bprevent", r"\bintervention", r"\belimination",
        r"\babandonment", r"\bdiscontinu", r"\bawareness",
        r"\bpolicy", r"\blegislation", r"\bprohibition",
        r"\bproject", r"\bimpact of"],
    "Prevalence and determinants": [
        r"\bprevalence", r"\bdeterminant", r"\bcorrelate",
        r"\brisk factor", r"\bsociodemographic", r"\bsocio-economic",
        r"\bdistribution", r"\bvariation"],
    "Health consequences": [
        r"\bhealth consequence", r"\bcomplication", r"\bobstetric",
        r"\bchildbirth", r"\bsexual function", r"\bsexual behavio(u)?r",
        r"\bpsychological", r"\binfertility", r"\bpregnancy",
        r"\bhuman papilloma", r"\bhpv", r"\bdisability", r"\bmorbidity"],
}

OUTPUT_DIR = Path(__file__).resolve().parent   # the Visualizations folder
# To use a subfolder instead: OUTPUT_DIR = Path(__file__).resolve().parent / "charts"


def save_fig(fig, filename):
    """Save a matplotlib figure as a PNG; never crash the dashboard on failure."""
    try:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUTPUT_DIR / filename, dpi=200,
                    bbox_inches="tight", facecolor=fig.get_facecolor())
    except Exception as error:
        st.warning(f"Could not save {filename}: {error}")

# ==================================================
# 2. ANALYSIS HELPERS (same logic as the EDA notebook)
# ==================================================

def group_research_type(value):
    t = str(value).strip().casefold()
    if ("mixed method" in t
            or "quantitative/qualitative" in t
            or "qualitative/quantitative" in t
            or ("survey" in t and "fgd" in t)):
        return "Mixed methods"
    if "literature review" in t:
        return "Literature review"
    if "qualitative" in t:
        return "Qualitative"
    if "quantitative" in t:
        return "Quantitative"
    return "Needs manual review"


def classify_themes(title, abstract):
    text = f"{title} {abstract}".casefold()
    return [theme for theme, patterns in THEME_KEYWORDS.items()
            if any(re.search(p, text) for p in patterns)]


def year_counts(data, start, end):
    """Counts per year, including years with zero articles."""
    return (data["publication_year"].dropna().astype(int)
            .value_counts().sort_index()
            .reindex(range(start, end + 1), fill_value=0))


def trend_summary(counts):
    half = len(counts) // 2
    if half < 1:
        return None
    a, b = counts.iloc[:half], counts.iloc[-half:]
    return {
        "first_range": f"{a.index[0]}-{a.index[-1]}",
        "first_total": int(a.sum()),
        "second_range": f"{b.index[0]}-{b.index[-1]}",
        "second_total": int(b.sum()),
    }


def location_level(label):
    low = label.casefold()
    if label in ZONE_MAPPING:
        return "Zone-specific"
    if low == "national":
        return "National"
    if "multi-country" in low:
        return "Multi-country"
    if low == "northern nigeria":
        return "Northern Nigeria (zone unclear)"
    if low == "not applicable":
        return "Not applicable"
    if "locality not specified" in low:
        return "Nigeria (locality unspecified)"
    return "Other / missing"


def add_geography(data):
    out = data.copy()
    loc = out["study_location"].astype(str).str.strip()
    out["geopolitical_zone"] = loc.map(ZONE_MAPPING)
    out["location_level"] = loc.apply(location_level)
    return out


def zone_counts(data):
    return (data["geopolitical_zone"].dropna().value_counts()
            .reindex(ALL_ZONES, fill_value=0))


# ==================================================
# 3. CUSTOM DASHBOARD STYLING
# ==================================================

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {BG}; color: {TEXT}; }}
    [data-testid="stHeader"] {{ background-color: transparent; }}
    [data-testid="stSidebar"] {{
        background-color: {WHITE};
        border-right: 1px solid {BORDER};
    }}
    .block-container {{
        padding-top: 2rem; padding-bottom: 3rem; max-width: 1500px;
    }}
    h1, h2, h3 {{ color: {NAVY} !important; letter-spacing: -0.3px; }}
    p, li, label {{ color: {TEXT}; }}
    .hero {{
        background: linear-gradient(120deg, {NAVY}, {TEAL});
        padding: 30px 32px; border-radius: 16px;
        margin-bottom: 22px; color: white;
    }}
    .hero h1 {{
        color: white !important; margin: 0 0 8px 0; font-size: 2.15rem;
    }}
    .hero p {{ color: #E1F0F3 !important; margin: 0; font-size: 1rem; }}
    .eyebrow {{
        text-transform: uppercase; letter-spacing: 1.5px;
        font-size: 0.75rem; font-weight: 700; color: #BDE6E8;
        margin-bottom: 8px;
    }}
    .research-question {{
        background: {WHITE}; border: 1px solid {BORDER};
        border-left: 5px solid {TEAL}; padding: 20px 24px;
        border-radius: 10px; margin-bottom: 24px;
    }}
    .research-question p {{ margin-bottom: 0; }}
    .section-intro {{
        color: {MUTED}; font-size: 0.96rem;
        margin-top: -8px; margin-bottom: 18px;
    }}
    .metric-card {{
        background: {WHITE}; border: 1px solid {BORDER};
        border-top: 4px solid {TEAL}; border-radius: 12px;
        padding: 18px 20px; min-height: 112px;
    }}
    .metric-label {{
        color: {MUTED}; font-size: 0.83rem; font-weight: 600;
        margin-bottom: 10px;
    }}
    .metric-value {{
        color: {NAVY}; font-size: 2rem; font-weight: 750;
        line-height: 1.15;
    }}
    .finding-card {{
        background: {WHITE}; border: 1px solid {BORDER};
        border-radius: 12px; padding: 20px; margin: 8px 0 18px 0;
    }}
    .finding-label {{
        color: {TEAL}; font-size: 0.76rem; font-weight: 750;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 8px;
    }}
    .finding-card p {{ margin-bottom: 0; line-height: 1.65; }}
    div[data-testid="stDownloadButton"] button {{
        background-color: {TEAL}; color: white; border: 0;
        border-radius: 8px; font-weight: 600;
    }}
    div[data-testid="stDownloadButton"] button:hover {{
        background-color: {NAVY}; color: white;
    }}
    div[data-testid="stAlert"] {{ border-radius: 10px; }}
    hr {{ border-color: {BORDER}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 4. LOAD THE DATASET
# ==================================================

@st.cache_data
def load_data(csv_path, modified_time):
    data = pd.read_csv(csv_path, dtype={"pmid": str})
    data.columns = data.columns.str.strip()

    required = ["publication_year", "screening_decision", "study_location",
                "research_type", "title", "abstract"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data["publication_year"] = pd.to_numeric(
        data["publication_year"], errors="coerce")

    for column in ["screening_decision", "study_location",
                   "research_type", "title", "abstract"]:
        data[column] = data[column].fillna("").astype(str).str.strip()

    data["study_location"] = data["study_location"].replace(
        {"Nationwide (Multi-country)": "Multi-country"})
    return data


possible_paths = [
    Path.cwd() / "cleaneddata.csv",
    Path(__file__).resolve().parent / "cleaneddata.csv",
    Path(__file__).resolve().parent.parent / "cleaneddata.csv",
]
csv_path = next((p for p in possible_paths if p.is_file()), None)

if csv_path is None:
    st.error("Could not find cleaneddata.csv. "
             "Place it in the project folder or beside dashboard.py.")
    st.stop()

try:
    df = load_data(str(csv_path), csv_path.stat().st_mtime)
except Exception as error:
    st.error(f"Could not load the dataset: {error}")
    st.stop()

decisions = df["screening_decision"].str.lower()
included = df[decisions.eq("include")].copy()
excluded_count = int(decisions.eq("exclude").sum())
review_count = int(decisions.eq("needs review").sum())


# ==================================================
# 5. HEADER
# ==================================================

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Public Health Research Analytics</div>
        <h1>FGM Research in Nigeria</h1>
        <p>Exploring publication patterns, study locations,
        research methods and themes in PubMed-indexed literature.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="research-question">
        <div class="finding-label">Research question</div>
        <p>How has research on female genital mutilation (FGM)
        in Nigeria evolved over time, and what geographical
        or thematic gaps exist in the published literature?</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# 6. SIDEBAR FILTERS
# ==================================================

st.sidebar.markdown("## Dashboard controls")
st.sidebar.caption("Filter the included studies by publication year.")

years = sorted(included["publication_year"].dropna().astype(int).unique())

if len(years) > 1:
    selected_years = st.sidebar.slider(
        "Publication year range",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years))),
    )
    analysis_df = included[
        included["publication_year"].between(*selected_years)
    ].copy()
else:
    selected_years = ((int(years[0]), int(years[0])) if years
                      else (YEAR_START, YEAR_END))
    analysis_df = included.copy()

st.sidebar.divider()
st.sidebar.markdown("**Screening summary**")
st.sidebar.write(f"Records screened: {len(df):,}")
st.sidebar.write(f"Included: {len(included):,}")
st.sidebar.write(f"Excluded: {excluded_count:,}")
st.sidebar.write(f"Needs review: {review_count:,}")
st.sidebar.caption(
    "The year filter affects the research charts, not the screening totals.")


# ==================================================
# 7. KEY METRICS
# ==================================================

st.markdown("## Dataset overview")
st.markdown('<p class="section-intro">A snapshot of the screening results.</p>',
            unsafe_allow_html=True)

metrics = [
    ("Records screened", len(df)),
    ("Included studies", len(included)),
    ("Excluded records", excluded_count),
    ("Needs review", review_count),
]

for column, (label, value) in zip(st.columns(4), metrics):
    column.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value:,}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.caption(f"Currently displaying charts for {len(analysis_df):,} "
           "included records in the selected year range.")
st.divider()


# ==================================================
# 8. ARTICLE SCREENING AND ELIGIBILITY
# ==================================================

st.markdown("## Article Screening & Eligibility")
st.markdown("Explore the records screened for this review, inspect article "
            "details, and check documented screening reasons.")

screening_df = df.copy()
screening_df["_decision"] = (
    screening_df["screening_decision"].astype(str).str.strip().str.lower())

decision_labels = {
    "include": "Included",
    "exclude": "Excluded",
    "needs review": "Needs review",
}
screening_df["_decision_label"] = (
    screening_df["_decision"].map(decision_labels)
    .fillna("Other / check label"))

s1, s2, s3 = st.columns(3)
s1.metric("Included", int(screening_df["_decision"].eq("include").sum()))
s2.metric("Excluded", int(screening_df["_decision"].eq("exclude").sum()))
s3.metric("Needs review",
          int(screening_df["_decision"].eq("needs review").sum()))
st.caption("These counts cover all screened records and are not affected "
           "by the publication-year filter in the sidebar.")

st.markdown("### Find an article")
filter_col, search_col = st.columns([1, 2])

with filter_col:
    chosen_decision = st.selectbox(
        "Screening decision",
        ["All decisions", "Included", "Excluded",
         "Needs review", "Other / check label"],
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
    filtered = filtered[filtered["_decision_label"] == chosen_decision]

search_text = search_text.strip()
if search_text:
    title_match = filtered["title"].str.contains(
        search_text, case=False, na=False, regex=False)
    pmid_match = filtered["pmid"].astype(str).str.contains(
        search_text, case=False, na=False, regex=False)
    filtered = filtered[title_match | pmid_match]

st.write(f"**{len(filtered):,} matching records**")

table_columns = [c for c in ["pmid", "title", "publication_year",
                             "screening_decision", "study_location",
                             "research_type"] if c in filtered.columns]

if filtered.empty:
    st.info("No records match these filters. Try another search.")
else:
    st.dataframe(filtered[table_columns], hide_index=True)

    st.markdown("### Inspect an article")

    article_options = {
        f"{row.get('title', 'Untitled')} | "
        f"PMID: {row.get('pmid', 'Not recorded')} | Record {idx}": idx
        for idx, row in filtered.iterrows()
    }

    selected_article = st.selectbox(
        "Choose an article",
        options=list(article_options.keys()),
        key="screening_article_detail",
    )
    article = filtered.loc[article_options[selected_article]]

    st.markdown(f"**Title:** {article.get('title', 'Not recorded')}")
    st.write(f"**Decision:** {article.get('screening_decision', 'Not recorded')}")
    st.write(f"**Publication year:** "
             f"{article.get('publication_year', 'Not recorded')}")
    st.write(f"**PMID:** {article.get('pmid', 'Not recorded')}")

    abstract = str(article.get("abstract", "")).strip()
    with st.expander("Read abstract"):
        if abstract and abstract.lower() != "nan":
            st.write(abstract)
        else:
            st.info("No abstract is available in this record.")

    reason_column = next(
        (c for c in ["exclusion_reason", "screening_reason",
                     "reason_for_exclusion"] if c in df.columns), None)
    if reason_column:
        reason = str(article.get(reason_column, "")).strip()
        st.write("**Documented screening reason:**")
        if reason and reason.lower() != "nan":
            st.write(reason)
        else:
            st.caption("No reason recorded for this article.")

    article_url = str(article.get("article_url", "")).strip()
    if article_url.startswith(("https://", "http://")):
        st.markdown(f"[Open original article record]({article_url})")

st.divider()


# ==================================================
# 9. CHART AND FINDING HELPERS
# ==================================================

def style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(BORDER)
    ax.spines["bottom"].set_color(BORDER)
    ax.tick_params(colors=MUTED, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)


def show_bar_chart(series, title, xlabel, ylabel="Category", filename=None):
    if series.empty:
        st.info("No data available for this chart.")
        return

    fig, ax = plt.subplots(figsize=(8, 4.8))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    series = series.sort_values()
    bars = ax.barh(series.index.astype(str), series.values,
                   color=TEAL, height=0.68)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(axis="x", alpha=0.22)
    ax.bar_label(bars, padding=4, fontsize=9)
    ax.set_title(title, color=NAVY, fontsize=13, fontweight="bold",
                 loc="left", pad=14)
    style_axes(ax)

    fig.tight_layout()
    if filename:
        save_fig(fig, filename)
    st.pyplot(fig)
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
# 10. H1: PUBLICATION TRENDS
# ==================================================

st.markdown("## 01 · Publication trends")
st.markdown(
    '<p class="section-intro">Hypothesis H1: FGM research publications in '
    'Nigeria have increased over the study period.</p>',
    unsafe_allow_html=True,
)

annual = year_counts(analysis_df, selected_years[0], selected_years[1])

if annual.sum() > 0:
    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    ax.plot(annual.index, annual.values, color=TEAL, marker="o",
            markersize=7, linewidth=2.5, markerfacecolor=WHITE,
            markeredgewidth=2)
    ax.fill_between(annual.index, annual.values, color=TEAL, alpha=0.10)
    ax.set_title("Annual Publications on FGM in Nigeria", color=NAVY,
                 fontsize=14, fontweight="bold", loc="left", pad=14)
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Included articles")
    ax.set_xticks(annual.index)
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="y", alpha=0.25)
    style_axes(ax)

    fig.tight_layout()
    save_fig(fig, "h1_publication_trends.png")
    st.pyplot(fig)
    plt.close(fig)


    peak_count, low_count = int(annual.max()), int(annual.min())
    peak_years = ", ".join(str(y) for y in annual[annual == peak_count].index)
    low_years = ", ".join(str(y) for y in annual[annual == low_count].index)

    message = (f"Highest annual count: {peak_count} ({peak_years}). "
               f"Lowest annual count: {low_count} ({low_years}).")
    ts = trend_summary(annual)
    if ts:
        message += (f" {ts['first_range']}: {ts['first_total']} articles; "
                    f"{ts['second_range']}: {ts['second_total']} articles.")
    show_finding("What the data shows", message)

    if selected_years[1] == YEAR_END:
        st.info(f"{YEAR_END} is a partial publication year. Its count "
                "should not be compared directly with completed years.")
else:
    st.info("No publication-year data available.")

st.caption("These counts describe the included records retrieved for this "
           "project; they do not represent all FGM research.")
st.divider()


# ==================================================
# 11. H2: GEOGRAPHICAL DISTRIBUTION
# ==================================================

st.markdown("## 02 · Geographical distribution")
st.markdown(
    '<p class="section-intro">Hypothesis H2: FGM research publications are '
    'geographically concentrated in certain geopolitical zones rather than '
    'evenly distributed across Nigeria.</p>',
    unsafe_allow_html=True,
)

geo_df = add_geography(analysis_df)
zones = zone_counts(geo_df)
levels = geo_df["location_level"].value_counts()

left, right = st.columns([3, 2])

with left:
    show_bar_chart(zones, "Studies by explicitly identified geopolitical zone",
                   "Number of articles", "Geopolitical zone",filename="h2_geopolitical_zones.png")

with right:
    st.markdown("### Location coverage")
    show_bar_chart(levels, "Studies by location level",
                   "Number of articles", "Level", filename="h2_location_levels.png")
    empty_zones = [z for z in ALL_ZONES if zones[z] == 0]
    if empty_zones and len(geo_df):
        show_finding("Zones with no zone-specific studies",
                     ", ".join(empty_zones) + ".")

st.caption(
    f"{int(zones.sum())} of {len(geo_df)} included studies name a specific "
    "geopolitical zone. National, multi-country, 'Northern Nigeria' and "
    "unspecified labels are kept separate rather than assigned to a zone. "
    "A low count does not by itself prove a research gap.")
st.divider()


# ==================================================
# 12. H3: RESEARCH METHODS
# ==================================================

st.markdown("## 03 · Research methods")
st.markdown(
    '<p class="section-intro">Hypothesis H3: Quantitative research '
    'methodologies are the most commonly used approaches in FGM-related '
    'studies.</p>',
    unsafe_allow_html=True,
)

analysis_df["method_group"] = analysis_df["research_type"].apply(
    group_research_type)
method_counts = analysis_df["method_group"].value_counts()

left, right = st.columns([3, 2])

with left:
    show_bar_chart(method_counts, "Research methods represented",
                   "Number of articles", "Method group", filename="h3_research_methods.png")

with right:
    st.markdown("### Method profile")
    if not method_counts.empty:
        top = method_counts.index[0]
        n_top = int(method_counts.iloc[0])
        show_finding(
            "Most frequent category",
            f"{top}: {n_top} of {len(analysis_df)} articles "
            f"({n_top / len(analysis_df):.0%}).")
    st.write("Groups are derived from the existing research-type labels. "
             "Check the original labels before making strong claims.")

st.divider()


# ==================================================
# 13. H4: RESEARCH THEMES
# ==================================================

st.markdown("## 04 · Research themes")
st.markdown(
    '<p class="section-intro">Hypothesis H4: FGM research in Nigeria focuses '
    'more on socio-cultural factors and prevention than on other research '
    'themes.</p>',
    unsafe_allow_html=True,
)

st.warning(
    "Theme counts are exploratory keyword matches, not validated content "
    "analysis. One article may match multiple themes, and broad keywords "
    "(for example 'awareness' and 'policy') match most abstracts.")

analysis_df["preliminary_themes"] = analysis_df.apply(
    lambda r: classify_themes(r["title"], r["abstract"]), axis=1)

theme_counts = (analysis_df["preliminary_themes"]
                .explode().dropna().value_counts())

if not theme_counts.empty:
    show_bar_chart(theme_counts, "Preliminary keyword-based research themes",
                   "Articles matching theme", "Research theme", filename="h4_research_themes.png")
    st.caption("Theme counts can exceed the number of included articles "
               "because an article may match more than one theme.")

    total = len(analysis_df)
    show_finding(
        "Theme shares (exploratory)",
        "; ".join(f"{t}: {n} of {total} ({n / total:.0%})"
                  for t, n in theme_counts.items()) + ".")

    theme_year = (
        analysis_df[["publication_year", "preliminary_themes"]]
        .explode("preliminary_themes")
        .dropna()
        .reset_index(drop=True)          # removes the duplicate index labels
    )
    theme_year["publication_year"] = theme_year["publication_year"].astype(int)

    with st.expander("Themes by publication year"):
        st.dataframe(
            pd.crosstab(
                theme_year["preliminary_themes"],
                theme_year["publication_year"],
            )
        )
else:
    st.info("No theme keyword matches in the selected year range.")

unmatched = analysis_df[analysis_df["preliminary_themes"].apply(len) == 0]
show_finding(
    "Manual review needed",
    f"{len(unmatched)} articles in the selected range matched no theme "
    "keywords. Other articles may also need checking.")

with st.expander("Review article-level theme assignments"):
    theme_table = analysis_df[
        ["publication_year", "title", "preliminary_themes"]].copy()
    theme_table["preliminary_themes"] = theme_table[
        "preliminary_themes"].apply(lambda t: "; ".join(t) or "None matched")
    st.dataframe(theme_table, hide_index=True)

st.divider()


# ==================================================
# 14. DATASET AND LIMITATIONS
# ==================================================

st.markdown("## Dataset and limitations")
st.markdown('<p class="section-intro">Important context for interpreting '
            'these descriptive results.</p>', unsafe_allow_html=True)

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
        - Methods are grouped into four broad categories.
        - Keyword-based themes require manual validation.
        - The 2026 publication year is partial.
        """
    )

st.download_button(
    label="Download included records as CSV",
    data=included.to_csv(index=False).encode("utf-8"),
    file_name="fgm_included_articles.csv",
    mime="text/csv",
)

st.caption(
    "Source: Project screening dataset of PubMed-indexed records. "
    "Findings describe this dataset and should not be generalized "
    "to all FGM research without further validation.")
# FGM RESEARCH IN NIGERIA (2015-2026): EXPLORATORY DATA ANALYSIS
import re

import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.max_columns", None)

YEAR_START, YEAR_END = 2015, 2026

ALL_ZONES = ["North-Central", "North-East", "North-West",
             "South-East", "South-South", "South-West"]

# Only labels that explicitly name a geopolitical zone are mapped.
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


def group_research_type(value):
    t = str(value).strip().casefold()
    # "mixed method" (not "mixed") so "mixed-effects" models are not caught
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


def classify_themes(row):
    text = f"{row['title']} {row['abstract']}".casefold()
    return [theme for theme, patterns in THEME_KEYWORDS.items()
            if any(re.search(p, text) for p in patterns)]


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


# %% 1. LOAD AND INSPECT
print("=" * 65)
print("FGM RESEARCH IN NIGERIA (2015-2026): EXPLORATORY DATA ANALYSIS")
print("=" * 65)

df = pd.read_csv("cleaneddata.csv", dtype={"pmid": str})
df.columns = df.columns.str.strip()
for col in ["screening_decision", "study_location", "research_type",
            "title", "abstract"]:
    df[col] = df[col].fillna("").astype(str).str.strip()
df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")

print("\nDataset shape:", df.shape)
print("Duplicate PMIDs:", df["pmid"].duplicated().sum())
print("Empty PMIDs:", (df["pmid"].fillna("") == "").sum())
print("Duplicate titles:", df["title"].str.casefold().duplicated().sum())

for col in ["screening_decision", "study_location", "research_type"]:
    print(f"\n--- {col.upper()} ---")
    print(df[col].value_counts(dropna=False).to_string())

# %% 2. ELIGIBLE DATASET
eda_df = df[df["screening_decision"].str.casefold()
            .isin(["include", "included"])].copy()
eda_df = eda_df[eda_df["publication_year"].between(YEAR_START, YEAR_END)].copy()
eda_df["study_location"] = eda_df["study_location"].replace(
    {"Nationwide (Multi-country)": "Multi-country"})

print("\nEligible articles:", len(eda_df))
print("Year range:", int(eda_df["publication_year"].min()), "to",
      int(eda_df["publication_year"].max()))

# %% 3. H1: PUBLICATION TRENDS
print("\n" + "=" * 65)
print("H1: Has FGM research output in Nigeria increased over time?")
print("=" * 65)

yearly = (eda_df["publication_year"].astype(int).value_counts().sort_index()
          .reindex(range(YEAR_START, YEAR_END + 1), fill_value=0))
print(yearly.to_string())

plt.figure(figsize=(5, 3))
plt.plot(yearly.index, yearly.values, marker="o", linewidth=2)
plt.title("FGM Research Publications in Nigeria (2015-2026)", fontsize=10)
plt.xlabel("Publication Year", fontsize=9)
plt.ylabel("Number of Publications", fontsize=9)
plt.xticks(range(YEAR_START, YEAR_END + 1), rotation=45, fontsize=8)
plt.yticks(fontsize=8)
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()

half = len(yearly) // 2
first, second = yearly.iloc[:half], yearly.iloc[half:]
print(f"\n{first.index[0]}-{first.index[-1]}: {int(first.sum())} articles | "
      f"{second.index[0]}-{second.index[-1]}: {int(second.sum())} articles")

rho_all = yearly.index.to_series().corr(yearly, method="spearman")
rho_excl = yearly.index[:-1].to_series().corr(yearly.iloc[:-1],
                                              method="spearman")
print(f"Spearman rho (year vs count): {rho_all:.2f} "
      f"(excluding partial {YEAR_END}: {rho_excl:.2f})")
print(f"Note: {YEAR_END} is a partial year and should be read cautiously.")

# %% 4. H2: GEOGRAPHICAL DISTRIBUTION
print("\n" + "=" * 65)
print("H2: Which geopolitical zones receive the most research attention?")
print("=" * 65)

eda_df["geopolitical_zone"] = eda_df["study_location"].map(ZONE_MAPPING)
eda_df["location_level"] = eda_df["study_location"].apply(location_level)

print("\nStudies by location level:")
print(eda_df["location_level"].value_counts().to_string())

zones = (eda_df["geopolitical_zone"].dropna().value_counts()
         .reindex(ALL_ZONES, fill_value=0))
print("\nStudies by explicitly identified zone (all six zones):")
print(zones.to_string())
print("Zones with no zone-specific studies:",
      [z for z in ALL_ZONES if zones[z] == 0])
print(f"Zone-specific studies: {int(zones.sum())} of {len(eda_df)}")

plt.figure(figsize=(5, 3))
zones.plot(kind="bar", width=0.65)
plt.title("FGM Research by Explicitly Identified Geopolitical Zone", fontsize=10)
plt.xlabel("Geopolitical Zone", fontsize=9)
plt.ylabel("Number of Publications", fontsize=9)
plt.xticks(rotation=30, ha="right", fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.show()

# %% 5. H3: RESEARCH METHODOLOGIES
print("\n" + "=" * 65)
print("H3: Which research methodologies are most common?")
print("=" * 65)

eda_df["methodology_group"] = eda_df["research_type"].apply(group_research_type)
methods = eda_df["methodology_group"].value_counts()
print(methods.to_string())
print(f"Quantitative share: {methods.get('Quantitative', 0) / len(eda_df):.0%}")

review = eda_df[eda_df["methodology_group"] == "Needs manual review"]
if not review.empty:
    print("\nRecords needing methodology review:")
    print(review[["pmid", "title", "research_type"]].to_string(index=False))

plt.figure(figsize=(5, 3))
methods.sort_values().plot(kind="bar", width=0.65)
plt.title("Research Methodologies Used in FGM Studies", fontsize=10)
plt.xlabel("Research Methodology", fontsize=9)
plt.ylabel("Number of Publications", fontsize=9)
plt.xticks(rotation=20, ha="right", fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.show()

# %% 6. H4: RESEARCH THEMES (provisional keyword classification)
print("\n" + "=" * 65)
print("H4: What are the major themes?")
print("=" * 65)

eda_df["research_themes"] = eda_df.apply(classify_themes, axis=1)
themes = eda_df["research_themes"].explode().dropna().value_counts()

print("\nTheme distribution (an article can match several themes):")
for theme, n in themes.items():
    print(f"  {theme}: {n} of {len(eda_df)} ({n / len(eda_df):.0%})")

unclassified = eda_df[eda_df["research_themes"].apply(len) == 0]
print("\nArticles with no matched theme:")
print(unclassified[["pmid", "title"]].to_string(index=False))

plt.figure(figsize=(5, 3))
themes.sort_values().plot(kind="barh", width=0.65)
plt.title("Major Themes in FGM Research in Nigeria", fontsize=10)
plt.xlabel("Number of Publications", fontsize=9)
plt.ylabel("Research Theme", fontsize=9)
plt.xticks(fontsize=8)
plt.yticks(fontsize=8)
plt.tight_layout()
plt.show()

print("\nCaution: keyword themes are exploratory. Broad terms such as "
      "'awareness' and 'policy' match most abstracts, so validate a sample "
      "manually before treating these shares as findings.")

# %% 7. LIMITATIONS
print("\n" + "=" * 65)
print("LIMITATIONS")
print("=" * 65)
print("""
1. Database coverage: PubMed only; other databases are not represented.
2. Study selection: results depend on the screening criteria applied.
3. Geography: national, multi-country and broad labels cannot be assigned
   to a specific zone and are kept separate.
4. Partial year: the 2026 count covers a partial year.
5. Methodology: original labels were grouped into four broad categories.
6. Themes: keyword-based and provisional; they do not establish an
   article's main focus.
7. Counts describe research output, not FGM prevalence or the
   effectiveness of interventions.
""")
print("EDA COMPLETED.")

import pandas as pd

# Load the FGM article screening dataset
df = pd.read_csv(
    "fgm_articles_screening.csv",
    dtype={"pmid": "string"}
)

# Inspect the dataset structure
print("Dataset shape:", df.shape)

print("\nFirst five rows:")
print(df.head())

print("\nColumn names:")
print(df.columns.tolist())

print("\nData types:")
print(df.dtypes)

print("\nMissing values per column:")
print(df.isnull().sum())

print("\nDuplicate PMIDs:")
print(df["pmid"].duplicated().sum())

print("\nSummary of numerical variables:")
print(df.describe())


import matplotlib.pyplot as plt

# 1. Check the publication-year distribution
print("\nPUBLICATIONS BY YEAR")
print(df["publication_year"].value_counts().sort_index())

# 2. Check screening decisions
print("\nSCREENING DECISIONS")
print(df["screening_decision"].value_counts(dropna=False))

# 3. Check study locations
print("\nSTUDY LOCATIONS")
print(df["study_location"].value_counts(dropna=False))

# 4. Check research types
print("\nRESEARCH TYPES")
print(df["research_type"].value_counts(dropna=False))

# 5. Check for duplicate titles
print("\nDUPLICATE TITLES")
print(
    df["title"].str.strip().str.lower().duplicated().sum()
)

# 6. Check for placeholder values
placeholders = [
    "not classified",
    "unknown",
    "not reported",
    "n/a",
    "na",
    "none",
    "not specified"
]

for column in [
    "screening_decision",
    "study_location",
    "research_type"
]:
    values = df[column].astype("string").str.strip().str.lower()
    count = values.isin(placeholders).sum()
    print(f"{column}: {count} placeholder values")

# 7. Visualise annual publication counts
year_counts = df["publication_year"].value_counts().sort_index()

plt.figure(figsize=(10, 5))
year_counts.plot(kind="bar")
plt.title("FGM Research Publications by Year")
plt.xlabel("Publication Year")
plt.ylabel("Number of Articles")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 8. Visualise research types
research_counts = df["research_type"].value_counts()

plt.figure(figsize=(10, 6))
top_research_types = research_counts.head(10).sort_values()

top_research_types.plot(kind="barh")

plt.title("Top 10 Research Types in FGM Publications")
plt.xlabel("Number of Articles")
plt.ylabel("Research Type")
plt.tight_layout()
plt.show()

# 9. Visualise the most frequently reported study locations
location_counts = df["study_location"].value_counts().head(15)

location_counts.sort_values().plot(
    kind="barh",
    figsize=(9, 6)
)
plt.title("Top 15 Reported Study Locations")
plt.xlabel("Number of Articles")
plt.ylabel("Study Location")
plt.tight_layout()
plt.show()


# TASK 2: Investigate inconsistent categories

print("\n--- RESEARCH TYPE LABELS ---")
print(
    df["research_type"]
    .value_counts(dropna=False)
    .to_string()
)

print("\n--- STUDY LOCATION LABELS ---")
print(
    df["study_location"]
    .value_counts(dropna=False)
    .to_string()
)

print("\n--- SCREENING DECISIONS ---")
print(
    df["screening_decision"]
    .value_counts(dropna=False)
    .to_string()
)

# Check whether different titles refer to the same article
print("\n--- POSSIBLE DUPLICATE TITLES ---")

title_clean = df["title"].str.strip().str.lower()
duplicate_titles = df[title_clean.duplicated(keep=False)]

if duplicate_titles.empty:
    print("No duplicate titles found.")
else:
    print(
        duplicate_titles[
            ["pmid", "title", "publication_year"]
        ].sort_values("title").to_string(index=False)
    )


# TASK 2: Prepare the eligible dataset for analysis

# Keep only records marked Include
eda_df = df[
    df["screening_decision"]
    .str.strip()
    .str.lower()
    .eq("include")
].copy()

print("\n--- ELIGIBLE DATASET ---")
print("Number of eligible articles:", len(eda_df))

# Publication counts for included articles only
print("\n--- ELIGIBLE PUBLICATIONS BY YEAR ---")
print(
    eda_df["publication_year"]
    .value_counts()
    .sort_index()
    .to_string()
)

# Research types among included articles
print("\n--- RESEARCH TYPES: INCLUDED ARTICLES ---")
print(
    eda_df["research_type"]
    .value_counts()
    .to_string()
)

# Location verification among included articles
print("\n--- STUDY LOCATIONS: INCLUDED ARTICLES ---")
print(
    eda_df["study_location"]
    .value_counts()
    .to_string()
)

# Check the remaining unclassified records
print("\n--- UNCLASSIFIED RESEARCH TYPES ---")
print(
    eda_df.loc[
        eda_df["research_type"].str.strip().str.lower()
        == "not classified",
        ["pmid", "title", "publication_year", "abstract"]
    ].to_string(index=False)
)

# Group research types into broader categories
# Original research_type values remain unchanged.

def group_research_type(value):
    text = str(value).lower()

    if "literature review" in text:
        return "Literature review"

    if "quantitative/qualitative" in text or "mixed" in text:
        return "Mixed methods"

    if "qualitative" in text:
        return "Qualitative"

    if "quantitative" in text:
        if "secondary" in text or "ndhs" in text or "dhs data" in text or "mics data" in text:
            return "Secondary survey/data analysis"
        if "cross-sectional" in text:
            return "Cross-sectional quantitative"
        if "cohort" in text or "longitudinal" in text:
            return "Longitudinal/cohort"
        if "quasi-experimental" in text:
            return "Quasi-experimental"
        return "Other quantitative"

    return "Needs manual review"


eda_df["research_type_group"] = (
    eda_df["research_type"].apply(group_research_type)
)

print("\n--- GROUPED RESEARCH TYPES ---")
print(eda_df["research_type_group"].value_counts().to_string())

# Plot the grouped categories
group_counts = eda_df["research_type_group"].value_counts().sort_values()

plt.figure(figsize=(9, 5))
group_counts.plot(kind="barh")
plt.title("Research Methods in Included FGM Publications")
plt.xlabel("Number of Articles")
plt.ylabel("Broad Research Type")
plt.tight_layout()
plt.show()

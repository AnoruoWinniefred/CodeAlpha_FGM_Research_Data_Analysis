"""
FGM Literature Screening Methodology

Data source: PubMed
Publication period: 2015-2026, inclusive

Inclusion criteria:
1. FGM/C is the primary research focus.
2. The study investigates Nigeria or includes Nigeria
   in a multicountry analysis.
3. The publication falls within the specified study period.

Exclusion criteria:
1. Published before 2015 or after 2026.
2. Study conducted outside Nigeria, including case reports
   involving Nigerian patients treated in another country.
3. FGM/C is not the primary research focus.
4. Multicountry study does not include Nigeria.

Screening outcome:
70 articles screened; 45 included and 25 excluded.
"""
import pandas as pd

CSV_PATH = "cleaneddata.csv"
YEAR_START, YEAR_END = 2015, 2026

# Set True only after checking the full texts of these three studies.
APPLY_LOCATION_CORRECTIONS = False
LOCATION_CORRECTIONS = {
    "27499413": "North-Central Nigeria",   # Ilorin is in Kwara State
    "25241272": "North-West Nigeria",      # title says north-west Nigeria
    "26614608": "North-West Nigeria",      # Birnin Kudu (believed Jigawa State)
}

# ---------------------------------------------------------------
# 1. LOAD AND CLEAN
# ---------------------------------------------------------------
df = pd.read_csv(CSV_PATH, dtype={"pmid": str})
df.columns = df.columns.str.strip()
df["pmid"] = df["pmid"].fillna("").str.strip()

n_start = len(df)
print(f"Loaded: {n_start} | Duplicate PMIDs: {df['pmid'].duplicated().sum()} "
      f"| Missing PMIDs: {(df['pmid'] == '').sum()}")

df["publication_year"] = pd.to_numeric(df["publication_year"], errors="coerce")
df = df[df["publication_year"].between(YEAR_START, YEAR_END)].copy()
print(f"Removed by year filter: {n_start - len(df)} | Remaining: {len(df)}")

# Reset the screening columns, then re-apply decisions from the lists below
df["screening_decision"] = "Needs review"
df["study_location"] = "Not verified"
df["research_type"] = "Not classified"

# ---------------------------------------------------------------
# 2. SCREENING DECISIONS
# ---------------------------------------------------------------
include_ids = [
    "30692824", "38616797", "40193370", "33463831", "38768111",
    "35283977", "34394263", "37584957", "35392944", "27499413",
    "40745880", "37585168", "31870245", "36962539", "36258712",
    "37461030", "31396592", "26614608", "39228647", "35155663",
    "33910545", "33577614", "35164773", "38532404", "28641026",
    "31240736", "39994629", "30588898", "40418731", "36318829",
    "29777639", "29777640", "38997690", "28784060", "42036654",
    "41524131", "41654954", "32127873", "33513163", "42544175",
    "27355616", "36204905", "25241272", "38595739", "40098091",
]

exclude_ids = [
    "33172757", "27707452", "31741540", "34743651", "27724920",
    "38622689", "37490461", "36627618", "40333804", "27724946",
    "34087606", "38837785", "30907422", "38300228", "29596591",
    "31007811", "39902618", "41074098", "36855163", "35094712",
    "30424713", "25745572", "33891651", "31362960", "26955127",
]

review_ids = []

inc, exc, rev = set(include_ids), set(exclude_ids), set(review_ids)
assert not (inc & exc) and not (inc & rev) and not (exc & rev), \
    "Overlapping ID lists"
print(f"include_ids: {len(include_ids)} | exclude_ids: {len(exclude_ids)}")

print("PMIDs in lists but not in dataset:",
      sorted((inc | exc | rev) - set(df["pmid"])))

unlisted = df.loc[~df["pmid"].isin(inc | exc | rev),
                  ["pmid", "title", "publication_year"]]
if not unlisted.empty:
    print("\nRecords not in any list:")
    print(unlisted.to_string(index=False))

df.loc[df["pmid"].isin(inc), "screening_decision"] = "Include"
df.loc[df["pmid"].isin(exc), "screening_decision"] = "Exclude"
df.loc[df["pmid"].isin(rev), "screening_decision"] = "Needs review"

# ---------------------------------------------------------------
# 3. DATA EXTRACTION FOR INCLUDED STUDIES
#    pmid: (study_location, research_type)
# ---------------------------------------------------------------
extraction = {
    "30692824": ("Not applicable", "Literature review"),
    "38616797": ("South-West Nigeria", "Quantitative - cross-sectional"),
    "40193370": ("National", "Quantitative - secondary survey analysis"),
    "33463831": ("South-Eastern Nigeria", "Qualitative - descriptive"),
    "38768111": ("South-West Nigeria", "Qualitative - interviews"),
    "35283977": ("North-Central Nigeria", "Quantitative - cross-sectional survey"),
    "34394263": ("South-Eastern Nigeria", "Qualitative - exploratory"),
    "37584957": ("South-Eastern Nigeria", "Quantitative - questionnaire"),
    "35392944": ("National", "Quantitative - secondary analysis of NDHS 2013 and 2018"),
    "27499413": ("South-West Nigeria", "Quantitative - cross-sectional survey"),
    "40745880": ("National", "Quantitative - secondary analysis of 2018 NDHS"),
    "37585168": ("National", "Quantitative - cross-sectional analysis of 2018 NDHS"),
    "31870245": ("South-Eastern Nigeria", "Qualitative - free listing and thematic analysis"),
    "36962539": ("National", "Quantitative - secondary analysis of 2018 NDHS"),
    "36258712": ("North-Central Nigeria", "Quantitative - cross-sectional study"),
    "37461030": ("South-Eastern Nigeria", "Quantitative - cross-sectional study"),
    "31396592": ("South-Eastern Nigeria", "Quantitative - prospective comparative cross-sectional study"),
    "26614608": ("Northern Nigeria", "Quantitative - cross-sectional study"),
    "39228647": ("National", "Quantitative - retrospective cross-sectional analysis"),
    "35155663": ("Multi-country", "Quantitative - ecological analysis of DHS data"),
    "33910545": ("National", "Quantitative - cohort analysis of national survey data"),
    "33577614": ("National", "Quantitative - Bayesian hierarchical spatio-temporal model"),
    "35164773": ("South-Eastern Nigeria", "Qualitative - in-depth interviews and thematic content analysis"),
    "38532404": ("National", "Quantitative - mixed-effects multilevel logistic regression"),
    "28641026": ("National", "Quantitative - secondary analysis of 2013 NDHS"),
    "31240736": ("South-West Nigeria", "Quantitative/Qualitative - cross-sectional survey and FGDs"),
    "39994629": ("South-West Nigeria", "Quantitative - quasi-experimental study"),
    "30588898": ("National", "Quantitative - geographically weighted logistic regression"),
    "40418731": ("National", "Quantitative - Bayesian hierarchical regression models"),
    "36318829": ("South-West Nigeria", "Quantitative - cross-sectional descriptive survey"),
    "29777639": ("National", "Quantitative - bivariate and multivariate ordered logistic estimates"),
    "29777640": ("South-Eastern Nigeria", "Quantitative - survey using Theory of Planned Behavior and logistic regression"),
    "38997690": ("National", "Quantitative - Bayesian hierarchical models comparing DHS and MICS"),
    "28784060": ("South-West Nigeria", "Qualitative - in-depth interviews"),
    "42036654": ("South-West Nigeria", "Qualitative - semi-structured in-depth interviews"),
    "41524131": ("National", "Quantitative - weighted accelerated-failure-time regression survival modelling"),
    "41654954": ("National", "Quantitative - multi-year policy impact analysis using MICS data"),
    "32127873": ("Nigeria (locality not specified)", "Quantitative"),
    "33513163": ("South-Eastern Nigeria", "Qualitative"),
    "42544175": ("Nigeria (locality not specified)", "Qualitative"),
    "27355616": ("Multi-country", "Quantitative"),
    "36204905": ("South-West Nigeria", "Quantitative - cross-sectional descriptive study"),
    "25241272": ("Northern Nigeria", "Quantitative cross-sectional study"),
    "38595739": ("South-Eastern Nigeria", "Qualitative - descriptive design with in-depth interviews"),
    "40098091": ("Multi-country", "Quantitative - cross-sectional study using DHS data"),
}

assert set(extraction) == inc, \
    f"Extraction/include mismatch: {sorted(set(extraction) ^ inc)}"

if APPLY_LOCATION_CORRECTIONS:
    for pmid, new_loc in LOCATION_CORRECTIONS.items():
        extraction[pmid] = (new_loc, extraction[pmid][1])

for pmid, (loc, typ) in extraction.items():
    df.loc[df["pmid"] == pmid, ["study_location", "research_type"]] = [loc, typ]

# ---------------------------------------------------------------
# 4. SAVE AND SUMMARISE
# ---------------------------------------------------------------
df.to_csv(CSV_PATH, index=False)

print("\nSCREENING SUMMARY:")
print(df["screening_decision"].value_counts())

print("\nStill needing review:")
print(df.loc[df["screening_decision"] == "Needs review",
             ["pmid", "title", "publication_year"]].to_string(index=False))

left = df[(df["screening_decision"] == "Include") &
          (df["study_location"] == "Not verified")]
print(f"\nIncluded records still missing extraction: {len(left)}")
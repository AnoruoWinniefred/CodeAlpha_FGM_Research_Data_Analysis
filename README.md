# Female Genital Mutilation (FGM) Research in Nigeria
### Public Health Research Analytics

Exploring publication patterns, study locations, research methods and themes in PubMed-indexed literature on FGM/C in Nigeria (2015–2026).

## Project Overview

This project examines research publications on female genital mutilation/cutting (FGM/C) conducted in Nigeria.

The workflow covers article screening, data preparation, exploratory data analysis (EDA), visualization and an interactive Streamlit dashboard. It examines publication patterns over time, the distribution of reported study locations, the research methods represented in the included literature, and the major research themes.

The aim is to show how data analytics can be applied to public health literature to identify patterns and summarize existing research.

## Research Questions

1. How has FGM research publication output in Nigeria changed between 2015 and 2026?
2. Which geopolitical zones in Nigeria receive the most research attention?
3. What research methodologies are most commonly used in FGM-related studies in Nigeria?
4. What are the major themes explored in FGM-related studies in Nigeria?

## Hypotheses

- **H1:** FGM research publications in Nigeria have increased over the study period.
- **H2:** FGM research publications are geographically concentrated in certain geopolitical zones rather than evenly distributed across Nigeria.
- **H3:** Quantitative research methodologies are the most commonly used approaches in FGM-related studies in Nigeria.
- **H4:** FGM research in Nigeria focuses more on socio-cultural factors and prevention than on other research themes.

## Data Source

- **Source:** PubMed
- **Study period:** 2015–2026, inclusive
- **Records screened:** 70
- **Included:** 45 articles
- **Excluded:** 25 articles

## Methodology

### 1. Data Collection
Article metadata (title, authors, journal, abstract, DOI and publication year) was collected from PubMed.

### 2. Screening
Records were assessed against predefined criteria.

**Inclusion criteria**
1. FGM/C is the primary research focus.
2. The study investigates Nigeria or includes Nigeria in a multicountry analysis.
3. The publication falls within the 2015–2026 study period.

**Exclusion criteria**
1. Published before 2015 or after 2026.
2. Study conducted outside Nigeria, including case reports involving Nigerian patients treated in another country.
3. FGM/C is not the primary research focus.
4. Multicountry study does not include Nigeria.

### 3. Data Preparation and Extraction
Python and pandas were used to standardize screening fields and check for duplicate and missing PMIDs. For each included study, the study location and research type were extracted from the abstract and recorded in the dataset.

### 4. Exploratory Data Analysis
- **Publication trends:** annual counts for 2015–2026, including years with zero articles.
- **Geography:** study locations were mapped to geopolitical zones only when the label explicitly named a zone. National, multi-country, "Northern Nigeria" and unspecified labels were kept separate rather than assigned to a zone.
- **Methods:** original research-type labels were grouped into quantitative, qualitative, mixed methods and literature review.
- **Themes:** a provisional keyword classification of titles and abstracts into four themes (socio-cultural factors, prevention and interventions, prevalence and determinants, health consequences). An article can match more than one theme.

### 5. Visualization
Matplotlib was used to create the charts, which are saved as PNG files.

### 6. Dashboard
An interactive Streamlit dashboard presents the screening results, a searchable article table with abstracts, and the four analyses, with a publication-year filter.

## Key Findings

These findings describe the screened PubMed dataset of 45 included articles.

- **H1, publication trends (supported descriptively):** 16 included articles were published in 2015–2020 and 29 in 2021–2026. Annual counts fluctuate from year to year, and 2026 is a partial year.
- **H2, geographic distribution (supported descriptively):** only 21 of the 45 studies name a specific geopolitical zone: South-East (10), South-West (9) and North-Central (2). No study explicitly identifies the North-East, North-West or South-South. A further 16 studies are national in scope, and the rest are multi-country, "Northern Nigeria" or unspecified.
- **H3, research methods (supported):** quantitative designs account for 33 of 45 studies (73%), followed by qualitative (10), mixed methods (1) and a literature review (1).
- **H4, research themes (tentative):** socio-cultural factors and prevention and interventions are the most frequently matched themes (34 articles each), followed by prevalence and determinants (23) and health consequences (15). Because the keyword lists include broad terms, this result is exploratory and needs manual validation.

A low count for a zone does not by itself prove a research gap. These findings should not be read as estimates of FGM/C prevalence in Nigeria or as a complete picture of all research on the subject.

## Tools and Technologies

- Python
- pandas
- Matplotlib
- Streamlit
- Jupyter Notebook
- PubMed
- Visual Studio Code
- Git and GitHub

## How to Run

1. Install the dependencies:
   ```
   pip install streamlit pandas matplotlib
   ```
2. Run the screening script to generate or update `cleaneddata.csv`.
3. Run the exploratory analysis with `python eda.py`, or open `EDA.ipynb`.
4. Launch the dashboard:
   ```
   streamlit run dashboard.py
   ```

Charts are saved as PNG files next to the script that produced them.

## Project Outputs

- Screened and extracted article dataset (`cleaneddata.csv`)
- Python script for screening and data extraction
- EDA script (`eda.py`) and notebook (`EDA.ipynb`)
- Interactive Streamlit dashboard (`dashboard.py`)
- Saved charts: publication trends, geopolitical zones, location levels, research methods and research themes

## Limitations

- The analysis is based on records retrieved from PubMed and may not capture every relevant publication.
- Findings depend on the search strategy, screening criteria and completeness of the available metadata.
- Reported study locations vary in geographic detail, and 24 of the 45 included studies could not be assigned to a specific zone.
- Multicountry studies may report pooled results that cannot be attributed specifically to Nigeria.
- Research-type labels were grouped into four broad categories, which hides differences between designs.
- Themes were identified by keyword matching, not content analysis. Broad terms such as "awareness" and "policy" match many abstracts, so theme shares are likely to be inflated.
- 2026 is a partial year and should not be compared directly with completed years.
- Publication counts reflect the retrieved literature, not the prevalence of FGM/C in the population.

## Conclusion

This project demonstrates the use of Python for literature-data preparation, screening, exploratory analysis, visualization and dashboarding to investigate research patterns relating to FGM/C in Nigeria.

Research output appears to have grown over the study period, is dominated by quantitative designs, and is concentrated in the South-East and South-West, with no zone-specific studies identified for the North-East, North-West or South-South. These patterns may guide further investigation.

## Author

**Winniefred Ada Anoruo**
Medical Laboratory Scientist | Data Analyst
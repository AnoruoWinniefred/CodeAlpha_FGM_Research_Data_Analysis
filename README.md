#
Public Health Research Analytics Female Genital Mutilation (FGM) Research in Nigeria

Exploring publication patterns, study locations, research methods and themes in PubMed-indexed literature.

## Project Overview

This project examines research publications on female genital mutilation/cutting (FGM/C) conducted in Nigeria.

The analysis covers article screening, data preparation, exploratory data analysis (EDA), and visualization. It examines publication patterns over time, the distribution of reported study locations, and the research methods represented in the included literature.

The aim is to demonstrate how data analytics can be applied to public health literature to identify patterns and summarize existing research.

## Research Questions

1. How does the annual number of included publications vary between 2015 and 2026?
2. How are included studies distributed across the locations reported in the dataset?
3. Which research methods are most frequently represented among the included studies?

## Hypotheses

- **H1:** The annual number of included publications varies over the study period.
- **H2:** Included studies are unevenly distributed across the locations reported in the dataset.
- **H3:** Some research methods are more frequently represented than others.

The exploratory analysis supported all three hypotheses descriptively within the screened dataset.

## Data Source

- **Source:** PubMed
- **Study period:** 2015–2026, inclusive
- **Initial dataset:** 70 article records
- **Included:** 46 articles
- **Excluded:** 24 articles

## Methodology

### 1. Data Collection
Article metadata was collected from PubMed for the literature analysis.

### 2. Screening
Records were assessed against predefined inclusion and exclusion criteria, focusing on publication year, Nigerian study relevance, and whether FGM/C was the primary research focus.

Multicountry studies were eligible when Nigeria was included and FGM/C was the main research focus.

### 3. Data Preparation
Python and pandas were used to prepare the dataset, standardize screening fields, and check for duplicate and missing PMIDs.

### 4. Exploratory Data Analysis
Publication years, reported study locations, and research types were examined to identify patterns in the included literature.

### 5. Visualization
Matplotlib was used to create charts illustrating publication trends, geographic distribution, and research-type representation.

## Key Findings

The exploratory analysis supported the three hypotheses:

- **Publication trends:** Annual publication counts varied across the study period.
- **Geographic distribution:** Included studies were unevenly distributed across reported locations.
- **Research methods:** Some research types appeared more frequently than others.

These findings describe the screened PubMed dataset. They should not be interpreted as estimates of FGM/C prevalence in Nigeria or as a complete representation of all research conducted on the subject.

## Tools and Technologies

- Python
- pandas
- Matplotlib
- PubMed
- Visual Studio Code

## Limitations

- The analysis is based on records retrieved from PubMed and may not capture every relevant publication.
- Findings depend on the search strategy, screening criteria, and completeness of the available metadata.
- Reported study locations may vary in geographic detail.
- Multicountry studies may report pooled results that cannot be attributed specifically to Nigeria.
- Publication counts reflect the retrieved literature, not the prevalence of FGM/C in the population.

## Project Outputs

- Screened article dataset
- Python scripts for screening and exploratory analysis
- Publication trend visualization
- Study location visualization
- Research-type visualization

## Conclusion

This project demonstrates the use of Python for literature-data preparation, screening, exploratory analysis, and visualization to investigate research patterns relating to FGM/C in Nigeria.

The analysis provides a structured overview of the included literature and highlights patterns that may guide further investigation.

## Author

Winniefred Ada Anoruo

Medical Laboratory Scientist | Data Analyst

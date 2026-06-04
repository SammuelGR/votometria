# Project Blueprint & Developer Guidelines

This document provides a comprehensive overview of the **Brazilian Presidential Election Analytical Dashboard** project. It serves as a master guide for developers and AI coding agents to ensure architectural alignment and consistency across all modules.

---

## 1. Project Proposal & Objectives

The goal of this project is to build an analytical dashboard that consolidates public expectation, electoral data, public attention, and macroeconomic context for Brazilian Presidential Elections.

The application helps users answer two main focus questions:

1. **Who is concentrating public attention?**
2. **How does public attention and market expectation behave over time?**

---

## 2. Monorepo Architecture

This project is structured as a monorepo containing isolated modules:

- **/scripts**: Contains the data ingestion backend (Python, virtual environment, and ETL scripts).
- **/frontend**: Reserved for the web-based visualization frontend application (dashboard).
- **/docs**: Contains documentation schemas, specifications, and guidelines.

---

## 3. Integrated Data Modules & Data Sources

Future development will expand the backend to ingest, clean, and align data for the following dashboard sections:

### A. Current Election ("Eleição Atual")

This section tracks present-day expectation, interest, and their correlations:

1. **Public Attention ("Atenção Pública")**:
   - _Source_: Google Trends & Wikipedia Pageviews APIs.
   - _Visualization_: Line chart showing interest trends over time. Interactive markers on the X-axis for relevant news/events.
2. **Market Expectation ("Expectativa de Mercado")**:
   - _Source_: Polymarket CLOB API.
   - _Visualization_: Line chart showing candidate victory probabilities. Must include Moving Averages (MM) to highlight trendlines.
3. **Share of Search**:
   - _Source_: Google Trends.
   - _Visualization_: Horizontal bar chart displaying the percentage share of search volume across main candidates.
4. **Public Attention vs. Market Expectation**:
   - _Source_: Merged Google Trends/Wikipedia & Polymarket datasets.
   - _Visualization_: Scatter plot mapping Share of Search (X-axis) against Polymarket Probability (Y-axis), where each point represents a candidate.

### B. Past Results ("Resultados Passados")

This section serves as a historical reference (e.g., 2018 and 2022 elections):

5. **Total per Candidate**:

- _Source_: Tribunal Superior Eleitoral (TSE) official CSV data.
- _Visualization_: Vertical bar chart of valid votes per candidate for a selected election year.

6. **Round Difference ("Diferença de Turnos")**:
   - _Source_: TSE.
   - _Visualization_: Line chart showing candidate performance change between the 1st and 2nd round.
7. **Geographic Distribution**:
   - _Source_: TSE.
   - _Visualization_: Choropleth map of Brazil colored by vote share per state/region.
8. **Social Media vs. Demographics**:
   - _Source_: Demographic voting data & social media indexes.
   - _Visualization_: Scatter plot showing social media presence (Y-axis) against vote share by age group (X-axis).

---

## 4. Data Integration & Quality Standards

When merging these sources, agents must implement the following data quality rules:

- **Name Standardization**: Normalize candidate names across different sources (e.g., aligning "Luiz Inácio Lula da Silva" vs "Lula" into a unified ID).
- **Temporal Alignment**: Resample daily/high-frequency series (like Polymarket) to a **weekly granularity** when comparing with lower-frequency public interest data (Google Trends).
- **Date Formats**: Enforce standard ISO `YYYY-MM-DD` formatting across all databases and datasets.
- **Data Types**: Ensure numerical metrics (like TSE vote counts stored as text strings) are parsed into integer or float columns during ingestion.
- **No Synthetic Data**: Always query real live data sources. Do not implement mock fallbacks or dummy data generators.

---

## 5. Coding Conventions

- **Strict English Policy**: All variables, database models, table/column names, prints, logs, docstrings, and code comments **must** be written in English.

---

## 6. KPI Thresholds & Update Frequencies

### Specific KPI Meta Targets

Future visualization logic or analytical notifications must implement the following business thresholds:

- **Attention Concentration**: Triggered when the top 2 candidates by Share of Search aggregate **70% or more** of total attention in a given period.
- **Attention/Market Divergence**: Triggered when the difference between a candidate's Share of Search and their Polymarket win probability exceeds **10 percentage points**.
- **Relevant Event Impact**: Triggered when a candidate's search interest increases by **20% or more** in the window following a logged political event (e.g. debate or campaign announcement).

### Data Ingestion Frequencies

- **Polymarket Expectations**: Daily or every 4 hours.
- **Google Trends & Wikipedia Pageviews**: Weekly batches.
- **TSE Historical Votes**: Static historical load per election cycle.
- **Macroeconomic Indicators**: Weekly or monthly batches (aligned with indicator releases).

# Frontend Modules

This document defines how the analytical modules are represented in the frontend interface.

The product and domain definition of each module is documented in `docs/modules.md`.

The frontend stack, routing and implementation conventions are documented in `docs/frontend.md`.

## Interface structure

The application is organized into one main analytical dashboard.

## Dashboard

The dashboard brings together public attention, market expectations and the relationship between both.

Modules in the dashboard:

- Market Expectations
- Public Attention
- Share of Search

Visual hierarchy:

```text
[ Market Expectations ]

[ Public Attention ]

[ Share of Search ]
```

Market Expectations is the main highlighted module.

## Module composition

Analytical modules are implemented as specific components.

Shared visual components may be used to keep consistency across the interface, including panels, headers, filter controls, source badges, legends and metric cards.

Each module keeps its own internal structure according to the analysis it represents.

Time-series date range selection belongs to the chart interaction layer, such as Recharts Brush.

Do not represent the date range as a standalone period filter outside the chart.

## Market Expectations

Market Expectations is the main module of the dashboard.

It shows the evolution of market probabilities for candidates in the current presidential election.

### Main visualization

Recharts time series line chart.

- X axis: time
- Y axis: market probability
- Series: one line per candidate
- Range interaction: Recharts Brush

### Summary metrics

- Current leader
- Margin between 1st and 2nd
- Biggest change in selected period
- Latest relevant event

### Controls

- Interval
- Candidates

### Interaction

The chart allows date range selection through the time-series interaction layer.

### Contextual layers

Relevant events are represented as vertical markers on the time axis.

### Source

- Polymarket

## Public Attention

Public Attention shows how public interest in each candidate changes over time.

### Main visualization

Time series line chart.

- X axis: time
- Y axis: public attention
- Series: one line per candidate

### Summary metrics

- Highest attention in selected period
- Highest attention peak

### Controls

- Election year
- Candidates

### Interaction

The chart should allow date range selection through the time-series interaction layer.

### Contextual layers

Relevant events are represented as vertical markers on the time axis.

### Sources

- Google Trends

## Share of Search

Share of Search shows how public attention is distributed among candidates in a selected period.

It complements Public Attention by showing the proportional concentration of attention.

### Main visualization

Proportional composition chart.

The preferred visual representation is a 100% stacked bar.

This module should represent Share of Search as a proportional distribution, not as absolute search volume.

### Summary metrics

- Top 2 concentration
- Candidate with highest share

### Controls

- Election year
- Candidates

### Interaction

The selected date range is controlled inside the module.

### Source

- Google Trends

## Candidate Totals

Candidate Totals compares the total votes received by candidates in past presidential elections.

### Main visualization

Candidate comparison chart.

### Source

- Tribunal Superior Eleitoral

## Runoff Difference

Runoff Difference compares candidate performance between the first and second rounds of past presidential elections.

### Main visualization

Round comparison chart.

### Source

- Tribunal Superior Eleitoral

## Electoral Map

Electoral Map shows the geographic distribution of presidential election results across Brazilian states.

### Main visualization

Brazilian state-level map.

### Source

- Tribunal Superior Eleitoral

## Complementary Indicators

Complementary Indicators groups additional analyses that support the interpretation of the electoral context.

This module may include rejection, approval, polling history, digital presence, demographic segmentation or economic context, according to the datasets consolidated by the project.

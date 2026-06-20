# Frontend Modules

This document defines how the analytical modules are represented in the frontend interface.

The product and domain definition of each module is documented in `docs/modules.md`.

The frontend stack, routing and implementation conventions are documented in `docs/frontend.md`.

## Interface structure

The application is organized into two main analytical dashboards.

```text
/current-election
/historical-elections
```

## Current Election dashboard

The Current Election dashboard focuses on the ongoing presidential election.

It brings together public attention, market expectations and the relationship between both.

Modules in this dashboard:

- Market Expectations
- Public Attention
- Share of Search
- Public Attention vs Market Expectations

Visual hierarchy:

```text
[ Market Expectations ]

[ Public Attention ] [ Share of Search ]

[ Public Attention vs Market Expectations ]
```

Market Expectations is the main highlighted module.

Public Attention and Share of Search are visually grouped because they represent complementary views of public attention.

Public Attention receives more horizontal space than Share of Search in desktop layouts.

Public Attention vs Market Expectations works as the synthesis module of the dashboard.

## Module composition

Analytical modules are implemented as specific components.

Shared visual components may be used to keep consistency across the interface, including panels, headers, filter controls, source badges, legends and metric cards.

Each module keeps its own internal structure according to the analysis it represents.

Time-series date range selection belongs to the chart interaction layer, such as Recharts Brush.

Do not represent the date range as a standalone period filter outside the chart.

## Market Expectations

Market Expectations is the main module of the Current Election dashboard.

It shows the evolution of market probabilities for candidates in the current presidential election.

### Main visualization

Time series line chart.

- X axis: time
- Y axis: market probability
- Series: one line per candidate

### Summary metrics

- Current leader
- Margin between 1st and 2nd
- Biggest change in selected period
- Latest relevant event

### Controls

- Interval
- Candidates

### Interaction

The chart should allow date range selection through the time-series interaction layer.

### Contextual layers

Relevant events are represented as vertical markers on the time axis.

### Source

- Polymarket

## Public Attention

Public Attention shows how public interest in each candidate changes over time.

It is visually grouped with Share of Search.

### Main visualization

Time series line chart.

- X axis: time
- Y axis: public attention
- Series: one line per candidate

### Summary metrics

- Highest attention in selected period
- Highest attention peak

### Controls

- Candidates

### Interaction

The chart should allow date range selection through the time-series interaction layer.

### Contextual layers

Relevant events are represented as vertical markers on the time axis.

### Sources

- Google Trends
- Wikipedia Pageviews

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

- Candidates

### Interaction

The selected date range should come from the dashboard or related chart context when implemented.

### Source

- Google Trends

## Public Attention vs Market Expectations

Public Attention vs Market Expectations compares public attention and market probability for the candidates.

This module helps identify alignment and divergence between public interest and prediction market expectations.

### Main visualization

Scatterplot.

- X axis: Share of Search
- Y axis: market probability
- Point: one candidate in the selected period

### Controls

- Candidates

### Interaction

The selected date range should come from the dashboard or related chart context when implemented.

The tooltip shows:

- Candidate
- Share of Search
- Market probability
- Difference in percentage points

### Explanation text

Each point represents a candidate in the selected period. The horizontal axis shows the candidate's Share of Search, while the vertical axis shows the candidate's market probability on Polymarket. The difference between these values helps identify alignments and divergences between public interest and market expectations.

### Sources

- Google Trends
- Wikipedia Pageviews
- Polymarket

## Historical Elections dashboard

The Historical Elections dashboard focuses on past Brazilian presidential elections.

It brings together official results, geographic distribution, comparisons between rounds and complementary indicators.

Modules in this dashboard:

- Candidate Totals
- Runoff Difference
- Electoral Map
- Complementary Indicators

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

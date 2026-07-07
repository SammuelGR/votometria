# Analytical Modules

This document defines the analytical modules of the project from a product and domain perspective.

The goal is to describe what each module represents, which part of the election analysis it supports, and which data sources are related to it.

Frontend layout, visual hierarchy and implementation details are documented separately in `docs/frontend-modules.md` and `docs/frontend.md`.

## Product structure

The application is organized around one main analytical dashboard.

### Dashboard

The dashboard brings together indicators related to public attention, market expectations and the relationship between both.

Modules in this dashboard:

- Market Expectations
- Public Attention
- Share of Search

## Contextual events

Relevant political events are part of the analytical context of the project.

They may include debates, polls, court decisions, interviews, campaign announcements, controversies or other events that help explain changes in public attention or market expectations.

In the product interface, contextual events are represented as supporting information inside time-based modules.

They are not treated as a standalone visual module in the product structure.

## Dashboard modules

### Market Expectations

The Market Expectations module tracks how the probability of victory for each candidate evolves during the current presidential election.

This module uses Polymarket data as its main source.

It supports analysis of:

- probability evolution by candidate
- leadership changes over time
- distance between the main candidates
- relevant political events that coincide with changes in market expectations

Related sources:

- Polymarket
- Relevant political events

### Public Attention

The Public Attention module tracks how public interest in each candidate changes over time.

This module uses search data as a proxy for public attention.

It supports analysis of:

- interest evolution by candidate
- attention peaks
- candidates with higher attention in a selected period
- events that coincide with changes in public attention

Related sources:

- Google Trends
- Relevant political events

### Share of Search

The Share of Search module shows how public attention is distributed among the candidates in a selected period.

This module is related to the concentration of attention around the main candidates.

It supports analysis of:

- attention concentration
- share of attention by candidate
- dominance of the top candidates in a selected period

Related sources:

- Google Trends

### Candidate Totals

The Candidate Totals module compares the total number of votes received by candidates in past presidential elections.

It supports analysis of:

- total votes by candidate
- vote share by candidate
- comparison between candidates in a selected election

Related sources:

- Tribunal Superior Eleitoral

### Runoff Difference

The Runoff Difference module compares candidate performance between the first and second rounds of past presidential elections.

It supports analysis of:

- vote variation between rounds
- change in vote share
- difference between the leading candidates
- candidate performance after the first round

Related sources:

- Tribunal Superior Eleitoral

### Electoral Map

The Electoral Map module shows the geographic distribution of presidential election results across Brazilian states.

It supports analysis of:

- winning candidate by state
- vote distribution by state
- regional patterns in electoral performance

Related sources:

- Tribunal Superior Eleitoral

### Complementary Indicators

The Complementary Indicators module groups additional analyses that support the interpretation of the election context.

This module may include indicators related to rejection, approval, polling history, digital presence, demographic segmentation or economic context, depending on the data sources consolidated by the group.

Related sources may include:

- polling aggregators
- public opinion data
- Google Trends
- economic indicators
- other complementary public datasets

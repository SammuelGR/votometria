# Frontend

This document defines stable frontend architecture decisions for the project.

Frontend module representation is documented in `docs/frontend-modules.md`.

Product and domain module definitions are documented in `docs/modules.md`.

## Stack

The frontend uses:

- React 19
- TypeScript
- Vite 8
- Tailwind CSS v4
- React Router 7
- TanStack Query v5
- Lucide React
- clsx
- tailwind-merge

The recommended runtime is Node 24 LTS.

## Application model

The frontend is a single-page application.

The application has two main dashboard routes:

```text
/current-election
/historical-elections
```

## Dashboards

The application is organized around two main dashboards:

- Current Election
- Historical Elections

The Current Election dashboard focuses on the ongoing presidential election.

The Historical Elections dashboard focuses on past Brazilian presidential elections.

## Interface architecture

The frontend follows a dashboard-style interface.

Each dashboard is composed of analytical modules.

Analytical modules own their internal interface structure because each analysis has its own visual purpose, controls and interaction model.

Shared UI primitives provide consistency across dashboards and modules.

## Interface language

All user-facing interface text must be written in Portuguese.

Code identifiers, component names, file names, types, comments, logs and internal documentation remain in English according to the project coding conventions.

Routes use English slugs.

## Module boundaries

The meaning of each analytical module belongs to `docs/modules.md`.

The visual representation of each analytical module belongs to `docs/frontend-modules.md`.

The frontend implementation follows the decisions registered in those documents.

## Routing convention

Routes use English slugs.

Route names should reflect the product areas they represent.

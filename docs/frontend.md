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

Node 22.12 or newer is supported by Vite 8.

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

## Project structure

Pages are organized by context:

```text
src/pages/
  CurrentElection/
    CurrentElection.tsx
    modules/
      ...

  HistoricalElections/
    HistoricalElections.tsx
```

Use explicit component file names instead of generic `index.tsx` files for pages and feature-level components.

Page-specific module components stay inside the page context that owns them.

Shared UI components stay in `src/components/ui`.

Shared UI components may be imported from the `src/components/ui` barrel export:

```ts
import { ModuleHeader, ModulePanel } from '~/components/ui';
```

Components inside `src/components/ui` should import other UI components directly from their source file when needed, not from the barrel export.

General utilities stay in `src/utils`.

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

Route paths are centralized in `src/routes/paths.ts`.

The route tree is defined in `src/routes/AppRoutes.tsx`.

Do not hardcode route strings in layout navigation or route declarations when a value exists in `ROUTES`.

## Providers

Global application providers are configured in `src/App.tsx`.

TanStack Query is configured with a shared `QueryClient` and `QueryClientProvider`.

## Styling conventions

Use Tailwind CSS v4.

Prefer project theme tokens and CSS variables in `src/index.css` for stable colors and shared visual decisions.

When writing Tailwind classes, keep classes in a consistent logical order. Prefer alphabetical order when practical, especially in new or edited code.

Avoid unnecessary decorative text in analytical modules. Module titles, controls, metrics and visualizations should carry the interface unless additional interpretation text is explicitly needed.

## Current implementation notes

The Current Election dashboard currently uses temporary chart placeholder images.

Real charts should replace those placeholders when data and chart components are implemented.

Temporal range selection for charts should be handled by the chart implementation, such as Recharts Brush, not by a separate application-level period filter.

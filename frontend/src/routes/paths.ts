export const ROUTES = {
  currentElection: '/current-election',
  fallback: '*',
  historicalElections: '/historical-elections',
  root: '/',
} as const;

export type RoutePath = (typeof ROUTES)[keyof typeof ROUTES];

import { BrowserRouter, Navigate, Route, Routes } from 'react-router';

import AppLayout from '~/components/layout/AppLayout';
import CurrentElection from '~/pages/CurrentElection/CurrentElection';
import HistoricalElections from '~/pages/HistoricalElections/HistoricalElections';
import { ROUTES } from '~/routes/paths';

export default function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path={ROUTES.root} element={<Navigate to={ROUTES.currentElection} replace />} />

          <Route path={ROUTES.currentElection} element={<CurrentElection />} />

          <Route path={ROUTES.historicalElections} element={<HistoricalElections />} />

          <Route path={ROUTES.fallback} element={<Navigate to={ROUTES.root} replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

import { BarChart3 as BarChart3Icon, History as HistoryIcon, Vote as VoteIcon } from 'lucide-react';
import type { ReactElement } from 'react';
import { NavLink, Outlet } from 'react-router';

import { ROUTES, type RoutePath } from '~/routes/paths';
import { cn } from '~/utils/cn';

type NavigationItem = {
  icon: ReactElement;
  label: string;
  path: RoutePath;
};

const navigationItems: NavigationItem[] = [
  {
    icon: <BarChart3Icon aria-hidden="true" className="size-4" />,
    label: 'Eleição Atual',
    path: ROUTES.currentElection,
  },
  {
    icon: <HistoryIcon aria-hidden="true" className="size-4" />,
    label: 'Eleições Passadas',
    path: ROUTES.historicalElections,
  },
];

export default function AppLayout() {
  return (
    <div className="bg-background min-h-screen text-foreground">
      <header className="bg-surface border-border border-b">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-navigation flex size-10 items-center justify-center rounded-lg">
              <VoteIcon aria-hidden="true" className="size-5" />
            </div>

            <div>
              <p className="text-base font-semibold">Dashboard Eleitoral Comparativo</p>

              <p className="text-muted text-sm">Eleições presidenciais brasileiras</p>
            </div>
          </div>

          <nav aria-label="Navegação principal" className="flex flex-wrap gap-2 lg:justify-end">
            {navigationItems.map((item) => (
              <NavLink
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2 rounded-md border border-transparent px-3 py-2 text-sm transition-colors',
                    isActive ? 'bg-navigation-active border-border shadow-sm' : 'hover:bg-navigation text-muted',
                  )
                }
                key={item.path}
                to={item.path}
              >
                {item.icon}

                <span>{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}

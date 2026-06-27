import { NavLink, Outlet } from 'react-router';

import { ROUTES, type RoutePath } from '~/routes/paths';
import { cn } from '~/utils/cn';

type NavigationItem = {
  label: string;
  path: RoutePath;
};

const navigationItems: NavigationItem[] = [
  {
    label: 'Eleição Atual',
    path: ROUTES.currentElection,
  },
  {
    label: 'Histórico',
    path: ROUTES.historicalElections,
  },
];

export default function AppLayout() {
  return (
    <div className="min-h-screen text-foreground">
      <header className="bg-surface border-line-strong border-b">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-baseline gap-3">
            <span className="font-extrabold text-2xl tracking-tight">
              <span>VOTO</span>
              <span className="font-black text-accent-2">·</span>
              <span className="text-accent">METRIA</span>
            </span>

            <span className="hidden font-mono text-[11px] text-muted uppercase tracking-wide sm:inline">
              instrumento de leitura eleitoral
            </span>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <nav
              aria-label="Navegação principal"
              className="border-line-strong bg-surface inline-flex overflow-hidden rounded-md border"
            >
              {navigationItems.map((item, index) => (
                <NavLink
                  className={({ isActive }) =>
                    cn(
                      'cursor-pointer font-mono px-4 py-2.5 text-xs uppercase tracking-wide transition-colors',
                      index > 0 && 'border-border border-l',
                      isActive ? 'bg-foreground text-surface' : 'text-muted hover:bg-navigation',
                    )
                  }
                  key={item.path}
                  to={item.path}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>

            <div className="hidden items-center gap-2 font-mono text-muted text-xs md:flex">
              <span
                aria-hidden="true"
                className="inline-block size-2 rounded-full bg-accent-2 motion-safe:animate-pulse"
              />

              <span>Presidencial 2026</span>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}

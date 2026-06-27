import type { ReactNode } from 'react';

type ChartTooltipProps = {
  children: ReactNode;
  title?: ReactNode;
};

/** Shared tooltip shell in the instrument style (surface, hairline, mono). */
export default function ChartTooltip({ children, title }: ChartTooltipProps) {
  return (
    <div className="bg-surface border-border min-w-40 rounded-md border px-3 py-2 font-mono text-xs shadow-sm">
      {title ? <div className="text-muted mb-1 uppercase tracking-wide">{title}</div> : null}

      {children}
    </div>
  );
}

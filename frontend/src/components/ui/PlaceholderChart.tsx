import { ChartNoAxesColumnIncreasing as ChartIcon } from 'lucide-react';

import { cn } from '~/utils/cn';

type PlaceholderChartProps = {
  className?: string;
  label: string;
};

export default function PlaceholderChart({ className, label }: PlaceholderChartProps) {
  return (
    <div
      className={cn(
        'bg-navigation border-border flex min-h-64 flex-col justify-center overflow-hidden rounded-md border border-dashed p-4',
        className,
      )}
    >
      <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
        <ChartIcon aria-hidden="true" className="size-8 text-muted" />

        <p className="font-mono text-muted text-xs uppercase tracking-wide">{label}</p>
      </div>
    </div>
  );
}

import { ChartNoAxesColumnIncreasing as ChartIcon } from 'lucide-react';

import { cn } from '~/utils/cn';

type PlaceholderChartProps = {
  className?: string;
  imageAlt?: string;
  imageSrc?: string;
  label: string;
  variant?: 'bar' | 'line' | 'scatter';
};

export default function PlaceholderChart({
  className,
  imageAlt,
  imageSrc,
  label,
  variant = 'line',
}: PlaceholderChartProps) {
  return (
    <div
      className={cn(
        'bg-navigation border-border flex min-h-64 flex-col justify-center overflow-hidden rounded-md border border-dashed p-4',
        className,
      )}
      data-chart-variant={variant}
    >
      {imageSrc ? (
        <img
          alt={imageAlt ?? label}
          className="h-full max-h-96 min-h-56 w-full rounded object-contain"
          src={imageSrc}
        />
      ) : (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center">
          <ChartIcon aria-hidden="true" className="size-8 text-muted" />

          <p className="font-mono text-muted text-xs uppercase tracking-wide">{label}</p>
        </div>
      )}
    </div>
  );
}

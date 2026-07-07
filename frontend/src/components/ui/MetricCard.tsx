import { cn } from '~/utils/cn';

type MetricCardVariant = 'default' | 'negative' | 'positive';

type MetricCardProps = {
  text?: string;
  title: string;
  value?: string;
  variant?: MetricCardVariant;
};

const valueVariantClassNames: Record<MetricCardVariant, string> = {
  default: 'text-foreground',
  negative: 'text-negative',
  positive: 'text-positive',
};

export default function MetricCard({ text, title, value, variant = 'default' }: MetricCardProps) {
  return (
    <div className="bg-navigation rounded-md p-4">
      <p className="font-medium text-muted text-xs uppercase">{title}</p>

      {text ? (
        <p className="line-clamp-2 mt-2 font-semibold leading-snug text-foreground text-sm" title={text}>
          {text}
        </p>
      ) : null}

      {value ? (
        <p className={cn('font-semibold text-sm', text ? 'mt-1' : 'mt-2', valueVariantClassNames[variant])}>{value}</p>
      ) : null}
    </div>
  );
}

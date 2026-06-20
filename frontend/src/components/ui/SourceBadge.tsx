import { cn } from '~/utils/cn';

type SourceBadgeProps = {
  label: string;
};

export default function SourceBadge({ label }: SourceBadgeProps) {
  return (
    <span
      className={cn(
        'bg-navigation border border-border font-medium inline-flex px-2.5 py-1',
        'rounded-full text-muted text-xs',
      )}
    >
      {label}
    </span>
  );
}

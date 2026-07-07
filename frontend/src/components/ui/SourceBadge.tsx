import { cn } from '~/utils/cn';

type SourceTone = 'attention' | 'election' | 'market' | 'neutral' | 'positive';

type SourceBadgeProps = {
  label: string;
  tone?: SourceTone;
};

const dotToneClass: Record<SourceTone, string> = {
  attention: 'bg-accent-2',
  election: 'bg-[#7b61ff]',
  market: 'bg-accent',
  neutral: 'bg-muted',
  positive: 'bg-positive',
};

export default function SourceBadge({ label, tone = 'neutral' }: SourceBadgeProps) {
  return (
    <span
      className={cn(
        'bg-surface border border-border font-mono inline-flex items-center gap-1.5',
        'rounded-sm px-2 py-1 text-[10.5px] text-muted uppercase tracking-wide',
      )}
    >
      <span aria-hidden="true" className={cn('size-1.5 rounded-full', dotToneClass[tone])} />

      {label}
    </span>
  );
}

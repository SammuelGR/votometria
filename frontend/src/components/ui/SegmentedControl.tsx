import { cn } from '~/utils/cn';

type SegmentedControlOption = {
  label: string;
  value: string;
};

type SegmentedControlProps = {
  label: string;
  onChange?: (value: string) => void;
  options: SegmentedControlOption[];
  value: string;
};

export default function SegmentedControl({ label, onChange, options, value }: SegmentedControlProps) {
  return (
    <div className="flex w-fit max-w-full flex-col gap-2">
      <span className="font-mono text-[11px] text-muted uppercase tracking-wide">{label}</span>

      <div className="border-line-strong bg-surface inline-flex max-w-full overflow-hidden rounded-md border">
        {options.map((option, index) => {
          const isSelected = option.value === value;

          return (
            <button
              className={cn(
                'cursor-pointer font-mono px-3 py-1.5 text-xs uppercase tracking-wide whitespace-nowrap transition-colors',
                index > 0 && 'border-border border-l',
                isSelected ? 'bg-foreground text-surface' : 'text-muted hover:bg-navigation',
              )}
              key={option.value}
              onClick={() => onChange?.(option.value)}
              type="button"
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

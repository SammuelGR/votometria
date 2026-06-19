import { cn } from '~/utils/cn';

type SegmentedControlOption = {
  label: string;
  value: string;
};

type SegmentedControlProps = {
  label: string;
  options: SegmentedControlOption[];
  value: string;
};

export default function SegmentedControl({ label, options, value }: SegmentedControlProps) {
  return (
    <div className="flex w-fit max-w-full flex-col gap-2">
      <span className="font-medium text-muted text-xs uppercase">{label}</span>

      <div className="bg-navigation inline-flex max-w-full flex-wrap gap-1 rounded-md p-1">
        {options.map((option) => {
          const isSelected = option.value === value;

          return (
            <button
              className={cn(
                'rounded px-2.5 py-1.5 text-sm transition-colors whitespace-nowrap',
                isSelected ? 'bg-surface shadow-sm text-foreground' : 'text-muted',
              )}
              key={option.value}
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

import { cn } from '~/utils/cn';

type CandidateMultiSelectProps = {
  label: string;
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
};

export default function CandidateMultiSelect({ label, options, selected, onChange }: CandidateMultiSelectProps) {
  const selectedSet = new Set(selected);

  function toggle(option: string) {
    if (selectedSet.has(option)) {
      onChange(selected.filter((item) => item !== option));
    } else {
      onChange([...selected, option]);
    }
  }

  return (
    <div className="flex w-full flex-col gap-2">
      <span className="font-mono text-[11px] text-muted uppercase tracking-wide">{label}</span>

      <div className="flex flex-wrap gap-1.5">
        {options.map((option) => {
          const isActive = selectedSet.has(option);

          return (
            <button
              aria-pressed={isActive}
              className={cn(
                'border-border cursor-pointer font-mono rounded-sm border px-2.5 py-1 text-xs transition-colors',
                isActive ? 'bg-foreground text-surface' : 'bg-surface text-muted hover:bg-navigation',
              )}
              key={option}
              onClick={() => toggle(option)}
              type="button"
            >
              {option}
            </button>
          );
        })}
      </div>
    </div>
  );
}

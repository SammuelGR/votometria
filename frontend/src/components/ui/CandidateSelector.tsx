type CandidateOption = {
  label: string;
  value: string;
};

type CandidateSelectorProps = {
  candidates: CandidateOption[];
  label: string;
  value: string;
};

export default function CandidateSelector({ candidates, label, value }: CandidateSelectorProps) {
  return (
    <div className="flex w-full flex-col gap-2 sm:w-64">
      <span className="font-medium text-muted text-xs uppercase">{label}</span>

      <select
        className="bg-navigation border-border h-10 rounded-md border px-3 text-foreground text-sm"
        defaultValue={value}
      >
        {candidates.map((candidate) => (
          <option key={candidate.value} value={candidate.value}>
            {candidate.label}
          </option>
        ))}
      </select>
    </div>
  );
}

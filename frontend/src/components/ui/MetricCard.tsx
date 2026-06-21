type MetricCardProps = {
  label: string;
  value: string;
};

export default function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="bg-navigation rounded-md p-4">
      <p className="font-medium text-muted text-xs uppercase">{label}</p>

      <p className="mt-2 font-semibold text-foreground text-sm">{value}</p>
    </div>
  );
}

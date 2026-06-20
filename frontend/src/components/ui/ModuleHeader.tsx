import type { ReactNode } from 'react';

type ModuleHeaderProps = {
  badges?: ReactNode;
  title: string;
};

export default function ModuleHeader({ badges, title }: ModuleHeaderProps) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
      <h2 className="font-semibold text-lg">{title}</h2>

      {badges ? <div className="flex shrink-0 flex-wrap gap-2">{badges}</div> : null}
    </div>
  );
}

import type { ReactNode } from 'react';

import { cn } from '~/utils/cn';

type ModulePanelProps = {
  children: ReactNode;
  className?: string;
};

export default function ModulePanel({ children, className }: ModulePanelProps) {
  return (
    <section className={cn('bg-surface border-border rounded-lg border p-5 shadow-sm', className)}>{children}</section>
  );
}

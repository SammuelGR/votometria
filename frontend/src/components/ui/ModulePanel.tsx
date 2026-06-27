import type { ReactNode } from 'react';

import { cn } from '~/utils/cn';

type ModulePanelProps = {
  children: ReactNode;
  className?: string;
};

export default function ModulePanel({ children, className }: ModulePanelProps) {
  return <section className={cn('bg-surface border-border rounded-md border p-5', className)}>{children}</section>;
}

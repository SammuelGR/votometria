import { useEffect, useId, useRef, useState } from 'react';
import { ChevronDownIcon, LoaderCircleIcon } from 'lucide-react';

import { cn } from '~/utils/cn';

export type MultiSelectOption = {
  disabled?: boolean;
  label: string;
  value: string;
};

type MultiSelectProps = {
  allLabel?: string;
  disabled?: boolean;
  emptyLabel?: string;
  error?: string;
  label: string;
  loading?: boolean;
  onChange: (value: string[]) => void;
  options: MultiSelectOption[];
  value: string[];
};

export default function MultiSelect({
  allLabel = 'Todos',
  disabled = false,
  emptyLabel = 'Nenhuma opção disponível',
  error,
  label,
  loading = false,
  onChange,
  options,
  value,
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = useState(false);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);
  const fieldId = useId();
  const isDisabled = disabled || loading;
  const isPopoverOpen = isOpen && !isDisabled;

  useEffect(() => {
    if (!isPopoverOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false);
        buttonRef.current?.focus();
      }
    }

    document.addEventListener('mousedown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('mousedown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isPopoverOpen]);

  function handleOptionChange(optionValue: string, checked: boolean) {
    const selectedValues = new Set(
      checked ? [...value, optionValue] : value.filter((selectedValue) => selectedValue !== optionValue),
    );
    const nextValue = options.filter((option) => selectedValues.has(option.value)).map((option) => option.value);

    onChange(nextValue);
  }

  return (
    <div className="relative flex w-full max-w-full flex-col gap-2 sm:w-56" ref={rootRef}>
      <label className="font-mono text-[11px] text-muted uppercase tracking-wide" htmlFor={fieldId}>
        {label}
      </label>

      <button
        aria-expanded={isPopoverOpen}
        className={cn(
          'border-line-strong bg-surface flex h-8 items-center justify-between gap-3 rounded-md border',
          'font-mono px-3 text-foreground text-xs transition-colors w-full',
          !isDisabled && 'cursor-pointer',
          !error && !isDisabled && 'hover:bg-navigation',
          error && 'border-negative',
          loading && 'cursor-wait text-muted',
          'disabled:cursor-not-allowed disabled:opacity-60',
        )}
        disabled={isDisabled}
        id={fieldId}
        onClick={() => setIsOpen((currentValue) => !currentValue)}
        ref={buttonRef}
        type="button"
      >
        <span className="truncate">{loading ? 'Carregando...' : getSummary(options, value, allLabel)}</span>

        {loading ? (
          <LoaderCircleIcon className="h-4 w-4 shrink-0 animate-spin text-muted" aria-hidden="true" />
        ) : (
          <ChevronDownIcon
            className={cn('h-4 w-4 shrink-0 text-muted transition-transform', isPopoverOpen && 'rotate-180')}
            aria-hidden="true"
          />
        )}
      </button>

      {isPopoverOpen ? (
        <div
          className={cn(
            'absolute bg-surface border border-line-strong gap-1 grid left-0 max-h-64',
            'mt-2 overflow-auto p-1.5 rounded-md shadow-sm top-full w-full z-20',
          )}
        >
          {options.length > 0 ? (
            <>
              <label
                className="cursor-pointer flex gap-2 hover:bg-navigation items-center px-2 py-1.5 rounded text-foreground text-sm"
                htmlFor={`${fieldId}-option-all`}
              >
                <input
                  checked={value.length === 0}
                  className="h-4 w-4 accent-foreground"
                  id={`${fieldId}-option-all`}
                  onChange={() => onChange([])}
                  type="checkbox"
                />

                <span>{allLabel}</span>
              </label>

              <div className="border-border border-t" />

              {options.map((option, optionIndex) => {
                const optionId = `${fieldId}-option-${optionIndex}`;

                return (
                  <label
                    className={cn(
                      'cursor-pointer flex gap-2 hover:bg-navigation items-center',
                      'px-2 py-1.5 rounded text-foreground text-sm',
                      option.disabled && 'cursor-not-allowed opacity-60 hover:bg-transparent',
                    )}
                    htmlFor={optionId}
                    key={option.value}
                  >
                    <input
                      checked={value.includes(option.value)}
                      className="h-4 w-4 accent-foreground"
                      disabled={option.disabled}
                      id={optionId}
                      onChange={(event) => handleOptionChange(option.value, event.currentTarget.checked)}
                      type="checkbox"
                    />

                    <span>{option.label}</span>
                  </label>
                );
              })}
            </>
          ) : (
            <span className="px-2 py-1.5 text-muted text-sm">{emptyLabel}</span>
          )}
        </div>
      ) : null}

      {error ? <span className="text-negative text-xs">{error}</span> : null}
    </div>
  );
}

function getSummary(options: MultiSelectOption[], value: string[], allLabel: string) {
  if (value.length === 0) {
    return allLabel;
  }

  if (value.length === 1) {
    return options.find((option) => option.value === value[0])?.label ?? value[0];
  }

  return `${value.length} selecionados`;
}

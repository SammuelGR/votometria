export const EMPTY_VALUE = '—';

type FormatProbabilityOptions = {
  signDisplay?: Intl.NumberFormatOptions['signDisplay'];
};

export function formatProbability(value?: number | null, options?: FormatProbabilityOptions) {
  if (value === undefined || value === null) {
    return EMPTY_VALUE;
  }

  return value.toLocaleString('pt-BR', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2,
    signDisplay: options?.signDisplay,
    style: 'percent',
  });
}

export function formatDateTime(value?: string | null) {
  if (!value) {
    return EMPTY_VALUE;
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString('pt-BR', {
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    month: '2-digit',
  });
}

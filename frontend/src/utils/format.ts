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

/**
 * Day/month tick label for chart X axes fed by date-only strings (`YYYY-MM-DD`,
 * parsed as UTC midnight) — uses UTC getters so the label doesn't shift a day
 * off in timezones behind UTC (e.g. `America/Sao_Paulo`).
 */
export function formatDayMonthUTC(value: number): string {
  const date = new Date(value);
  const day = String(date.getUTCDate()).padStart(2, '0');
  const month = String(date.getUTCMonth() + 1).padStart(2, '0');

  return `${day}/${month}`;
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

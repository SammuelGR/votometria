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

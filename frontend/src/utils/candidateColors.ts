import { normalizeCandidate } from '~/utils/candidateNormalization';

/**
 * Categorical palette harmonized with the instrument theme (cool ground,
 * indigo = market, magenta = attention). Used to color candidate series.
 */
export const CANDIDATE_PALETTE = [
  '#2a3fc4', // indigo
  '#db1873', // magenta
  '#128a86', // teal
  '#c9761a', // amber
  '#6b788a', // slate
  '#7048e8', // violet
  '#2f9e44', // green
  '#c2255c', // crimson
  '#1098ad', // cyan
  '#e8590c', // deep orange
  '#5c940d', // dark lime
  '#9c36b5', // purple
  '#495057', // graphite
];

/** Stable colors for the most prominent candidates across years. */
const FIXED_COLORS: Record<string, string> = {
  Lula: '#2a3fc4',
  'Flávio Bolsonaro': '#db1873',
  Bolsonaro: '#2f9e44',
  Haddad: '#c2255c',
  'Ronaldo Caiado': '#128a86',
  'Romeu Zema': '#c9761a',
  'Aldo Rebelo': '#6b788a',
  'Ciro Gomes': '#1098ad',
  'Simone Tebet': '#9c36b5',
};

// Keyed by normalizeCandidate(...) so a raw Google Trends term (e.g. "Lula")
// and a poll's nome_candidato_normalizado (e.g. "lula") resolve to the same
// color — the two charts style the same candidate consistently.
const NORMALIZED_FIXED_COLORS: Record<string, string> = Object.fromEntries(
  Object.entries(FIXED_COLORS).map(([name, color]) => [normalizeCandidate(name), color]),
);

function hashString(value: string): number {
  let hash = 0;

  for (let i = 0; i < value.length; i += 1) {
    hash = (hash * 31 + value.charCodeAt(i)) | 0;
  }

  return Math.abs(hash);
}

/** Returns a stable color for a candidate term, raw or normalized. */
export function candidateColor(term: string): string {
  const normalized = normalizeCandidate(term);

  return NORMALIZED_FIXED_COLORS[normalized] ?? CANDIDATE_PALETTE[hashString(normalized) % CANDIDATE_PALETTE.length];
}

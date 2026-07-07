import type { ElectionYear } from '~/services/googleTrends';

/**
 * Lowercases, strips accents and collapses whitespace. Mirrors the Python
 * `normalize_name` used to build `nome_candidato_normalizado`, so a Trends term
 * and a poll candidate name fold to the same base string.
 */
export function normalizeCandidate(raw: string): string {
  return raw
    .normalize('NFD')
    .replace(/\p{Diacritic}/gu, '')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Year-scoped equivalence groups (values already normalized). Only the aliases
 * the task requires are encoded — nothing is merged globally.
 *
 * - `current` (2026): "Bolsonaro" ≡ "Flávio Bolsonaro". Datafolha records the
 *   2026 Bolsonaro-family candidate simply as "Flávio", so it joins the group
 *   too — otherwise the poll series for Bolsonaro/2026 would be empty.
 * - `2018`: "Haddad" ≡ "Fernando Haddad".
 *
 * 2022 has no group, so "Bolsonaro"/"Haddad" never merge outside 2026/2018.
 */
const ALIAS_GROUPS: Partial<Record<ElectionYear, string[][]>> = {
  current: [['bolsonaro', 'flavio bolsonaro', 'flavio']],
  '2018': [['haddad', 'fernando haddad']],
};

/**
 * Canonical candidate key for a given election, used to cross Trends terms with
 * poll candidate names. Returns the normalized name unless it falls into one of
 * the year's alias groups, in which case the group's first member is returned.
 */
export function normalizeCandidateForElection(candidate: string, electionYear: ElectionYear): string {
  const normalized = normalizeCandidate(candidate);
  const groups = ALIAS_GROUPS[electionYear] ?? [];

  for (const group of groups) {
    if (group.includes(normalized)) {
      return group[0];
    }
  }

  return normalized;
}

/** True when two candidate labels are equivalent for the given election. */
export function candidatesMatchForElection(a: string, b: string, electionYear: ElectionYear): boolean {
  return normalizeCandidateForElection(a, electionYear) === normalizeCandidateForElection(b, electionYear);
}

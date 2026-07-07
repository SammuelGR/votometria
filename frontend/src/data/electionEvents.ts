import type { ElectionYear } from '~/services/googleTrends';

export type EventImpact = 'low' | 'medium' | 'high';

export type ElectionEvent = {
  date: string;
  electionYear: ElectionYear;
  title: string;
  type: string;
  relatedTerms: string[];
  description: string;
  impact: EventImpact;
};

/**
 * Curated electoral events used to give context to Google Trends peaks.
 *
 * These are explanatory HYPOTHESES, not proven causes: an event near a peak
 * suggests a possible relationship, never guaranteed causality. Edit this list
 * to keep it current — see docs/dashboard_google_trends.md.
 */
export const ELECTION_EVENTS: ElectionEvent[] = [
  // --- 2018 ---
  {
    date: '2018-01-24',
    electionYear: '2018',
    title: 'Condenação de Lula no TRF-4',
    type: 'judicial',
    relatedTerms: ['Lula', 'TRF-4', 'Lava Jato'],
    description: 'O Tribunal Regional Federal da 4ª Região confirmou por unanimidade a condenação de Lula no caso do triplex e aumentou sua pena para 12 anos e 1 mês de prisão.',
    impact: 'high',
  },
  {
    date: '2018-04-07',
    electionYear: '2018',
    title: 'Prisão de Lula',
    type: 'judicial',
    relatedTerms: ['Lula', 'PT'],
    description: 'Lula se entregou à Polícia Federal em São Bernardo do Campo para cumprir pena no caso do triplex.',
    impact: 'high',
  },
  {
    date: '2018-08-09',
    electionYear: '2018',
    title: 'Primeiro debate presidencial na Band',
    type: 'debate',
    relatedTerms: ['Cabo Daciolo', 'Ciro Gomes', 'Bolsonaro'],
    description: 'Primeiro debate televisionado da eleição; forte repercussão de Cabo Daciolo e da URSAL nas redes.',
    impact: 'medium',
  },
  {
    date: '2018-08-15',
    electionYear: '2018',
    title: 'PT registra candidatura de Lula',
    type: 'campanha',
    relatedTerms: ['Lula', 'Haddad', 'PT'],
    description: 'O PT formalizou o registro da candidatura de Lula no TSE, ainda preso, com Haddad como vice.',
    impact: 'high',
  },
  {
    date: '2018-08-31',
    electionYear: '2018',
    title: 'TSE rejeita candidatura de Lula',
    type: 'judicial',
    relatedTerms: ['Lula', 'Haddad', 'PT'],
    description: 'O TSE rejeitou o registro de candidatura de Lula com base na Lei da Ficha Limpa.',
    impact: 'high',
  },
  {
    date: '2018-09-06',
    electionYear: '2018',
    title: 'Atentado contra Bolsonaro',
    type: 'campanha',
    relatedTerms: ['Bolsonaro'],
    description: 'Bolsonaro foi esfaqueado durante ato de campanha em Juiz de Fora.',
    impact: 'high',
  },
  {
    date: '2018-09-11',
    electionYear: '2018',
    title: 'Haddad substitui Lula',
    type: 'campanha',
    relatedTerms: ['Haddad', 'Lula', "Manuela d'Ávila"],
    description: 'O PT anunciou Fernando Haddad como candidato à Presidência.',
    impact: 'high',
  },
  {
    date: '2018-10-07',
    electionYear: '2018',
    title: 'Primeiro turno de 2018',
    type: 'resultado',
    relatedTerms: ['Bolsonaro', 'Haddad', 'Ciro Gomes'],
    description: 'Bolsonaro liderou o primeiro turno e Haddad ficou em segundo.',
    impact: 'high',
  },

  // --- 2022 ---
  {
    date: '2022-08-28',
    electionYear: '2022',
    title: 'Primeiro debate presidencial na Band',
    type: 'debate',
    relatedTerms: ['Lula', 'Bolsonaro', 'Ciro Gomes', 'Simone Tebet'],
    description: 'Primeiro debate televisionado com Lula e Bolsonaro presentes.',
    impact: 'medium',
  },
  {
    date: '2022-09-29',
    electionYear: '2022',
    title: 'Debate da Globo no primeiro turno',
    type: 'debate',
    relatedTerms: ['Lula', 'Bolsonaro', 'Simone Tebet', 'Padre Kelmon'],
    description: 'Último debate antes do primeiro turno, com forte repercussão nas redes.',
    impact: 'high',
  },
  {
    date: '2022-10-02',
    electionYear: '2022',
    title: 'Primeiro turno de 2022',
    type: 'resultado',
    relatedTerms: ['Lula', 'Bolsonaro', 'Simone Tebet', 'Ciro Gomes'],
    description: 'Lula liderou, mas a diferença para Bolsonaro foi menor que a esperada.',
    impact: 'high',
  },
  {
    date: '2022-10-23',
    electionYear: '2022',
    title: 'Roberto Jefferson ataca policiais federais',
    type: 'violencia-politica',
    relatedTerms: ['Roberto Jefferson', 'Bolsonaro', 'Padre Kelmon'],
    description: 'Roberto Jefferson resistiu à prisão, atirou e lançou granadas contra policiais federais.',
    impact: 'high',
  },
  {
    date: '2022-10-30',
    electionYear: '2022',
    title: 'Segundo turno e operações da PRF',
    type: 'resultado',
    relatedTerms: ['Lula', 'Bolsonaro', 'PRF'],
    description: 'Lula venceu a eleição mais apertada do período recente; houve polêmica sobre operações da PRF.',
    impact: 'high',
  },

  // --- current / 2026 (pré-campanha) ---
  {
    date: '2026-02-15',
    electionYear: 'current',
    title: 'Lula acompanha desfile em sua homenagem na Sapucaí',
    type: 'campanha',
    relatedTerms: ['Lula', 'Carnaval', 'Acadêmicos de Niterói', 'Sapucaí'],
    description: 'Lula assistiu ao desfile da Acadêmicos de Niterói, escola que homenageou sua trajetória política no Carnaval do Rio de Janeiro. O evento gerou ampla repercussão nacional e debates sobre possível promoção eleitoral em ano de eleição.',
    impact: 'medium',
  },
  {
    date: '2026-02-27',
    electionYear: 'current',
    title: 'Pesquisa eleitoral testa Flávio Bolsonaro contra Lula',
    type: 'pesquisa',
    relatedTerms: ['Lula', 'Flávio Bolsonaro', 'Paraná Pesquisas'],
    description: 'Pesquisa eleitoral divulgada no fim de fevereiro mostrou Flávio Bolsonaro competitivo em cenários presidenciais de 2026, ampliando a cobertura sobre a sucessão presidencial.',
    impact: 'medium',
  },
  {
    date: '2026-04-11',
    electionYear: 'current',
    title: 'Datafolha mostra empate técnico',
    type: 'pesquisa',
    relatedTerms: ['Lula', 'Flávio Bolsonaro'],
    description: 'Pesquisa Datafolha mostrou empate técnico entre Lula e Flávio Bolsonaro em eventual segundo turno.',
    impact: 'high',
  },
  {
    date: '2026-04-30',
    electionYear: 'current',
    title: 'Congresso reduz pena de Bolsonaro',
    type: 'judicial-politico',
    relatedTerms: ['Jair Bolsonaro', 'Flávio Bolsonaro', 'Lula'],
    description: 'Congresso aprovou redução de pena de Jair Bolsonaro após derrubar veto presidencial.',
    impact: 'high',
  },
  {
    date: '2026-05-06',
    electionYear: 'current',
    title: 'Pesquisas reforçam disputa entre Lula e Flávio Bolsonaro',
    type: 'pesquisa',
    relatedTerms: ['Lula', 'Flávio Bolsonaro', 'Pesquisa eleitoral'],
    description: 'Levantamentos divulgados no início de maio indicaram uma disputa acirrada entre Lula e Flávio Bolsonaro, aumentando a repercussão da pré-campanha presidencial.',
    impact: 'high',
  },
  {
    date: '2026-05-28',
    electionYear: 'current',
    title: 'Nova pesquisa eleitoral amplia cobertura da disputa presidencial',
    type: 'pesquisa',
    relatedTerms: ['Flávio Bolsonaro', 'Lula', 'Meio/Ideia'],
    description: 'Pesquisa divulgada no fim de maio mostrou mudanças nos cenários de intenção de voto entre Lula e Flávio Bolsonaro, gerando ampla repercussão política e na imprensa.',
    impact: 'high',
  },
  {
    date: '2026-06-16',
    electionYear: 'current',
    title: 'CNT/MDA mostra Lula ampliando vantagem',
    type: 'pesquisa',
    relatedTerms: ['Lula', 'Flávio Bolsonaro'],
    description: 'Pesquisa CNT/MDA mostrou Lula ampliando vantagem sobre Flávio Bolsonaro.',
    impact: 'medium',
  },
  {
    date: '2026-06-16',
    electionYear: 'current',
    title: 'STF condena Eduardo Bolsonaro',
    type: 'judicial',
    relatedTerms: ['Eduardo Bolsonaro', 'Jair Bolsonaro', 'Flávio Bolsonaro'],
    description: 'STF condenou Eduardo Bolsonaro por buscar interferência dos EUA no caso do pai.',
    impact: 'high',
  },
  {
    date: '2026-06-20',
    electionYear: 'current',
    title: 'Datafolha mostra Lula mantendo liderança',
    type: 'pesquisa',
    relatedTerms: ['Lula', 'Flávio Bolsonaro'],
    description: 'Datafolha mostrou Lula mantendo liderança sobre Flávio Bolsonaro.',
    impact: 'medium',
  },
];

export const EVENTS_DISCLAIMER_2026 =
  'Os eventos de 2026 representam o cenário de pré-campanha até a data de coleta e devem ser ' +
  'atualizados conforme novas pesquisas, candidaturas e fatos políticos surgirem.';

/** Events for a given election year, sorted by date ascending. */
export function eventsForYear(year: ElectionYear): ElectionEvent[] {
  return ELECTION_EVENTS.filter((event) => event.electionYear === year).sort((a, b) => a.date.localeCompare(b.date));
}

const MS_PER_DAY = 1000 * 60 * 60 * 24;

function daysBetween(a: string, b: string): number {
  return Math.abs((new Date(a).getTime() - new Date(b).getTime()) / MS_PER_DAY);
}

/** Nearest event to a date within the given window (in days), or null. */
export function nearestEvent(date: string, year: ElectionYear, windowDays = 7): ElectionEvent | null {
  let best: ElectionEvent | null = null;
  let bestDistance = Number.POSITIVE_INFINITY;

  for (const event of eventsForYear(year)) {
    const distance = daysBetween(date, event.date);

    if (distance <= windowDays && distance < bestDistance) {
      best = event;
      bestDistance = distance;
    }
  }

  return best;
}

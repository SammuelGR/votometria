import {
  Brush,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  type TooltipContentProps,
  XAxis,
  YAxis,
} from 'recharts';

import ChartTooltip from '~/components/charts/ChartTooltip';
import type { ElectionYear } from '~/services/googleTrends';
import type { ElectoralPanoramaPoint } from '~/utils/electoralPanorama';
import { formatDayMonthUTC } from '~/utils/format';

const GRID_COLOR = '#d2dae3';
const AXIS_COLOR = '#5c6b7a';
const ATTENTION_COLOR = '#db1873'; // magenta — atenção pública (Google Trends)
const POLLING_COLOR = '#2a3fc4'; // indigo — pesquisa eleitoral (Datafolha)
const MARKET_EXPECTATION_COLOR = '#2f9e44';
const ATTENTION_LABEL = 'Atenção pública';
const POLLING_LABEL = 'Pesquisa eleitoral';
const MARKET_EXPECTATION_LABEL = 'Expectativa de mercado';
// Source-explicit names used in the legend so the two series are never confused.
const ATTENTION_LEGEND = 'Atenção pública (índice 0–100)';
const POLLING_LEGEND = 'Pesquisas eleitorais (% de intenção de voto)';

function formatFullDate(date: string): string {
  const [year, month, day] = date.split('-');

  return `${day}/${month}/${year}`;
}

function electionYearLabel(year: ElectionYear): string {
  return year === 'current' ? '2026' : year;
}

type ElectoralPanoramaChartProps = {
  points: ElectoralPanoramaPoint[];
  candidate: string;
  year: ElectionYear;
};

export default function ElectoralPanoramaChart({ points, candidate, year }: ElectoralPanoramaChartProps) {
  const hasMarketExpectation = points.some((point) => point.marketExpectation != null);

  const renderTooltip = ({ active, payload, label }: TooltipContentProps) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    const datum = payload[0]?.payload as ElectoralPanoramaPoint | undefined;
    const date = datum?.date;
    const attention = datum?.attention;
    const polling = datum?.polling;
    const marketExpectation = datum?.marketExpectation;

    return (
      <ChartTooltip title={date ? formatFullDate(date) : label}>
        <div className="flex flex-col gap-0.5">
          <div className="text-foreground">
            {candidate} · {electionYearLabel(year)}
          </div>

          <div className="flex items-center justify-between gap-4">
            <span style={{ color: ATTENTION_COLOR }}>{ATTENTION_LABEL}</span>

            <span className="tabular-nums">{attention == null ? '—' : Math.round(attention)}</span>
          </div>

          <div className="flex items-center justify-between gap-4">
            <span style={{ color: POLLING_COLOR }}>{POLLING_LABEL}</span>

            <span className="tabular-nums">{polling == null ? '—' : `${polling.toFixed(1)}%`}</span>
          </div>

          {marketExpectation == null ? null : (
            <div className="flex items-center justify-between gap-4">
              <span style={{ color: MARKET_EXPECTATION_COLOR }}>{MARKET_EXPECTATION_LABEL}</span>

              <span className="tabular-nums">{`${marketExpectation.toFixed(1)}%`}</span>
            </div>
          )}
        </div>
      </ChartTooltip>
    );
  };

  return (
    <ResponsiveContainer height={320} width="100%">
      <LineChart data={points} margin={{ bottom: 0, left: 0, right: 12, top: 8 }}>
        <CartesianGrid stroke={GRID_COLOR} strokeDasharray="0" vertical={false} />

        <XAxis
          dataKey="ts"
          domain={['dataMin', 'dataMax']}
          minTickGap={24}
          scale="time"
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickFormatter={formatDayMonthUTC}
          type="number"
        />

        <YAxis
          domain={[0, 'auto']}
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickFormatter={(value: number) => `${value}%`}
          width={40}
        />

        <Tooltip content={renderTooltip} />

        <Legend
          wrapperStyle={{ fontFamily: 'monospace', fontSize: 11, lineHeight: 1.6 }}
          formatter={(value) => <span style={{ color: AXIS_COLOR }}>{value}</span>}
        />

        <Line
          connectNulls
          dataKey="attention"
          dot={false}
          isAnimationActive={false}
          name={ATTENTION_LEGEND}
          stroke={ATTENTION_COLOR}
          strokeWidth={2}
          type="monotone"
        />

        <Line
          connectNulls
          dataKey="polling"
          dot={false}
          isAnimationActive={false}
          name={POLLING_LEGEND}
          stroke={POLLING_COLOR}
          strokeWidth={2}
          type="monotone"
        />

        {hasMarketExpectation ? (
          <Line
            connectNulls
            dataKey="marketExpectation"
            dot={false}
            isAnimationActive={false}
            name={MARKET_EXPECTATION_LABEL}
            stroke={MARKET_EXPECTATION_COLOR}
            strokeWidth={2}
            type="monotone"
          />
        ) : null}

        <Brush dataKey="ts" height={22} stroke={AXIS_COLOR} tickFormatter={formatDayMonthUTC} travellerWidth={8} />
      </LineChart>
    </ResponsiveContainer>
  );
}

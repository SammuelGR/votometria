import { useMemo } from 'react';
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
import { candidateColor } from '~/utils/candidateColors';
import { buildPollMonthlyTimeline, formatCandidateLabel, type PollMonthlyPoint } from '~/utils/pesquisasMensais';
import type { PollMonthlyRow } from '~/services/pesquisasMensais';

const GRID_COLOR = '#d2dae3';
const AXIS_COLOR = '#5c6b7a';
const MONTHS_ABBR = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

function formatMonth(ts: number): string {
  const date = new Date(ts);

  return `${MONTHS_ABBR[date.getUTCMonth()]}/${String(date.getUTCFullYear()).slice(2)}`;
}

type PollsTimelinePoint = PollMonthlyPoint & { ts: number };

type PollsTimelineChartProps = {
  rows: PollMonthlyRow[];
  candidates: string[];
};

export default function PollsTimelineChart({ rows, candidates }: PollsTimelineChartProps) {
  const data = useMemo<PollsTimelinePoint[]>(
    () =>
      buildPollMonthlyTimeline(rows, candidates).map((point) => ({
        ...point,
        ts: Date.parse(point.date),
      })),
    [rows, candidates],
  );

  const renderTooltip = ({ active, payload, label }: TooltipContentProps) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    const datum = payload[0]?.payload as PollsTimelinePoint | undefined;
    const title = datum ? `${datum.mesReferencia} de ${datum.date.slice(0, 4)}` : String(label);
    const entries = payload
      .filter((entry) => entry.value != null && entry.dataKey != null)
      .map((entry) => ({ key: String(entry.dataKey), value: Number(entry.value), color: entry.color }))
      .sort((a, b) => b.value - a.value);

    return (
      <ChartTooltip title={title}>
        <div className="flex flex-col gap-0.5">
          {entries.map((entry) => (
            <div className="flex items-center justify-between gap-4" key={entry.key}>
              <span style={{ color: entry.color }}>{formatCandidateLabel(entry.key)}</span>

              <span className="tabular-nums">{entry.value.toFixed(1)}%</span>
            </div>
          ))}
        </div>
      </ChartTooltip>
    );
  };

  return (
    <ResponsiveContainer height={320} width="100%">
      <LineChart data={data} margin={{ bottom: 0, left: 0, right: 12, top: 8 }}>
        <CartesianGrid stroke={GRID_COLOR} strokeDasharray="0" vertical={false} />

        <XAxis
          dataKey="ts"
          domain={['dataMin', 'dataMax']}
          scale="time"
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickFormatter={formatMonth}
          type="number"
        />

        <YAxis
          domain={[0, 50]}
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickFormatter={(value: number) => `${value}%`}
          ticks={[0, 10, 20, 30, 40, 50]}
          width={40}
        />

        <Tooltip content={renderTooltip} />

        <Legend
          formatter={(value) => <span style={{ color: AXIS_COLOR }}>{formatCandidateLabel(String(value))}</span>}
          wrapperStyle={{ fontFamily: 'monospace', fontSize: 11, lineHeight: 1.6 }}
        />

        {candidates.map((candidate) => (
          <Line
            connectNulls={false}
            dataKey={candidate}
            dot={{ fill: candidateColor(candidate), r: 2.5, strokeWidth: 0 }}
            isAnimationActive={false}
            key={candidate}
            name={candidate}
            stroke={candidateColor(candidate)}
            strokeWidth={2}
            type="monotone"
          />
        ))}

        <Brush dataKey="ts" height={22} stroke={AXIS_COLOR} tickFormatter={formatMonth} travellerWidth={8} />
      </LineChart>
    </ResponsiveContainer>
  );
}

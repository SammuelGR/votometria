import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  type TooltipContentProps,
  XAxis,
  YAxis,
} from 'recharts';

import ChartTooltip from '~/components/charts/ChartTooltip';
import type { TseVoteRow } from '~/services/tseVotes';

const AXIS_COLOR = '#5c6b7a';
const TOP_COLORS = ['#2a3fc4', '#db1873'];
const REST_COLOR = '#9aa7b4';

function barColor(index: number): string {
  return TOP_COLORS[index] ?? REST_COLOR;
}

type TseVotesChartProps = {
  rows: TseVoteRow[];
};

export default function TseVotesChart({ rows }: TseVotesChartProps) {
  // sort adicionado para garantir a ordem visual
  const chartRows = [...rows].sort((left, right) => right.votes - left.votes);
  const height = Math.max(220, chartRows.length * 44);

  const renderTooltip = ({ active, payload }: TooltipContentProps) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    const entry = payload[0]?.payload as TseVoteRow | undefined;

    if (!entry) {
      return null;
    }

    const totalVotes = chartRows.reduce((sum, row) => sum + row.votes, 0);
    const sharePercent = totalVotes === 0 ? 0 : (entry.votes / totalVotes) * 100;

    return (
      <ChartTooltip title={entry.candidate}>
        <div className="flex items-center justify-between gap-4">
          <span className="text-muted">votos</span>

          <span className="tabular-nums">{entry.votes.toLocaleString('pt-BR')}</span>
        </div>

        <div className="flex items-center justify-between gap-4">
          <span className="text-muted">participação</span>

          <span className="tabular-nums">
            {sharePercent.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%
          </span>
        </div>
      </ChartTooltip>
    );
  };

  return (
    <ResponsiveContainer height={height} width="100%">
      <BarChart data={chartRows} layout="vertical" margin={{ bottom: 4, left: 4, right: 100, top: 4 }}>
        <XAxis
          axisLine={false}
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickFormatter={(value) => {
            const normalized = typeof value === 'number' || typeof value === 'string' ? Number(value) : NaN;

            return Number.isFinite(normalized) ? normalized.toLocaleString('pt-BR') : '';
          }}
          tickLine={false}
          type="number"
        />

        <YAxis
          dataKey="candidate"
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          type="category"
          width={160}
        />

        <Tooltip content={renderTooltip} cursor={{ fill: 'rgba(21,33,46,0.04)' }} />

        <Bar dataKey="votes" isAnimationActive={false} radius={[0, 2, 2, 0]}>
          {chartRows.map((entry, index) => (
            <Cell fill={barColor(index)} key={entry.candidate} />
          ))}

          <LabelList
            dataKey="votes"
            formatter={(value) => {
              const normalized = typeof value === 'number' || typeof value === 'string' ? Number(value) : NaN;

              return Number.isFinite(normalized) ? normalized.toLocaleString('pt-BR') : '';
            }}
            position="right"
            style={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
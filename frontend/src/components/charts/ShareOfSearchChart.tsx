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
import type { CandidateShare } from '~/utils/trends';

const AXIS_COLOR = '#5c6b7a';
const TOP_COLORS = ['#2a3fc4', '#db1873'];
const REST_COLOR = '#9aa7b4';

function barColor(index: number): string {
  return TOP_COLORS[index] ?? REST_COLOR;
}

type ShareOfSearchChartProps = {
  shares: CandidateShare[];
  periodLabel?: string;
};

export default function ShareOfSearchChart({ shares, periodLabel }: ShareOfSearchChartProps) {
  const height = Math.max(160, shares.length * 40);

  const renderTooltip = ({ active, payload }: TooltipContentProps) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    const entry = payload[0]?.payload as CandidateShare | undefined;

    if (!entry) {
      return null;
    }

    return (
      <ChartTooltip title={entry.term}>
        <div className="flex flex-col gap-0.5">
          <div className="flex items-center justify-between gap-4">
            <span className="text-muted">share of search</span>

            <span className="tabular-nums">{entry.share.toFixed(1)}%</span>
          </div>

          <div className="flex items-center justify-between gap-4">
            <span className="text-muted">interesse médio</span>

            <span className="tabular-nums">{Math.round(entry.mean)}</span>
          </div>

          {periodLabel ? <div className="text-muted mt-1">{periodLabel}</div> : null}
        </div>
      </ChartTooltip>
    );
  };

  return (
    <ResponsiveContainer height={height} width="100%">
      <BarChart data={shares} layout="vertical" margin={{ bottom: 4, left: 4, right: 40, top: 4 }}>
        <XAxis
          domain={[0, 'dataMax']}
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickFormatter={(value: number) => `${value}%`}
          type="number"
        />

        <YAxis
          dataKey="term"
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          type="category"
          width={130}
        />

        <Tooltip content={renderTooltip} cursor={{ fill: 'rgba(21,33,46,0.04)' }} />

        <Bar dataKey="share" isAnimationActive={false} radius={[0, 2, 2, 0]}>
          {shares.map((entry, index) => (
            <Cell fill={barColor(index)} key={entry.term} />
          ))}

          <LabelList
            dataKey="share"
            formatter={(value) => `${Math.round(Number(value))}%`}
            position="right"
            style={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

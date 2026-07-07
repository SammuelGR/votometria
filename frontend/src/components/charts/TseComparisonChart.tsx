import {
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
import type { TseComparisonRow } from '~/services/tseComparison';

const GRID_COLOR = '#d2dae3';
const AXIS_COLOR = '#5c6b7a';
const LINE_COLORS = ['#2a3fc4', '#db1873', '#1f8f5f', '#f59e0b', '#7c3aed', '#0f766e'];

type TseComparisonChartProps = {
  rows: TseComparisonRow[];
};

type ChartDatum = {
  name: string;
  [candidateName: string]: number | string;
};

function formatVotes(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value);
}

function lineColor(index: number): string {
  return LINE_COLORS[index] ?? '#5c6b7a';
}

export default function TseComparisonChart({ rows }: TseComparisonChartProps) {
    const chartData: ChartDatum[] = [
        { name: '1º turno', ...Object.fromEntries(rows.map((row) => [row.NM_URNA_CANDIDATO, row.QT_VOTOS_1T])) },
        { name: '2º turno', ...Object.fromEntries(rows.map((row) => [row.NM_URNA_CANDIDATO, row.QT_VOTOS_2T])) },
    ];

    const values = rows.flatMap((row) => [
        row.QT_VOTOS_1T,
        row.QT_VOTOS_2T,
    ]);

    const minValue = Math.min(...values);
    const maxValue = Math.max(...values);

    const STEP = 5_000_000;

    const yMin = Math.floor(minValue / STEP) * STEP;
    const yMax = Math.ceil(maxValue / STEP) * STEP;

    const ticks = Array.from(
        { length: (yMax - yMin) / STEP + 1 },
        (_, i) => yMin + i * STEP,
    );

  const renderTooltip = ({ active, payload, label }: TooltipContentProps) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    return (
      <ChartTooltip title={label as string}>
        <div className="flex flex-col gap-0.5">
          {payload.map((entry, index) => (
            <div className="flex items-center justify-between gap-4" key={`${entry.name}-${index}`}>
              <span style={{ color: lineColor(index) }}>{entry.name as string}</span>

              <span className="tabular-nums">{formatVotes(Number(entry.value))}</span>
            </div>
          ))}
        </div>
      </ChartTooltip>
    );
  };

  return (
    <ResponsiveContainer height={320} width="100%">
      <LineChart data={chartData} margin={{ bottom: 0, left: 100, right: 150, top: 8 }}>
        <CartesianGrid stroke={GRID_COLOR} strokeDasharray="0" vertical={false} />

        <XAxis
          dataKey="name"
          stroke={AXIS_COLOR}
          tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }}
          tickMargin={8}
          padding={{ left: 100, right: 100 }}
        />

        <YAxis
            stroke={AXIS_COLOR}
            tick={{
                fill: AXIS_COLOR,
                fontFamily: 'monospace',
                fontSize: 11,
            }}
            width={70}
            domain={[yMin, yMax]}
            ticks={ticks}
            tickFormatter={formatVotes}
        />

        <Tooltip content={renderTooltip} />

        <Legend
          wrapperStyle={{ fontFamily: 'monospace', fontSize: 11, lineHeight: 1.6 }}
          formatter={(value) => <span style={{ color: AXIS_COLOR }}>{value}</span>}
        />

        {rows.map((row, index) => (
          <Line
            dataKey={row.NM_URNA_CANDIDATO}
            dot={{
                r: 4,
                fill: lineColor(index),
                stroke: '#fff',
                strokeWidth: 2,
            }}
            isAnimationActive={false}
            key={row.NM_URNA_CANDIDATO}
            name={row.NM_URNA_CANDIDATO}
            stroke={lineColor(index)}
            strokeWidth={3}
            type="monotone"
            /*
            label={(props) => {
                const { x, y, index } = props;

                if (index !== chartData.length - 1) return null;

                return (
                    <text
                    x={Number(x) + 12}
                    y={Number(y) + 5}
                    fill={lineColor(index)}
                    fontFamily="monospace"
                    fontSize={12}
                    fontWeight={700}
                    >
                    {row.NM_URNA_CANDIDATO}
                    </text>
                );
            }}
            */
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}

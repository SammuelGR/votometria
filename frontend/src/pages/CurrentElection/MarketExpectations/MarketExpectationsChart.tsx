import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

import type { MarketExpectationInterval, MarketExpectationSeries } from '~/models/marketExpectations';
import { formatDateTime, formatProbability } from '~/utils/format';

type MarketExpectationsChartProps = {
  interval: MarketExpectationInterval;
  series: MarketExpectationSeries[];
};

type ChartRow = {
  timestampMs: number;
} & Record<string, number | string>;

const CHART_COLORS = [
  'var(--color-chart-1)',
  'var(--color-chart-2)',
  'var(--color-chart-3)',
  'var(--color-chart-4)',
  'var(--color-chart-5)',
  'var(--color-chart-6)',
];

export default function MarketExpectationsChart({ interval, series }: MarketExpectationsChartProps) {
  const lines = series.map((candidateSeries, index) => ({
    color: CHART_COLORS[index % CHART_COLORS.length],
    key: getSeriesKey(candidateSeries),
    name: candidateSeries.displayName,
  }));
  const data = buildChartData(series, interval);

  return (
    <div className="h-72 min-w-0">
      <ResponsiveContainer height="100%" width="100%">
        <LineChart data={data} margin={{ bottom: 8, left: 12, right: 16, top: 8 }}>
          <CartesianGrid stroke="var(--color-border)" strokeDasharray="4 4" vertical={false} />

          <XAxis
            dataKey="timestampMs"
            domain={['dataMin', 'dataMax']}
            minTickGap={24}
            scale="time"
            tickFormatter={(value) => formatDateTimeFromTimestamp(Number(value))}
            tickLine={false}
            tickMargin={8}
            type="number"
          />

          <YAxis
            domain={['auto', 'auto']}
            tickFormatter={(value) => formatProbability(Number(value))}
            tickLine={false}
            tickMargin={8}
            width={76}
          />

          <Tooltip
            formatter={(value, name) => [formatProbability(Number(value)), name]}
            labelFormatter={(label) => formatDateTimeFromTimestamp(Number(label))}
            wrapperStyle={{ zIndex: 50 }}
          />

          <Legend />

          {lines.map((line) => (
            <Line
              dataKey={line.key}
              dot={false}
              key={line.name}
              name={line.name}
              stroke={line.color}
              strokeWidth={2}
              type="linear"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function buildChartData(series: MarketExpectationSeries[], interval: MarketExpectationInterval) {
  const rowsByTimestamp = new Map<number, ChartRow>();

  series.forEach((candidateSeries) => {
    const seriesKey = getSeriesKey(candidateSeries);

    candidateSeries.points.forEach((point) => {
      const timestampMs = getBucketTimestamp(point.timestamp, interval);
      const row = rowsByTimestamp.get(timestampMs) ?? { timestampMs };
      row[seriesKey] = point.probability;
      rowsByTimestamp.set(timestampMs, row);
    });
  });

  return Array.from(rowsByTimestamp.values()).toSorted(
    (firstRow, secondRow) => firstRow.timestampMs - secondRow.timestampMs,
  );
}

function formatDateTimeFromTimestamp(value: number) {
  return formatDateTime(new Date(value).toISOString());
}

function getBucketTimestamp(value: string, interval: MarketExpectationInterval) {
  const date = new Date(value);

  if (interval === '1w') {
    const weekDay = date.getDay();
    const daysFromMonday = (weekDay + 6) % 7;
    date.setDate(date.getDate() - daysFromMonday);
    date.setHours(0, 0, 0, 0);

    return date.getTime();
  }

  if (interval === '1d') {
    date.setHours(0, 0, 0, 0);

    return date.getTime();
  }

  if (interval === '4h') {
    date.setHours(Math.floor(date.getHours() / 4) * 4, 0, 0, 0);

    return date.getTime();
  }

  date.setMinutes(0, 0, 0);

  return date.getTime();
}

function getSeriesKey(series: MarketExpectationSeries) {
  return `${series.candidateCatalogId}:${series.marketId}`;
}

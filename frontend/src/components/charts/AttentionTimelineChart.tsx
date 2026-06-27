import { useMemo } from 'react';
import {
  Brush,
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  type TooltipContentProps,
  XAxis,
  YAxis,
} from 'recharts';

import ChartTooltip from '~/components/charts/ChartTooltip';
import { EventDetails } from '~/components/charts/EventMarker';
import { eventsForYear } from '~/data/electionEvents';
import type { ElectionYear, TrendsMetric, TrendsRow } from '~/services/googleTrends';
import { candidateColor } from '~/utils/candidateColors';
import { EVENT_FLAG_COLOR, EVENT_LINE_COLOR, groupEventsByNearestTs } from '~/utils/events';
import { buildTimeline, detectPeaks, termsByMean } from '~/utils/trends';

const GRID_COLOR = '#d2dae3';
const AXIS_COLOR = '#5c6b7a';
const MONTHS_ABBR = ['jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez'];

function formatMonth(ts: number): string {
  const date = new Date(ts);

  return `${MONTHS_ABBR[date.getUTCMonth()]}/${String(date.getUTCFullYear()).slice(2)}`;
}

function formatFullDate(date: string): string {
  const [year, month, day] = date.split('-');

  return `${day}/${month}/${year}`;
}

type AttentionTimelineChartProps = {
  rows: TrendsRow[];
  terms: string[];
  metric: TrendsMetric;
  year: ElectionYear;
  showEvents: boolean;
};

export default function AttentionTimelineChart({ rows, terms, metric, year, showEvents }: AttentionTimelineChartProps) {
  const data = useMemo(
    () =>
      buildTimeline(rows, terms, metric).map((point) => ({
        ...point,
        ts: Date.parse(point.date as string),
      })),
    [rows, terms, metric],
  );

  const peakSet = useMemo(() => {
    const peaks = detectPeaks(buildTimeline(rows, terms, metric), terms, year);

    return new Set(peaks.map((peak) => `${peak.term}|${peak.date}`));
  }, [rows, terms, metric, year]);

  const emphasized = useMemo(
    () =>
      new Set(
        termsByMean(rows, metric)
          .filter((term) => terms.includes(term))
          .slice(0, 4),
      ),
    [rows, metric, terms],
  );

  const events = useMemo(() => (showEvents ? eventsForYear(year) : []), [showEvents, year]);
  const eventsByTs = useMemo(
    () =>
      groupEventsByNearestTs(
        events,
        data.map((point) => point.ts),
      ),
    [events, data],
  );

  const renderDot = (term: string) => {
    const color = candidateColor(term);

    return (props: { cx?: number; cy?: number; index?: number; payload?: Record<string, unknown> }) => {
      const { cx, cy, index, payload } = props;
      const key = `${term}-${index}`;

      if (cx == null || cy == null || !payload) {
        return <g key={key} />;
      }

      const isPeak = peakSet.has(`${term}|${payload.date as string}`);
      const isPartial = Boolean(payload[`${term}__partial`]);

      if (isPeak) {
        return <circle cx={cx} cy={cy} fill={color} key={key} r={4} stroke="#fff" strokeWidth={1.5} />;
      }

      if (isPartial) {
        return <circle cx={cx} cy={cy} fill="none" key={key} r={2.5} stroke={color} strokeWidth={1.2} />;
      }

      return <g key={key} />;
    };
  };

  const renderTooltip = ({ active, payload, label }: TooltipContentProps) => {
    if (!active || !payload || payload.length === 0) {
      return null;
    }

    const datum = payload[0]?.payload as { date?: string } | undefined;
    const date = datum?.date;
    const entries = payload
      .filter((entry) => entry.value != null && entry.dataKey != null)
      .map((entry) => ({ key: String(entry.dataKey), value: Number(entry.value), color: entry.color }))
      .sort((a, b) => b.value - a.value);
    const ts = typeof label === 'number' ? label : undefined;
    const eventsHere = ts != null ? (eventsByTs.get(ts) ?? []) : [];
    const hasPeak = date != null && entries.some((entry) => peakSet.has(`${entry.key}|${date}`));

    return (
      <ChartTooltip title={date ? formatFullDate(date) : ''}>
        <div className="flex flex-col gap-0.5">
          {entries.map((entry) => (
            <div className="flex items-center justify-between gap-4" key={entry.key}>
              <span style={{ color: entry.color }}>{entry.key}</span>

              <span className="tabular-nums">{Math.round(entry.value)}</span>
            </div>
          ))}
        </div>

        {hasPeak ? <div className="text-muted mt-1">pico detectado</div> : null}

        {eventsHere.length > 0 ? (
          <div className="border-border mt-1 border-t pt-1">
            <div className="text-muted">evento próximo (contexto, não causa)</div>

            <EventDetails events={eventsHere} />
          </div>
        ) : null}
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

        <YAxis stroke={AXIS_COLOR} tick={{ fill: AXIS_COLOR, fontFamily: 'monospace', fontSize: 11 }} width={34} />

        <Tooltip content={renderTooltip} />

        {events.map((event) => (
          <ReferenceLine
            key={`${event.date}-${event.title}`}
            label={{ fill: EVENT_FLAG_COLOR, fontSize: 10, position: 'top', value: '▾' }}
            stroke={EVENT_LINE_COLOR}
            strokeDasharray="3 4"
            x={Date.parse(event.date)}
          />
        ))}

        {terms.map((term) => {
          const isEmphasized = emphasized.has(term);

          return (
            <Line
              connectNulls={false}
              dataKey={term}
              dot={renderDot(term)}
              isAnimationActive={false}
              key={term}
              stroke={candidateColor(term)}
              strokeOpacity={isEmphasized ? 1 : 0.45}
              strokeWidth={isEmphasized ? 2 : 1.4}
              type="monotone"
            />
          );
        })}

        <Brush dataKey="ts" height={22} stroke={AXIS_COLOR} tickFormatter={formatMonth} travellerWidth={8} />
      </LineChart>
    </ResponsiveContainer>
  );
}

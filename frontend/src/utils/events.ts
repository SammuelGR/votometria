import type { ElectionEvent } from '~/data/electionEvents';

export const EVENT_LINE_COLOR = 'rgba(21, 33, 46, 0.22)';
export const EVENT_FLAG_COLOR = '#db1873';

/** Maps each event to the nearest timestamp present in the timeline. */
export function groupEventsByNearestTs(events: ElectionEvent[], timestamps: number[]): Map<number, ElectionEvent[]> {
  const grouped = new Map<number, ElectionEvent[]>();

  if (timestamps.length === 0) {
    return grouped;
  }

  for (const event of events) {
    const eventTs = Date.parse(event.date);
    const nearest = timestamps.reduce(
      (best, ts) => (Math.abs(ts - eventTs) < Math.abs(best - eventTs) ? ts : best),
      timestamps[0],
    );

    const bucket = grouped.get(nearest);

    if (bucket) {
      bucket.push(event);
    } else {
      grouped.set(nearest, [event]);
    }
  }

  return grouped;
}

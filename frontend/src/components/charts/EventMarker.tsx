import type { ElectionEvent } from '~/data/electionEvents';

/** Compact list of events used inside chart tooltips. */
export function EventDetails({ events }: { events: ElectionEvent[] }) {
  return (
    <ul className="mt-1 flex flex-col gap-1">
      {events.map((event) => (
        <li className="text-foreground" key={`${event.date}-${event.title}`}>
          <span className="text-foreground">{event.title}</span>

          <span className="text-muted"> · {event.type}</span>
        </li>
      ))}
    </ul>
  );
}

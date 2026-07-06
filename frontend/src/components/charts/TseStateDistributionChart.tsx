import { useEffect, useMemo, useState } from 'react';
import { ComposableMap, Geographies, Geography, ZoomableGroup } from 'react-simple-maps';

import ChartTooltip from '~/components/charts/ChartTooltip';
import type { TseStateDistRow } from '~/services/tseStateDist';
import { candidateColor } from '~/utils/candidateColors';

type TseStateDistributionChartProps = {
  rows: TseStateDistRow[];
};

type TooltipState = {
  row: TseStateDistRow | null;
  x: number;
  y: number;
};

const BRASIL_GEO_URL = '/brazil-states.geojson';

function formatVotes(value: number): string {
  return new Intl.NumberFormat('pt-BR').format(value);
}

export default function TseStateDistributionChart({ rows }: TseStateDistributionChartProps) {
  const [hovered, setHovered] = useState<TooltipState>({ row: null, x: 0, y: 0 });

  useEffect(() => {
    async function loadGeo() {
      await fetch(BRASIL_GEO_URL);
    }

    void loadGeo();
  }, []);

  const legendItems = useMemo(() => {
    const seen = new Set<string>();

    return rows
      .flatMap((row) => row.candidates)
      .filter((candidate) => {
        if (seen.has(candidate.name)) {
          return false;
        }

        seen.add(candidate.name);
        return true;
      })
      .sort((a, b) => b.votes - a.votes);
  }, [rows]);

  return (
    <div className="flex flex-col gap-4 lg:flex-row">
      <div className="flex-1 rounded-md border border-border bg-surface p-2">
        <ComposableMap projection="geoMercator" projectionConfig={{ center: [-54, -14], scale: 900 }}>
          <ZoomableGroup center={[-54, -14]} disablePanning zoom={1}>
            <Geographies geography={BRASIL_GEO_URL}>
              {({ geographies: mapGeographies }) =>
                (mapGeographies as Array<{ properties?: { sigla?: string; name?: string }; rsmKey?: string }>).map((geo) => {
                  const uf = (geo.properties?.sigla as string | undefined) ?? (geo.properties?.name as string | undefined);
                  const row = rows.find((entry) => entry.uf === uf);
                  const winnerColor = row ? candidateColor(row.winner.name) : '#e5e7eb';

                  return (
                    <Geography
                      geography={geo as never}
                      key={geo.rsmKey ?? uf}
                      onMouseEnter={(event) => {
                        setHovered({ row: row ?? null, x: event.clientX, y: event.clientY });
                      }}
                      onMouseLeave={() => setHovered({ row: null, x: 0, y: 0 })}
                      style={{
                        default: { fill: winnerColor, outline: 'none' },
                        hover: { fill: '#1f2937', outline: 'none' },
                        pressed: { fill: '#111827', outline: 'none' },
                      }}
                    />
                  );
                })
              }
            </Geographies>
          </ZoomableGroup>
        </ComposableMap>
      </div>

      <div className="flex min-w-[220px] flex-col gap-2 rounded-md border border-border bg-navigation p-3">
        <p className="font-mono text-[11px] uppercase tracking-wide text-muted">Legenda</p>

        {legendItems.map((candidate) => (
          <div className="flex items-center gap-2" key={candidate.name}>
            <span className="size-3 rounded-sm" style={{ backgroundColor: candidateColor(candidate.name) }} />
            <span className="font-mono text-xs text-foreground">{candidate.name}</span>
          </div>
        ))}
      </div>

      {hovered.row ? (
        <div className="fixed z-50 pointer-events-none" style={{ left: hovered.x + 12, top: hovered.y + 12 }}>
          <ChartTooltip title={hovered.row.uf}>
            <div className="flex flex-col gap-0.5">
              {[...hovered.row.candidates]
                .sort((a, b) => b.votes - a.votes)
                .map((candidate) => (
                  <div className="flex items-center justify-between gap-4" key={candidate.name}>
                    <span style={{ color: candidateColor(candidate.name) }}>{candidate.name}</span>

                    <span className="tabular-nums">{formatVotes(candidate.votes)}</span>
                  </div>
                ))}
            </div>
          </ChartTooltip>
        </div>
      ) : null}
    </div>
  );
}

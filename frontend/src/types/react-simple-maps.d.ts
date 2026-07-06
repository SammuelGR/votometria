declare module 'react-simple-maps' {
  import type { ReactNode, MouseEvent } from 'react';

  export type GeographyShape = {
    rsmKey: string;
    properties?: {
      name?: string;
      [key: string]: unknown;
    };
    [key: string]: unknown;
  };

  type GeographyProps = {
    geography: GeographyShape;
    key?: string;
    onMouseEnter?: (event: MouseEvent<SVGPathElement>) => void;
    onMouseLeave?: () => void;
    style?: Record<string, Record<string, string | number | undefined>>;
  };

  type GeographiesProps = {
    geography: string;
    children: (props: { geographies: GeographyShape[] }) => ReactNode;
  };

  type ComposableMapProps = {
    children: ReactNode;
    projection?: string;
    projectionConfig?: {
      center?: [number, number];
      scale?: number;
      [key: string]: number | [number, number] | undefined;
    };
  };

  type ZoomableGroupProps = {
    children: ReactNode;
    center?: [number, number];
    disablePanning?: boolean;
    zoom?: number;
  };

  export function ComposableMap(props: ComposableMapProps): JSX.Element;
  export function Geographies(props: GeographiesProps): JSX.Element;
  export function Geography(props: GeographyProps): JSX.Element;
  export function ZoomableGroup(props: ZoomableGroupProps): JSX.Element;
}

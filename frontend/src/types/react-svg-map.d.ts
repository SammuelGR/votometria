declare module 'react-svg-map' {
  import type { ReactNode, MouseEvent } from 'react';

  export type SVGMapLocation = {
    id: string;
    properties?: {
      name?: string;
      sigla?: string;
      [key: string]: unknown;
    };
    [key: string]: unknown;
  };

  type SVGMapProps = {
    className?: string;
    map: unknown;
    onLocationMouseOver?: (location: SVGMapLocation) => void;
    onLocationMouseOut?: () => void;
    locationClassName?: (location: SVGMapLocation) => string;
  };

  export function SVGMap(props: SVGMapProps): ReactNode;
}

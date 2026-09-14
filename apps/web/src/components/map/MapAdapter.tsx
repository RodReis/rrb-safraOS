import "@geoman-io/leaflet-geoman-free/dist/leaflet-geoman.css";
import "leaflet/dist/leaflet.css";

import type { Layer, Map as LeafletMap } from "leaflet";
import { useEffect, useRef } from "react";
import { GeoJSON, MapContainer, TileLayer, useMap } from "react-leaflet";

export interface TalhaoGeometry {
  type: "Polygon" | "MultiPolygon";
  coordinates: unknown;
}

export interface MapAdapterExistingGeometry {
  id: string;
  name: string;
  geometry: TalhaoGeometry;
}

export interface MapAdapterProps {
  existingGeometries: MapAdapterExistingGeometry[];
  onDraw?: (geometry: TalhaoGeometry) => void;
  tenantKey: string;
}

const BRAZIL_CENTER: [number, number] = [-15.78, -47.93];
const BRAZIL_DEFAULT_ZOOM = 4;

function DrawControls({ onDraw }: { onDraw?: (geometry: TalhaoGeometry) => void }) {
  const map = useMap();

  useEffect(() => {
    if (!onDraw) {
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const pmMap = map as unknown as { pm: any };
    if (!pmMap.pm) {
      // ponytail: geoman nao inicializa `map.pm` em jsdom (sem canvas real); no-op seguro em teste, sem efeito no browser real.
      return;
    }
    pmMap.pm.addControls({
      position: "topleft",
      drawMarker: false,
      drawCircle: false,
      drawCircleMarker: false,
      drawPolyline: false,
      drawRectangle: false,
      drawText: false,
    });

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const handleCreate = (event: any) => {
      const layer = event.layer as Layer & { toGeoJSON: () => GeoJSON.Feature };
      const feature = layer.toGeoJSON();
      onDraw(feature.geometry as TalhaoGeometry);
    };

    map.on("pm:create", handleCreate);
    return () => {
      map.off("pm:create", handleCreate);
    };
  }, [map, onDraw]);

  return null;
}

export function MapAdapter({ existingGeometries, onDraw, tenantKey }: MapAdapterProps) {
  const mapRef = useRef<LeafletMap | null>(null);

  return (
    <div role="region" aria-label="Mapa de talhões" key={tenantKey}>
      <MapContainer
        center={BRAZIL_CENTER}
        zoom={BRAZIL_DEFAULT_ZOOM}
        style={{ height: "100%", width: "100%", minHeight: 480 }}
        ref={mapRef}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {existingGeometries.map((item) => (
          <GeoJSON key={item.id} data={item.geometry as GeoJSON.Geometry} />
        ))}
        <DrawControls onDraw={onDraw} />
      </MapContainer>
    </div>
  );
}

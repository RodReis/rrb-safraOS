import type { TalhaoGeometry } from "../../../components/map/MapAdapter";

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const VALID_GEOMETRY_TYPES = new Set(["Polygon", "MultiPolygon"]);

export class GeoJsonImportError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
    this.name = "GeoJsonImportError";
  }
}

export async function extractGeometryFromGeoJsonFile(file: File): Promise<TalhaoGeometry> {
  if (file.size > MAX_FILE_SIZE_BYTES) {
    throw new GeoJsonImportError("talhoes.payload_too_large", "Arquivo GeoJSON acima de 5 MB.");
  }

  const text = await file.text();
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new GeoJsonImportError("talhoes.invalid_file", "Arquivo nao e um GeoJSON valido.");
  }

  const candidate =
    typeof parsed === "object" && parsed !== null && "geometry" in parsed
      ? (parsed as { geometry: unknown }).geometry
      : parsed;

  if (
    typeof candidate !== "object" ||
    candidate === null ||
    !("type" in candidate) ||
    !VALID_GEOMETRY_TYPES.has((candidate as { type: string }).type)
  ) {
    throw new GeoJsonImportError(
      "talhoes.invalid_geometry_type",
      "Geometria deve ser do tipo Polygon ou MultiPolygon.",
    );
  }

  if (!("coordinates" in candidate) || !Array.isArray((candidate as { coordinates: unknown }).coordinates)) {
    throw new GeoJsonImportError(
      "talhoes.invalid_geometry_type",
      "Geometria deve conter um array de coordenadas valido.",
    );
  }

  return candidate as TalhaoGeometry;
}

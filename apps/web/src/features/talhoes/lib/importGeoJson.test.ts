import { describe, expect, it } from "vitest";

import { extractGeometryFromGeoJsonFile, GeoJsonImportError } from "./importGeoJson";

function makeFile(content: string, name = "talhao.geojson"): File {
  return new File([content], name, { type: "application/geo+json" });
}

describe("extractGeometryFromGeoJsonFile", () => {
  it("extracts geometry from a raw Polygon", async () => {
    const file = makeFile(JSON.stringify({ type: "Polygon", coordinates: [[[0, 0], [0, 1], [1, 1], [0, 0]]] }));

    const geometry = await extractGeometryFromGeoJsonFile(file);

    expect(geometry.type).toBe("Polygon");
  });

  it("extracts geometry from a Feature wrapper", async () => {
    const file = makeFile(
      JSON.stringify({
        type: "Feature",
        properties: {},
        geometry: { type: "MultiPolygon", coordinates: [] },
      }),
    );

    const geometry = await extractGeometryFromGeoJsonFile(file);

    expect(geometry.type).toBe("MultiPolygon");
  });

  it("rejects a file larger than 5MB", async () => {
    const bigContent = JSON.stringify({ type: "Polygon", coordinates: [] }) + " ".repeat(6 * 1024 * 1024);
    const file = makeFile(bigContent);

    await expect(extractGeometryFromGeoJsonFile(file)).rejects.toMatchObject({
      code: "talhoes.payload_too_large",
    });
  });

  it("rejects a file with unsupported geometry type", async () => {
    const file = makeFile(JSON.stringify({ type: "Point", coordinates: [0, 0] }));

    await expect(extractGeometryFromGeoJsonFile(file)).rejects.toMatchObject({
      code: "talhoes.invalid_geometry_type",
    });
  });

  it("rejects invalid JSON", async () => {
    const file = makeFile("not json");

    await expect(extractGeometryFromGeoJsonFile(file)).rejects.toBeInstanceOf(GeoJsonImportError);
  });

  it("rejects a Polygon without coordinates field", async () => {
    const file = makeFile(JSON.stringify({ type: "Polygon" }));

    await expect(extractGeometryFromGeoJsonFile(file)).rejects.toMatchObject({
      code: "talhoes.invalid_geometry_type",
    });
  });

  it("rejects a Polygon with coordinates as string instead of array", async () => {
    const file = makeFile(JSON.stringify({ type: "Polygon", coordinates: "nao-e-array" }));

    await expect(extractGeometryFromGeoJsonFile(file)).rejects.toMatchObject({
      code: "talhoes.invalid_geometry_type",
    });
  });
});

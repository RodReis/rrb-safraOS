import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";

import { MapAdapter, type TalhaoGeometry } from "../../../components/map/MapAdapter";
import { extractGeometryFromGeoJsonFile, GeoJsonImportError } from "../lib/importGeoJson";
import { talhaoFormSchema, type TalhaoFormValues } from "../schemas/talhaoSchema";

export interface TalhaoFormProps {
  farmId: string;
  submitting: boolean;
  onSubmit: (values: { name: string; geometry: TalhaoGeometry }) => void;
}

export function TalhaoForm({ farmId, submitting, onSubmit }: TalhaoFormProps) {
  const [geometry, setGeometry] = useState<TalhaoGeometry | null>(null);
  const [importError, setImportError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TalhaoFormValues>({
    resolver: zodResolver(talhaoFormSchema),
    defaultValues: { name: "" },
  });

  const previewAreaLabel = geometry ? "Polígono pronto — área oficial será calculada ao salvar." : null;

  async function handleFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) {
      return;
    }
    setImportError(null);
    try {
      const importedGeometry = await extractGeometryFromGeoJsonFile(file);
      setGeometry(importedGeometry);
    } catch (error) {
      if (error instanceof GeoJsonImportError) {
        setImportError(error.message);
      } else {
        setImportError("Nao foi possivel importar o arquivo.");
      }
    }
  }

  function submit(values: TalhaoFormValues) {
    if (!geometry) {
      return;
    }
    onSubmit({ name: values.name, geometry });
  }

  return (
    <form onSubmit={handleSubmit(submit)} aria-label="Formulário de talhão">
      <label htmlFor="talhao-name">Nome do talhão</label>
      <input id="talhao-name" {...register("name")} aria-describedby="talhao-name-error" />
      {errors.name && (
        <p id="talhao-name-error" role="alert">
          {errors.name.message}
        </p>
      )}

      <label htmlFor="talhao-geojson-input">Importar arquivo GeoJSON</label>
      <input
        id="talhao-geojson-input"
        type="file"
        accept=".geojson,application/geo+json"
        onChange={(event) => void handleFileChange(event)}
      />
      {importError && <p role="alert">{importError}</p>}
      {previewAreaLabel && <p role="status">{previewAreaLabel}</p>}

      <MapAdapter
        existingGeometries={geometry ? [{ id: "preview", name: "Prévia", geometry }] : []}
        onDraw={(drawnGeometry) => {
          setImportError(null);
          setGeometry(drawnGeometry);
        }}
        tenantKey={farmId}
      />

      <button type="submit" disabled={!geometry || submitting} aria-busy={submitting}>
        Salvar talhão
      </button>
    </form>
  );
}

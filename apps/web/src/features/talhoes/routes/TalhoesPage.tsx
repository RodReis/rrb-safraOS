import { useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

import { DataTable } from "@safraos/frontend/components/DataTable";
import { MapAdapter } from "../../../components/map/MapAdapter";
import { ConfirmDialog } from "../../../components/ui/ConfirmDialog";
import { Skeleton } from "../../../components/ui/Skeleton";
import { $api } from "../../../lib/apiClient";
import { buildTalhaoColumns } from "../components/TalhaoColumns";
import { TalhaoForm } from "../components/TalhaoForm";

export function TalhoesPage() {
  const { farmId } = useParams<{ farmId: string }>();
  const [showForm, setShowForm] = useState(false);
  const [talhaoToArchive, setTalhaoToArchive] = useState<string | null>(null);

  const talhoesQuery = $api.useQuery("get", "/v1/talhoes", {
    params: { query: { farmId: farmId ?? "" } },
  });

  const createMutation = $api.useMutation("post", "/v1/talhoes", {
    onSuccess: () => {
      toast.success("Talhão criado com sucesso.");
      setShowForm(false);
      void talhoesQuery.refetch();
    },
    onError: () => {
      toast.error("Não foi possível criar o talhão.");
    },
  });

  const archiveMutation = $api.useMutation("post", "/v1/talhoes/{talhao_id}/archive", {
    onSuccess: () => {
      toast.success("Talhão arquivado.");
      setTalhaoToArchive(null);
      void talhoesQuery.refetch();
    },
    onError: () => {
      toast.error("Não foi possível arquivar o talhão.");
    },
  });

  if (!farmId) {
    return null;
  }

  if (talhoesQuery.isLoading) {
    return (
      <section aria-labelledby="talhoes-heading">
        <h1 id="talhoes-heading">Talhões</h1>
        <Skeleton aria-label="Carregando talhões" />
        <Skeleton aria-label="Carregando talhões" />
        <Skeleton aria-label="Carregando talhões" />
      </section>
    );
  }

  if (talhoesQuery.error) {
    return (
      <div role="alert" className="notice">
        <p>Erro ao carregar talhões.</p>
        <button type="button" onClick={() => talhoesQuery.refetch()}>
          Tentar novamente
        </button>
      </div>
    );
  }

  const talhoes = talhoesQuery.data?.items ?? [];
  const talhaoBeingArchived = talhoes.find((talhao) => talhao.id === talhaoToArchive);

  return (
    <section aria-labelledby="talhoes-heading">
      <div className="section-heading">
        <h1 id="talhoes-heading">Talhões</h1>
        <button type="button" onClick={() => setShowForm(true)}>
          Novo talhão
        </button>
      </div>

      {showForm && (
        <TalhaoForm
          farmId={farmId}
          submitting={createMutation.isPending}
          onSubmit={(values) =>
            createMutation.mutate({
              body: { farmId, name: values.name, geometry: values.geometry as unknown as Record<string, unknown> },
            })
          }
        />
      )}

      <div className="talhoes-split-view">
        <div className="talhoes-list">
          {talhoes.length === 0 ? (
            <p role="status">Nenhum talhão cadastrado.</p>
          ) : (
            <DataTable
              columns={buildTalhaoColumns((id) => setTalhaoToArchive(id))}
              data={talhoes}
              emptyMessage="Nenhum talhão cadastrado."
              getRowId={(talhao) => talhao.id}
            />
          )}
        </div>

        <div className="talhoes-map">
          {/*
            ponytail: existingGeometries fixo em [] — GET /v1/talhoes ainda não expõe `geometry`
            (só areaHa). Decisão registrada no brief da Task 9: resolvido na Task 10, que adiciona
            ST_AsGeoJSON(geom)::json AS geometry no repository e propaga até TalhaoResponse/aqui.
          */}
          <MapAdapter existingGeometries={[]} tenantKey={farmId} />
        </div>
      </div>

      <ConfirmDialog
        open={talhaoToArchive !== null}
        title="Arquivar talhão?"
        description={
          talhaoBeingArchived
            ? `O talhão "${talhaoBeingArchived.name}" será arquivado e deixará de aparecer na lista ativa.`
            : "O talhão será arquivado e deixará de aparecer na lista ativa."
        }
        confirmLabel="Confirmar arquivamento"
        confirming={archiveMutation.isPending}
        onCancel={() => setTalhaoToArchive(null)}
        onConfirm={() => {
          if (talhaoToArchive) {
            archiveMutation.mutate({ params: { path: { talhao_id: talhaoToArchive } } });
          }
        }}
      />
    </section>
  );
}

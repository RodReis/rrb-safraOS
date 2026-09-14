import { useState } from "react";
import { toast } from "sonner";

import { DataTable } from "@safraos/frontend/components/DataTable";
import { ConfirmDialog } from "../../../components/ui/ConfirmDialog";
import { Skeleton } from "../../../components/ui/Skeleton";
import { $api } from "../../../lib/apiClient";
import { buildFarmColumns } from "../components/FarmColumns";
import { FarmForm } from "../components/FarmForm";
import type { FarmFormValues } from "../schemas/farmSchema";

export function FarmsPage() {
  const [showForm, setShowForm] = useState(false);
  const [farmToArchive, setFarmToArchive] = useState<string | null>(null);

  const farmsQuery = $api.useQuery("get", "/v1/farms", {});
  const municipiosQuery = $api.useQuery("get", "/v1/municipios", {});

  const createMutation = $api.useMutation("post", "/v1/farms", {
    onSuccess: () => {
      toast.success("Fazenda criada com sucesso.");
      setShowForm(false);
      void farmsQuery.refetch();
    },
    onError: () => {
      toast.error("Nao foi possivel criar a fazenda.");
    },
  });

  const archiveMutation = $api.useMutation("post", "/v1/farms/{farm_id}/archive", {
    onSuccess: () => {
      toast.success("Fazenda arquivada.");
      setFarmToArchive(null);
      void farmsQuery.refetch();
    },
    onError: () => {
      toast.error("Nao foi possivel arquivar a fazenda.");
    },
  });

  if (farmsQuery.isLoading) {
    return (
      <section aria-labelledby="farms-heading">
        <h1 id="farms-heading">Fazendas</h1>
        <Skeleton aria-label="Carregando fazendas" />
        <Skeleton aria-label="Carregando fazendas" />
        <Skeleton aria-label="Carregando fazendas" />
      </section>
    );
  }

  if (farmsQuery.error) {
    return (
      <div role="alert" className="notice">
        <p>Erro ao carregar fazendas.</p>
        <button type="button" onClick={() => farmsQuery.refetch()}>
          Tentar novamente
        </button>
      </div>
    );
  }

  const farms = farmsQuery.data?.items ?? [];
  const farmBeingArchived = farms.find((farm) => farm.id === farmToArchive);

  return (
    <section aria-labelledby="farms-heading">
      <div className="section-heading">
        <h1 id="farms-heading">Fazendas</h1>
        <button type="button" onClick={() => setShowForm(true)}>
          Nova fazenda
        </button>
      </div>

      {showForm && (
        <FarmForm
          municipios={(municipiosQuery.data?.items ?? []).map((m) => ({
            ibgeCode: m.ibgeCode,
            name: m.name,
            uf: m.uf,
          }))}
          submitting={createMutation.isPending}
          onSubmit={(values: FarmFormValues) =>
            createMutation.mutate({
              body: { name: values.name, uf: values.uf, municipioIbgeCode: values.municipioIbgeCode },
            })
          }
        />
      )}

      {farms.length === 0 ? (
        <p role="status">Nenhuma fazenda cadastrada.</p>
      ) : (
        <DataTable
          columns={buildFarmColumns((id) => setFarmToArchive(id))}
          data={farms}
          emptyMessage="Nenhuma fazenda cadastrada."
          getRowId={(farm) => farm.id}
        />
      )}

      <ConfirmDialog
        open={farmToArchive !== null}
        title="Arquivar fazenda?"
        description={
          farmBeingArchived
            ? `A fazenda "${farmBeingArchived.name}" sera arquivada e deixara de aparecer na lista ativa.`
            : "A fazenda sera arquivada e deixara de aparecer na lista ativa."
        }
        confirmLabel="Confirmar arquivamento"
        confirming={archiveMutation.isPending}
        onCancel={() => setFarmToArchive(null)}
        onConfirm={() => {
          if (farmToArchive) {
            archiveMutation.mutate({ params: { path: { farm_id: farmToArchive } } });
          }
        }}
      />
    </section>
  );
}

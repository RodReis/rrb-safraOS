import type { ColumnDef } from "@tanstack/react-table";

export interface FarmRow {
  id: string;
  name: string;
  uf: string;
  municipioName: string;
  archivedAt: string | null;
}

export function buildFarmColumns(onArchive: (id: string) => void): ColumnDef<FarmRow, unknown>[] {
  return [
    { accessorKey: "name", header: "Nome" },
    { accessorKey: "uf", header: "UF" },
    { accessorKey: "municipioName", header: "Municipio" },
    {
      id: "status",
      header: "Status",
      cell: ({ row }) => (row.original.archivedAt ? "Arquivada" : "Ativa"),
    },
    {
      id: "actions",
      header: "Acoes",
      cell: ({ row }) =>
        row.original.archivedAt ? null : (
          <button
            type="button"
            className="secondary-action"
            onClick={() => onArchive(row.original.id)}
          >
            Arquivar
          </button>
        ),
    },
  ];
}

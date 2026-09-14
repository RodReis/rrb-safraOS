import type { ColumnDef } from "@tanstack/react-table";

export interface TalhaoRow {
  id: string;
  name: string;
  areaHa: string;
  archivedAt: string | null;
}

export function buildTalhaoColumns(onArchive: (id: string) => void): ColumnDef<TalhaoRow, unknown>[] {
  return [
    { accessorKey: "name", header: "Nome" },
    {
      accessorKey: "areaHa",
      header: "Área (ha)",
      cell: ({ row }) => <span className="tabular-nums">{row.original.areaHa}</span>,
    },
    {
      id: "status",
      header: "Status",
      cell: ({ row }) => (row.original.archivedAt ? "Arquivado" : "Ativo"),
    },
    {
      id: "actions",
      header: "Ações",
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

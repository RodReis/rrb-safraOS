import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "./DataTable";

interface Row {
  id: string;
  name: string;
}

const columns: ColumnDef<Row, unknown>[] = [
  { accessorKey: "name", header: "Nome" },
];

describe("DataTable", () => {
  it("renderiza linhas de dados", () => {
    render(
      <DataTable
        columns={columns}
        data={[{ id: "1", name: "Fazenda A" }]}
        emptyMessage="Nenhuma fazenda."
        getRowId={(row) => row.id}
      />
    );

    expect(screen.getByText("Fazenda A")).toBeInTheDocument();
  });

  it("mostra mensagem de vazio quando nao ha dados", () => {
    render(<DataTable columns={columns} data={[]} emptyMessage="Nenhuma fazenda." />);

    expect(screen.getByText("Nenhuma fazenda.")).toBeInTheDocument();
  });

  it("chama onRowClick ao clicar na linha", () => {
    const onRowClick = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={[{ id: "1", name: "Fazenda A" }]}
        emptyMessage="Nenhuma fazenda."
        getRowId={(row) => row.id}
        onRowClick={onRowClick}
      />
    );

    screen.getByText("Fazenda A").closest("tr")?.click();
    expect(onRowClick).toHaveBeenCalledWith({ id: "1", name: "Fazenda A" });
  });
});

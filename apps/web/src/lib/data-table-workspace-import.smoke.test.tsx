// Smoke test: confirma que apps/web resolve @safraos/frontend via npm workspace,
// tanto em runtime (vitest) quanto em typecheck (tsc), usando o subpath export
// "./components/DataTable" declarado em packages/frontend/package.json.
// A Task 10 importa DataTable exatamente por este path.
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@safraos/frontend/components/DataTable";

interface Row {
  id: string;
  name: string;
}

const columns: ColumnDef<Row, unknown>[] = [{ accessorKey: "name", header: "Nome" }];

describe("workspace import @safraos/frontend/components/DataTable", () => {
  it("resolve e renderiza via import do workspace", () => {
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
});

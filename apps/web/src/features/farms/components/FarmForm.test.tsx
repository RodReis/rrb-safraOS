import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { FarmForm } from "./FarmForm";

const municipios = [{ ibgeCode: "5208707", name: "Goiania", uf: "GO" }];

describe("FarmForm", () => {
  it("envia dados validos", async () => {
    const onSubmit = vi.fn();
    render(<FarmForm municipios={municipios} onSubmit={onSubmit} submitting={false} />);

    fireEvent.change(screen.getByLabelText(/nome/i), { target: { value: "Fazenda Boa Vista" } });
    fireEvent.change(screen.getByLabelText(/uf/i), { target: { value: "GO" } });
    fireEvent.change(screen.getByLabelText(/munic[ií]pio/i), { target: { value: "5208707" } });
    fireEvent.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: "Fazenda Boa Vista",
        uf: "GO",
        municipioIbgeCode: "5208707",
      });
    });
  });

  it("mostra erro de validacao e preserva o valor digitado", async () => {
    const onSubmit = vi.fn();
    render(<FarmForm municipios={municipios} onSubmit={onSubmit} submitting={false} />);

    fireEvent.change(screen.getByLabelText(/nome/i), { target: { value: "A" } });
    fireEvent.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(screen.getByText(/ao menos 2 caracteres/i)).toBeInTheDocument();
    });
    expect(screen.getByLabelText(/nome/i)).toHaveValue("A");
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("desabilita o botao salvar durante submitting", () => {
    render(<FarmForm municipios={municipios} onSubmit={vi.fn()} submitting />);

    expect(screen.getByRole("button", { name: /salvar/i })).toBeDisabled();
  });
});

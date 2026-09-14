import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { TalhaoForm } from "./TalhaoForm";

describe("TalhaoForm", () => {
  it("disables submit until a geometry has been provided", () => {
    render(<TalhaoForm farmId="farm-1" submitting={false} onSubmit={vi.fn()} />);

    expect(screen.getByRole("button", { name: /salvar talhão/i })).toBeDisabled();
  });

  it("enables submit and calls onSubmit after importing a valid GeoJSON file", async () => {
    const onSubmit = vi.fn();
    render(<TalhaoForm farmId="farm-1" submitting={false} onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText(/nome do talhão/i), { target: { value: "Talhao Norte" } });

    const file = new File(
      [JSON.stringify({ type: "Polygon", coordinates: [[[0, 0], [0, 1], [1, 1], [0, 0]]] })],
      "talhao.geojson",
      { type: "application/geo+json" },
    );
    const input = screen.getByLabelText(/importar arquivo geojson/i);
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => expect(screen.getByRole("button", { name: /salvar talhão/i })).toBeEnabled());

    fireEvent.click(screen.getByRole("button", { name: /salvar talhão/i }));

    await waitFor(() =>
      expect(onSubmit).toHaveBeenCalledWith({
        name: "Talhao Norte",
        geometry: { type: "Polygon", coordinates: [[[0, 0], [0, 1], [1, 1], [0, 0]]] },
      }),
    );
  });

  it("shows an error message when the imported file is invalid", async () => {
    render(<TalhaoForm farmId="farm-1" submitting={false} onSubmit={vi.fn()} />);

    const file = new File([JSON.stringify({ type: "Point", coordinates: [0, 0] })], "talhao.geojson", {
      type: "application/geo+json",
    });
    const input = screen.getByLabelText(/importar arquivo geojson/i);
    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent(/polygon ou multipolygon/i));
  });
});

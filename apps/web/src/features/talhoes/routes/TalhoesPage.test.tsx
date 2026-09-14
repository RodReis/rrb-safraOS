import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../../lib/apiClient", async () => {
  const actual = await vi.importActual<typeof import("../../../lib/apiClient")>("../../../lib/apiClient");
  return {
    ...actual,
    $api: {
      useQuery: vi.fn(),
      useMutation: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
    },
  };
});

import { $api } from "../../../lib/apiClient";
import { TalhoesPage } from "./TalhoesPage";

function renderPage() {
  const queryClient = new QueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/fazendas/farm-1/talhoes"]}>
        <Routes>
          <Route path="/fazendas/:farmId/talhoes" element={<TalhoesPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("TalhoesPage", () => {
  beforeEach(() => {
    vi.mocked($api.useQuery).mockReturnValue({
      isLoading: false,
      error: null,
      data: { items: [] },
      refetch: vi.fn(),
    } as never);
  });

  it("shows empty state when there are no talhões", async () => {
    renderPage();

    await waitFor(() => expect(screen.getByText(/nenhum talhão cadastrado/i)).toBeInTheDocument());
  });

  it("shows loading skeleton while fetching", () => {
    vi.mocked($api.useQuery).mockReturnValue({
      isLoading: true,
      error: null,
      data: undefined,
      refetch: vi.fn(),
    } as never);

    renderPage();

    expect(screen.getAllByLabelText(/carregando talhões/i).length).toBeGreaterThan(0);
  });

  it("shows error state with retry when the query fails", () => {
    vi.mocked($api.useQuery).mockReturnValue({
      isLoading: false,
      error: new Error("network"),
      data: undefined,
      refetch: vi.fn(),
    } as never);

    renderPage();

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /tentar novamente/i })).toBeInTheDocument();
  });
});

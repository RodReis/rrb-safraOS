import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { $api } from "../../../lib/apiClient";
import { FarmsPage } from "./FarmsPage";

function renderWithClient(children: React.ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{children}</QueryClientProvider>);
}

function mockIdleMutation() {
  return {
    mutate: vi.fn(),
    isPending: false,
  } as never;
}

describe("FarmsPage", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn($api, "useMutation").mockReturnValue(mockIdleMutation());
  });

  it("mostra skeleton de loading e depois lista de fazendas", async () => {
    vi.spyOn($api, "useQuery").mockImplementation((_method, path) => {
      if (path === "/v1/farms") {
        return {
          data: {
            items: [
              { id: "1", name: "Fazenda A", uf: "GO", municipioName: "Goiania", archivedAt: null },
            ],
          },
          isLoading: false,
          error: null,
          refetch: vi.fn(),
        } as never;
      }
      return { data: { items: [] }, isLoading: false, error: null, refetch: vi.fn() } as never;
    });

    renderWithClient(<FarmsPage />);

    await waitFor(() => {
      expect(screen.getByText("Fazenda A")).toBeInTheDocument();
    });
  });

  it("mostra estado vazio quando nao ha fazendas", async () => {
    vi.spyOn($api, "useQuery").mockReturnValue({
      data: { items: [] },
      isLoading: false,
      error: null,
      refetch: vi.fn(),
    } as never);

    renderWithClient(<FarmsPage />);

    await waitFor(() => {
      expect(screen.getByText(/nenhuma fazenda/i)).toBeInTheDocument();
    });
  });

  it("mostra estado de erro com retry", async () => {
    vi.spyOn($api, "useQuery").mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error("falha"),
      refetch: vi.fn(),
    } as never);

    renderWithClient(<FarmsPage />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /tentar novamente/i })).toBeInTheDocument();
    });
  });
});

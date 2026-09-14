import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MapAdapter } from "./MapAdapter";

describe("MapAdapter", () => {
  it("renders the map container", () => {
    render(<MapAdapter existingGeometries={[]} tenantKey="org-1" />);

    expect(screen.getByRole("region", { name: /mapa de talhões/i })).toBeInTheDocument();
  });

  it("remounts when tenantKey changes (no stale layers across tenants)", () => {
    const { rerender } = render(<MapAdapter existingGeometries={[]} tenantKey="org-1" />);
    const firstContainer = screen.getByRole("region", { name: /mapa de talhões/i });

    rerender(<MapAdapter existingGeometries={[]} tenantKey="org-2" />);
    const secondContainer = screen.getByRole("region", { name: /mapa de talhões/i });

    // Elementos DOM diferentes: React desmontou e remontou a arvore do mapa.
    expect(firstContainer).not.toBe(secondContainer);
  });
});

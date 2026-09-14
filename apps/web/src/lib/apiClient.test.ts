import { describe, expect, it } from "vitest";

import { $api, queryClient } from "./apiClient";

describe("apiClient", () => {
  it("expoe useQuery e useMutation tipados", () => {
    expect(typeof $api.useQuery).toBe("function");
    expect(typeof $api.useMutation).toBe("function");
  });

  it("expoe uma instancia de QueryClient compartilhada", () => {
    expect(queryClient.getQueryCache).toBeDefined();
  });
});

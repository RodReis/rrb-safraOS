import { describe, expect, it } from "vitest";

import { farmFormSchema } from "./farmSchema";

describe("farmFormSchema", () => {
  it("aceita dados validos", () => {
    const result = farmFormSchema.safeParse({
      name: "Fazenda Boa Vista",
      uf: "GO",
      municipioIbgeCode: "5208707",
    });

    expect(result.success).toBe(true);
  });

  it("rejeita nome vazio", () => {
    const result = farmFormSchema.safeParse({ name: "", uf: "GO", municipioIbgeCode: "5208707" });

    expect(result.success).toBe(false);
  });

  it("rejeita UF com mais de 2 caracteres", () => {
    const result = farmFormSchema.safeParse({
      name: "Fazenda X",
      uf: "GOI",
      municipioIbgeCode: "5208707",
    });

    expect(result.success).toBe(false);
  });

  it("rejeita codigo IBGE fora do formato de 7 digitos", () => {
    const result = farmFormSchema.safeParse({
      name: "Fazenda X",
      uf: "GO",
      municipioIbgeCode: "123",
    });

    expect(result.success).toBe(false);
  });
});

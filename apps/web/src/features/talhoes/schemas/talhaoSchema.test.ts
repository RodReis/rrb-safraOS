import { describe, expect, it } from "vitest";

import { talhaoFormSchema } from "./talhaoSchema";

describe("talhaoFormSchema", () => {
  it("accepts a valid name", () => {
    const result = talhaoFormSchema.safeParse({ name: "Talhao Norte" });
    expect(result.success).toBe(true);
  });

  it("rejects a name shorter than 2 characters", () => {
    const result = talhaoFormSchema.safeParse({ name: "A" });
    expect(result.success).toBe(false);
  });
});

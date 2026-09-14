import { z } from "zod";

export const farmFormSchema = z.object({
  name: z.string().trim().min(2, "Nome deve ter ao menos 2 caracteres."),
  uf: z.string().length(2, "UF deve ter 2 letras."),
  municipioIbgeCode: z.string().regex(/^\d{7}$/, "Codigo IBGE deve ter 7 digitos."),
});

export type FarmFormValues = z.infer<typeof farmFormSchema>;

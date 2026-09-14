import { z } from "zod";

export const talhaoFormSchema = z.object({
  name: z.string().trim().min(2, "Nome deve ter ao menos 2 caracteres."),
});

export type TalhaoFormValues = z.infer<typeof talhaoFormSchema>;

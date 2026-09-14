import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";

import { farmFormSchema, type FarmFormValues } from "../schemas/farmSchema";

export interface FarmFormProps {
  defaultValues?: Partial<FarmFormValues>;
  onSubmit: (values: FarmFormValues) => void;
  submitting: boolean;
  municipios: { ibgeCode: string; name: string; uf: string }[];
}

export function FarmForm({ defaultValues, onSubmit, submitting, municipios }: FarmFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FarmFormValues>({
    resolver: zodResolver(farmFormSchema),
    defaultValues: {
      name: defaultValues?.name ?? "",
      uf: defaultValues?.uf ?? "",
      municipioIbgeCode: defaultValues?.municipioIbgeCode ?? "",
    },
  });

  return (
    <form onSubmit={handleSubmit((values) => onSubmit(values))} noValidate>
      <div>
        <label htmlFor="farm-name">Nome</label>
        <input id="farm-name" {...register("name")} aria-describedby="farm-name-error" />
        {errors.name && (
          <p id="farm-name-error" role="alert">
            {errors.name.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="farm-uf">UF</label>
        <input id="farm-uf" {...register("uf")} aria-describedby="farm-uf-error" maxLength={2} />
        {errors.uf && (
          <p id="farm-uf-error" role="alert">
            {errors.uf.message}
          </p>
        )}
      </div>

      <div>
        <label htmlFor="farm-municipio">Municipio</label>
        <select id="farm-municipio" {...register("municipioIbgeCode")} aria-describedby="farm-municipio-error">
          <option value="">Selecione</option>
          {municipios.map((m) => (
            <option key={m.ibgeCode} value={m.ibgeCode}>
              {m.name} ({m.uf})
            </option>
          ))}
        </select>
        {errors.municipioIbgeCode && (
          <p id="farm-municipio-error" role="alert">
            {errors.municipioIbgeCode.message}
          </p>
        )}
      </div>

      <button type="submit" disabled={submitting} aria-busy={submitting}>
        Salvar
      </button>
    </form>
  );
}

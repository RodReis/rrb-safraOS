import { QueryClient } from "@tanstack/react-query";
import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";

import type { paths } from "./api-types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:5183";

const fetchClient = createFetchClient<paths>({
  baseUrl: API_BASE_URL,
  credentials: "include",
});

export const $api = createClient(fetchClient);

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

import { useQuery } from "@tanstack/react-query";
import { customersApi } from "@/lib/api";
import type { CustomerFilters } from "@/types";

export function useCustomers(filters: CustomerFilters = {}) {
  return useQuery({
    queryKey: ["customers", filters],
    queryFn: async () => {
      const { data } = await customersApi.list(filters);
      return data;
    },
    staleTime: 30_000,
  });
}
import { useQuery } from "@tanstack/react-query";
import { customersApi } from "@/lib/api";

export function useCustomer(id: string | undefined) {
  return useQuery({
    queryKey: ["customer", id],
    queryFn: async () => {
      if (!id) throw new Error("Missing customer id");
      const { data } = await customersApi.get(id);
      return data;
    },
    enabled: Boolean(id),
    staleTime: 30_000,
  });
}
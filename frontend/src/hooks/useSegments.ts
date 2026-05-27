import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { segmentsApi } from "@/lib/api";
import type { SegmentCreate } from "@/types";

export function useSegments() {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["segments"],
    queryFn: async () => {
      const { data } = await segmentsApi.list();
      return data;
    },
    staleTime: 60_000,
  });

  const createMutation = useMutation({
    mutationFn: (payload: SegmentCreate) => segmentsApi.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["segments"] });
    },
  });

  return { ...query, createSegment: createMutation };
}
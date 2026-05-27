import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { mlApi } from "@/lib/api";
import type { MLTrainRequest } from "@/types";

export function useML() {
  const queryClient = useQueryClient();

  const modelsQuery = useQuery({
    queryKey: ["ml", "models"],
    queryFn: async () => {
      const { data } = await mlApi.models();
      return data;
    },
    staleTime: 30_000,
  });

  const trainMutation = useMutation({
    mutationFn: (payload: MLTrainRequest) => mlApi.train(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["ml", "models"] });
    },
  });

  return { ...modelsQuery, trainModel: trainMutation };
}
import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api";

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: ["analytics", "overview"],
    queryFn: async () => {
      const { data } = await analyticsApi.overview();
      return data;
    },
    staleTime: 60_000,
  });
}

export function useRevenueAnalytics(groupBy = "month") {
  return useQuery({
    queryKey: ["analytics", "revenue", groupBy],
    queryFn: async () => {
      const { data } = await analyticsApi.revenue(groupBy);
      return data;
    },
    staleTime: 60_000,
  });
}

export function useChurnAnalytics() {
  return useQuery({
    queryKey: ["analytics", "churn"],
    queryFn: async () => {
      const { data } = await analyticsApi.churn();
      return data;
    },
    staleTime: 60_000,
  });
}
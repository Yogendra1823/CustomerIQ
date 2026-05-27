import { useState } from "react";
import { ChurnTrendChart } from "@/components/charts/ChurnTrendChart";
import { RevenueChart } from "@/components/charts/RevenueChart";
import { SegmentPieChart } from "@/components/charts/SegmentPieChart";
import { KpiCard } from "@/components/KpiCard";
import { CardSkeleton } from "@/components/LoadingSkeleton";
import { PageHeader } from "@/components/layout/PageHeader";
import {
  useAnalyticsOverview,
  useChurnAnalytics,
  useRevenueAnalytics,
} from "@/hooks/useAnalytics";
import { useSegments } from "@/hooks/useSegments";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";
import { DollarSign, Users, TrendingDown, Layers } from "lucide-react";

export function AnalyticsPage() {
  const [groupBy, setGroupBy] = useState("month");
  const { data: overview, isLoading } = useAnalyticsOverview();
  const { data: revenue } = useRevenueAnalytics(groupBy);
  const { data: churn } = useChurnAnalytics();
  const { data: segments = [] } = useSegments();

  return (
    <div>
      <PageHeader
        title="Analytics"
        description="Revenue, churn, and segment performance insights"
        actions={
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="h-10 rounded-lg border border-slate-700 bg-slate-900 px-3 text-sm text-slate-200"
          >
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
        }
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
        ) : (
          <>
            <KpiCard
              label="Customers"
              value={formatNumber(overview?.total_customers)}
              icon={Users}
            />
            <KpiCard
              label="Revenue"
              value={formatCurrency(overview?.total_revenue)}
              icon={DollarSign}
            />
            <KpiCard
              label="Avg CLV"
              value={formatCurrency(overview?.avg_clv)}
              icon={Layers}
            />
            <KpiCard
              label="Churn"
              value={formatPercent(overview?.churn_rate)}
              icon={TrendingDown}
              accent="text-red-400"
            />
          </>
        )}
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">Revenue</h3>
          <RevenueChart data={revenue?.data ?? []} />
        </div>
        <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">Segments</h3>
          <SegmentPieChart segments={segments} />
        </div>
      </div>
      <div className="mt-6 rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
        <h3 className="mb-4 text-sm font-semibold text-slate-300">Churn analysis</h3>
        <ChurnTrendChart data={churn?.data ?? []} />
      </div>
      {overview?.regional_breakdown?.length ? (
        <div className="mt-6 rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">Regional breakdown</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-slate-500">
                <th className="pb-2">Region</th>
                <th className="pb-2">Customers</th>
                <th className="pb-2 text-right">Revenue</th>
              </tr>
            </thead>
            <tbody>
              {overview.regional_breakdown.map((r) => (
                <tr key={r.region} className="border-t border-slate-800">
                  <td className="py-2 text-slate-200">{r.region}</td>
                  <td className="py-2 text-slate-400">{r.customers}</td>
                  <td className="py-2 text-right text-slate-100">
                    {formatCurrency(r.revenue)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
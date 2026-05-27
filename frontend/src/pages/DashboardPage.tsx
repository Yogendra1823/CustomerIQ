import { DollarSign, Layers, TrendingUp, Users } from "lucide-react";
import { ChurnTrendChart } from "@/components/charts/ChurnTrendChart";
import { RevenueChart } from "@/components/charts/RevenueChart";
import { SegmentPieChart } from "@/components/charts/SegmentPieChart";
import { KpiCard } from "@/components/KpiCard";
import { CardSkeleton } from "@/components/LoadingSkeleton";
import { PageHeader } from "@/components/layout/PageHeader";
import { useDashboard } from "@/hooks/useDashboard";
import { useSegments } from "@/hooks/useSegments";
import { useRevenueAnalytics, useChurnAnalytics } from "@/hooks/useAnalytics";
import { formatCurrency, formatNumber, formatPercent } from "@/lib/utils";

export function DashboardPage() {
  const { data: stats, isLoading } = useDashboard();
  const { data: segments = [] } = useSegments();
  const { data: revenue } = useRevenueAnalytics();
  const { data: churn } = useChurnAnalytics();

  return (
    <div>
      <PageHeader
        title="Dashboard"
        description="Real-time overview of customer health and revenue"
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isLoading ? (
          Array.from({ length: 4 }).map((_, i) => <CardSkeleton key={i} />)
        ) : (
          <>
            <KpiCard
              label="Total customers"
              value={formatNumber(stats?.total_customers)}
              change={stats?.revenue_growth_pct}
              icon={Users}
            />
            <KpiCard
              label="Total revenue"
              value={formatCurrency(stats?.total_revenue)}
              change={stats?.revenue_growth_pct}
              icon={DollarSign}
            />
            <KpiCard
              label="Avg CLV"
              value={formatCurrency(stats?.avg_clv)}
              icon={TrendingUp}
            />
            <KpiCard
              label="Churn rate"
              value={formatPercent(stats?.churn_rate)}
              change={stats?.churn_rate != null ? -2.1 : undefined}
              icon={Layers}
              accent="text-amber-400"
            />
          </>
        )}
      </div>
      <div className="mt-6 grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">Revenue trend</h3>
          <RevenueChart data={revenue?.data ?? []} />
        </div>
        <div className="rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
          <h3 className="mb-4 text-sm font-semibold text-slate-300">Segment distribution</h3>
          <SegmentPieChart segments={segments} />
        </div>
      </div>
      <div className="mt-6 rounded-xl border border-slate-700/60 bg-slate-900/50 p-5">
        <h3 className="mb-4 text-sm font-semibold text-slate-300">Churn trend</h3>
        <ChurnTrendChart data={churn?.data ?? []} />
      </div>
    </div>
  );
}
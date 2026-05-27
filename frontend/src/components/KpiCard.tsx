import type { LucideIcon } from "lucide-react";
import { TrendingDown, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";

interface KpiCardProps {
  label: string;
  value: string;
  change?: number;
  icon: LucideIcon;
  accent?: string;
}

export function KpiCard({ label, value, change, icon: Icon, accent = "text-cyan-400" }: KpiCardProps) {
  const positive = change != null && change >= 0;

  return (
    <div className="rounded-xl border border-slate-700/60 bg-gradient-to-br from-slate-900 to-slate-950 p-5 shadow-lg shadow-black/20">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
          <p className="mt-2 text-2xl font-bold text-slate-50">{value}</p>
          {change != null ? (
            <div
              className={cn(
                "mt-2 flex items-center gap-1 text-xs font-medium",
                positive ? "text-emerald-400" : "text-red-400",
              )}
            >
              {positive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
              {positive ? "+" : ""}
              {change.toFixed(1)}% vs last period
            </div>
          ) : null}
        </div>
        <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg bg-slate-800", accent)}>
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
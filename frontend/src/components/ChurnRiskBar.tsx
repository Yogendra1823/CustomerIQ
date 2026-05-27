import { cn, churnRiskLevel, formatPercent } from "@/lib/utils";

interface ChurnRiskBarProps {
  probability: number | null;
  showLabel?: boolean;
}

const riskColors = {
  low: "bg-emerald-500",
  medium: "bg-amber-500",
  high: "bg-red-500",
};

export function ChurnRiskBar({ probability, showLabel = true }: ChurnRiskBarProps) {
  const level = churnRiskLevel(probability);
  const pct = probability == null ? 0 : probability <= 1 ? probability * 100 : probability;

  return (
    <div className="space-y-1">
      {showLabel ? (
        <div className="flex justify-between text-xs">
          <span className="capitalize text-slate-400">{level} risk</span>
          <span className="text-slate-300">{formatPercent(probability)}</span>
        </div>
      ) : null}
      <div className="h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className={cn("h-full rounded-full transition-all", riskColors[level])}
          style={{ width: `${Math.min(100, Math.max(0, pct))}%` }}
        />
      </div>
    </div>
  );
}
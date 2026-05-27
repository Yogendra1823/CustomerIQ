import { Search, X } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";

export interface FilterOption {
  label: string;
  value: string;
}

interface FilterPanelProps {
  search: string;
  onSearchChange: (value: string) => void;
  region?: string;
  onRegionChange?: (value: string) => void;
  valueTier?: string;
  onValueTierChange?: (value: string) => void;
  regions?: FilterOption[];
  valueTiers?: FilterOption[];
  onClear?: () => void;
  className?: string;
}

export function FilterPanel({
  search,
  onSearchChange,
  region,
  onRegionChange,
  valueTier,
  onValueTierChange,
  regions = [],
  valueTiers = [],
  onClear,
  className,
}: FilterPanelProps) {
  const hasFilters = Boolean(search || region || valueTier);

  return (
    <div
      className={cn(
        "flex flex-wrap items-center gap-3 rounded-xl border border-slate-700/60 bg-slate-900/60 p-4",
        className,
      )}
    >
      <div className="relative min-w-[200px] flex-1">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          type="search"
          placeholder="Search by customer ID..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="h-10 w-full rounded-lg border border-slate-700 bg-slate-950 pl-10 pr-3 text-sm text-slate-100 placeholder:text-slate-500 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
        />
      </div>
      {onRegionChange ? (
        <select
          value={region ?? ""}
          onChange={(e) => onRegionChange(e.target.value)}
          className="h-10 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-200 focus:border-cyan-500 focus:outline-none"
        >
          <option value="">All regions</option>
          {regions.map((r) => (
            <option key={r.value} value={r.value}>
              {r.label}
            </option>
          ))}
        </select>
      ) : null}
      {onValueTierChange ? (
        <select
          value={valueTier ?? ""}
          onChange={(e) => onValueTierChange(e.target.value)}
          className="h-10 rounded-lg border border-slate-700 bg-slate-950 px-3 text-sm text-slate-200 focus:border-cyan-500 focus:outline-none"
        >
          <option value="">All tiers</option>
          {valueTiers.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      ) : null}
      {hasFilters && onClear ? (
        <Button variant="ghost" size="sm" onClick={onClear}>
          <X className="h-4 w-4" />
          Clear
        </Button>
      ) : null}
    </div>
  );
}
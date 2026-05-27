import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { RevenueDataPoint } from "@/types";
import { formatCurrency } from "@/lib/utils";

interface RevenueChartProps {
  data: RevenueDataPoint[];
}

export function RevenueChart({ data }: RevenueChartProps) {
  const chartData = data.length
    ? data
    : [
        { period: "Jan", revenue: 120000 },
        { period: "Feb", revenue: 145000 },
        { period: "Mar", revenue: 132000 },
        { period: "Apr", revenue: 168000 },
        { period: "May", revenue: 190000 },
        { period: "Jun", revenue: 210000 },
      ];

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22d3ee" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis dataKey="period" stroke="#64748b" fontSize={12} tickLine={false} />
          <YAxis
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            tickFormatter={(v) => `₹${(Number(v) / 1000).toFixed(0)}k`}
          />
          <Tooltip
            contentStyle={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: 8,
            }}
            formatter={(value) => [formatCurrency(Number(value)), "Revenue"]}
          />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="#22d3ee"
            strokeWidth={2}
            fill="url(#revenueGrad)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
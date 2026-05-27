import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ChurnDataPoint } from "@/types";
import { formatPercent } from "@/lib/utils";

interface ChurnTrendChartProps {
  data: ChurnDataPoint[];
}

export function ChurnTrendChart({ data }: ChurnTrendChartProps) {
  const chartData = data.length
    ? data.map((d) => ({
        period: d.period,
        churn_rate: d.churn_rate <= 1 ? d.churn_rate * 100 : d.churn_rate,
        at_risk: d.at_risk,
      }))
    : [
        { period: "Jan", churn_rate: 4.2, at_risk: 120 },
        { period: "Feb", churn_rate: 4.8, at_risk: 145 },
        { period: "Mar", churn_rate: 5.1, at_risk: 160 },
        { period: "Apr", churn_rate: 4.5, at_risk: 138 },
        { period: "May", churn_rate: 5.3, at_risk: 172 },
        { period: "Jun", churn_rate: 4.9, at_risk: 155 },
      ];

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis dataKey="period" stroke="#64748b" fontSize={12} tickLine={false} />
          <YAxis
            stroke="#64748b"
            fontSize={12}
            tickLine={false}
            tickFormatter={(v) => `${v}%`}
          />
          <Tooltip
            cursor={{ fill: "transparent" }}
            contentStyle={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: 8,
            }}
            formatter={(value, name) =>
              String(name) === "churn_rate" ? [formatPercent(Number(value) / 100), "Churn rate"]
                : [Number(value), "At risk"]
            }
          />
          <Bar dataKey="churn_rate" fill="#f87171" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
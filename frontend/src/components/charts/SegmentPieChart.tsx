import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { Segment } from "@/types";

interface SegmentPieChartProps {
  segments: Segment[];
}

const FALLBACK = [
  { name: "Champions", value: 28, color: "#22d3ee" },
  { name: "Loyal", value: 22, color: "#34d399" },
  { name: "At Risk", value: 18, color: "#fbbf24" },
  { name: "Hibernating", value: 15, color: "#94a3b8" },
  { name: "New", value: 17, color: "#a78bfa" },
];

export function SegmentPieChart({ segments }: SegmentPieChartProps) {
  const chartData =
    segments.length > 0
      ? segments.map((s) => ({
          name: s.name,
          value: s.size ?? 0,
          color: s.color_hex ?? "#22d3ee",
        }))
      : FALLBACK;

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={3}
            dataKey="value"
          >
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={entry.color ?? "#22d3ee"} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#0f172a",
              border: "1px solid #334155",
              borderRadius: 8,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
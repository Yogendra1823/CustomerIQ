import { cn } from "@/lib/utils";

interface SegmentBadgeProps {
  name: string;
  color?: string | null;
  size?: "sm" | "md";
}

export function SegmentBadge({ name, color, size = "sm" }: SegmentBadgeProps) {
  const bg = color ?? "#22d3ee";

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
      )}
      style={{
        borderColor: `${bg}55`,
        backgroundColor: `${bg}18`,
        color: bg,
      }}
    >
      <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: bg }} />
      {name}
    </span>
  );
}
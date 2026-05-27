import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { SegmentBadge } from "../components/SegmentBadge";
describe("SegmentBadge", () => {
  it("renders segment name correctly", () => {
    render(<SegmentBadge name="Premium Loyalists" color="#ef4444" />);
    expect(screen.getByText("Premium Loyalists")).toBeInTheDocument();
  });

  it("applies color style based on hex code", () => {
    const { container } = render(<SegmentBadge name="At-Risk Churners" color="#f59e0b" />);
    const badgeElement = container.querySelector("span");
    expect(badgeElement).toHaveStyle("color: rgb(245, 158, 11)");
    expect(badgeElement).toHaveStyle("background-color: rgba(245, 158, 11, 0.094)"); // #f59e0b18 is roughly 0.094 opacity
  });

  it("renders with a default fallback color when no color is provided", () => {
    const { container } = render(<SegmentBadge name="Standard Segment" color={undefined} />);
    const badgeElement = container.querySelector("span");
    expect(badgeElement).toHaveStyle("color: rgb(34, 211, 238)"); // #22d3ee is rgb(34, 211, 238)
  });
});

import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { KpiCard } from "../components/KpiCard";
import { DollarSign } from "lucide-react";
describe("KpiCard", () => {
  it("renders label and value correctly", () => {
    render(<KpiCard label="Total Revenue" value="$12,000" icon={DollarSign} />);
    expect(screen.getByText("Total Revenue")).toBeInTheDocument();
    expect(screen.getByText("$12,000")).toBeInTheDocument();
  });

  it("renders trend percentage if provided", () => {
    render(<KpiCard label="Total Revenue" value="$12,000" change={5.4} icon={DollarSign} />);
    expect(screen.getByText("+5.4% vs last period")).toBeInTheDocument();
  });

  it("renders negative trend percentage if provided", () => {
    render(<KpiCard label="Total Revenue" value="$12,000" change={-3.2} icon={DollarSign} />);
    expect(screen.getByText("-3.2% vs last period")).toBeInTheDocument();
  });
});

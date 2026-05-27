import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { DashboardPage } from "../pages/DashboardPage";
import { useDashboard } from "../hooks/useDashboard";
import { useSegments } from "../hooks/useSegments";
import { useRevenueAnalytics, useChurnAnalytics } from "../hooks/useAnalytics";

// Mock the hooks
vi.mock("../hooks/useDashboard", () => ({
  useDashboard: vi.fn(),
}));
vi.mock("../hooks/useSegments", () => ({
  useSegments: vi.fn(),
}));
vi.mock("../hooks/useAnalytics", () => ({
  useRevenueAnalytics: vi.fn(),
  useChurnAnalytics: vi.fn(),
}));

// Mock the charts to avoid Recharts rendering issues in jsdom
vi.mock("../components/charts/RevenueChart", () => ({
  RevenueChart: () => <div data-testid="mock-revenue-chart">Revenue Chart</div>,
}));
vi.mock("../components/charts/SegmentPieChart", () => ({
  SegmentPieChart: () => <div data-testid="mock-pie-chart">Pie Chart</div>,
}));
vi.mock("../components/charts/ChurnTrendChart", () => ({
  ChurnTrendChart: () => <div data-testid="mock-churn-chart">Churn Chart</div>,
}));

const mockStats = {
  total_customers: 1540,
  total_revenue: 128500.0,
  avg_clv: 3450.2,
  churn_rate: 0.125,
  revenue_growth_pct: 5.4,
  new_customers_30d: 85,
  high_risk_count: 32,
};

const mockSegments = [
  { id: 1, name: "VIPs", slug: "vips", size: 120, revenue_share: 45.0, color_hex: "#00FF00" },
];

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders PageHeader correctly", () => {
    vi.mocked(useDashboard).mockReturnValue({ data: undefined, isLoading: true } as any);
    vi.mocked(useSegments).mockReturnValue({ data: [], isLoading: false } as any);
    vi.mocked(useRevenueAnalytics).mockReturnValue({ data: undefined } as any);
    vi.mocked(useChurnAnalytics).mockReturnValue({ data: undefined } as any);

    render(<DashboardPage />);
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Real-time overview of customer health and revenue")).toBeInTheDocument();
  });

  it("renders Skeletons while loading stats", () => {
    vi.mocked(useDashboard).mockReturnValue({ data: undefined, isLoading: true } as any);
    vi.mocked(useSegments).mockReturnValue({ data: [], isLoading: false } as any);
    vi.mocked(useRevenueAnalytics).mockReturnValue({ data: undefined } as any);
    vi.mocked(useChurnAnalytics).mockReturnValue({ data: undefined } as any);

    render(<DashboardPage />);
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders KpiCards with formatted values once loaded", () => {
    vi.mocked(useDashboard).mockReturnValue({ data: mockStats, isLoading: false } as any);
    vi.mocked(useSegments).mockReturnValue({ data: mockSegments, isLoading: false } as any);
    vi.mocked(useRevenueAnalytics).mockReturnValue({ data: { data: [] } } as any);
    vi.mocked(useChurnAnalytics).mockReturnValue({ data: { data: [] } } as any);

    render(<DashboardPage />);

    expect(screen.getByText("Total customers")).toBeInTheDocument();
    expect(screen.getByText("1,540")).toBeInTheDocument();

    expect(screen.getByText("Total revenue")).toBeInTheDocument();
    expect(screen.getByText("₹1,28,500")).toBeInTheDocument();

    expect(screen.getByText("Avg CLV")).toBeInTheDocument();
    expect(screen.getByText("₹3,450")).toBeInTheDocument();

    expect(screen.getByText("Churn rate")).toBeInTheDocument();
    expect(screen.getByText("12.5%")).toBeInTheDocument();
  });

  it("renders all analytics charts", () => {
    vi.mocked(useDashboard).mockReturnValue({ data: mockStats, isLoading: false } as any);
    vi.mocked(useSegments).mockReturnValue({ data: mockSegments, isLoading: false } as any);
    vi.mocked(useRevenueAnalytics).mockReturnValue({ data: { data: [] } } as any);
    vi.mocked(useChurnAnalytics).mockReturnValue({ data: { data: [] } } as any);

    render(<DashboardPage />);

    expect(screen.getByTestId("mock-revenue-chart")).toBeInTheDocument();
    expect(screen.getByTestId("mock-pie-chart")).toBeInTheDocument();
    expect(screen.getByTestId("mock-churn-chart")).toBeInTheDocument();
  });

  it("displays trends correctly", () => {
    vi.mocked(useDashboard).mockReturnValue({ data: mockStats, isLoading: false } as any);
    vi.mocked(useSegments).mockReturnValue({ data: mockSegments, isLoading: false } as any);
    vi.mocked(useRevenueAnalytics).mockReturnValue({ data: { data: [] } } as any);
    vi.mocked(useChurnAnalytics).mockReturnValue({ data: { data: [] } } as any);

    render(<DashboardPage />);
    // Check trend indicators presence (+5.4%)
    expect(screen.getAllByText("+5.4% vs last period").length).toBeGreaterThan(0);
    expect(screen.getByText("-2.1% vs last period")).toBeInTheDocument();
  });
});

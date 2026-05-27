import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { CustomerDrawer } from "../components/CustomerDrawer";
import { useCustomer } from "../hooks/useCustomer";

// Mock the useCustomer hook
vi.mock("../hooks/useCustomer", () => ({
  useCustomer: vi.fn(),
}));

const mockCustomer = {
  id: "cust-1",
  external_id: "CUST_999",
  age: 30,
  gender: "Female",
  region: "Karnataka",
  membership_status: "premium",
  total_spend: "1250.50",
  clv_estimate: "1500.00",
  purchase_frequency: 5,
  churn_probability: "0.25",
  created_at: "2026-01-01T00:00:00Z",
  segment: {
    name: "Premium Loyalists",
    color_hex: "#00FF00",
  },
  transactions: [
    { id: "tx-1", amount: "500.00", category: "Electronics", order_id: "TX_1001" },
    { id: "tx-2", amount: "750.50", category: "Apparel", order_id: "TX_1002" },
  ],
};

describe("CustomerDrawer", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("does not render content when closed", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: undefined,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId={null} open={false} onOpenChange={vi.fn()} />);
    expect(screen.queryByText("Customer preview")).not.toBeInTheDocument();
  });

  it("renders loading skeleton when loading", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    expect(screen.getByText("Customer preview")).toBeInTheDocument();
    // Checking skeleton indicator (by class or container presence)
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders 'customer not found' when load is complete but data is missing", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: undefined,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    expect(screen.getByText("Customer not found")).toBeInTheDocument();
  });

  it("renders customer details correctly", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: mockCustomer,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    
    expect(screen.getByText("CUST_999")).toBeInTheDocument();
    expect(screen.getByText("Premium Loyalists")).toBeInTheDocument();
    expect(screen.getByText("Region")).toBeInTheDocument();
    expect(screen.getByText("Karnataka")).toBeInTheDocument();
    expect(screen.getByText("Orders")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
  });

  it("renders transactions correctly", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: mockCustomer,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    
    expect(screen.getByText("Electronics")).toBeInTheDocument();
    expect(screen.getByText("Apparel")).toBeInTheDocument();
  });

  it("calls onOpenChange when close button is clicked", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: mockCustomer,
      isLoading: false,
    } as any);

    const onOpenChange = vi.fn();
    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={onOpenChange} />);
    
    const closeBtn = screen.getByRole("button");
    fireEvent.click(closeBtn);
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("renders 'No transactions' if transactions list is empty", () => {
    const noTxCustomer = { ...mockCustomer, transactions: [] };
    vi.mocked(useCustomer).mockReturnValue({
      data: noTxCustomer,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    expect(screen.getByText("No transactions")).toBeInTheDocument();
  });

  it("displays proper currency formatting for total spend", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: mockCustomer,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    expect(screen.getByText("₹1,251")).toBeInTheDocument();
  });

  it("displays proper currency formatting for clv estimate", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: mockCustomer,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    expect(screen.getByText("₹1,500")).toBeInTheDocument();
  });

  it("renders churn probability metrics accurately", () => {
    vi.mocked(useCustomer).mockReturnValue({
      data: mockCustomer,
      isLoading: false,
    } as any);

    render(<CustomerDrawer customerId="cust-1" open={true} onOpenChange={vi.fn()} />);
    // Probability is 0.25 (25%)
    expect(screen.getByText("25.0%")).toBeInTheDocument();
  });
});

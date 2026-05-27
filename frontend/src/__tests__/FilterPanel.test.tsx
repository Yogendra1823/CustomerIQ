import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { FilterPanel } from "../components/FilterPanel";

describe("FilterPanel", () => {
  it("renders search input correctly", () => {
    const onSearchChange = vi.fn();
    render(<FilterPanel search="" onSearchChange={onSearchChange} />);
    expect(screen.getByPlaceholderText("Search by customer ID...")).toBeInTheDocument();
  });

  it("calls onSearchChange when search input changes", () => {
    const onSearchChange = vi.fn();
    render(<FilterPanel search="" onSearchChange={onSearchChange} />);
    
    const input = screen.getByPlaceholderText("Search by customer ID...");
    fireEvent.change(input, { target: { value: "123" } });
    
    expect(onSearchChange).toHaveBeenCalledWith("123");
  });

  it("renders region select if regions are provided", () => {
    const onSearchChange = vi.fn();
    const onRegionChange = vi.fn();
    render(
      <FilterPanel 
        search="" 
        onSearchChange={onSearchChange} 
        region="" 
        onRegionChange={onRegionChange}
        regions={[{ label: "North America", value: "NA" }]}
      />
    );
    expect(screen.getByRole("combobox")).toBeInTheDocument();
    expect(screen.getByText("North America")).toBeInTheDocument();
  });

  it("calls onRegionChange when region is selected", () => {
    const onSearchChange = vi.fn();
    const onRegionChange = vi.fn();
    render(
      <FilterPanel 
        search="" 
        onSearchChange={onSearchChange} 
        region="" 
        onRegionChange={onRegionChange}
        regions={[{ label: "North America", value: "NA" }]}
      />
    );
    
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "NA" } });
    
    expect(onRegionChange).toHaveBeenCalledWith("NA");
  });

  it("shows clear button when filters are active and onClear is provided", () => {
    const onSearchChange = vi.fn();
    const onClear = vi.fn();
    render(
      <FilterPanel 
        search="test" 
        onSearchChange={onSearchChange} 
        onClear={onClear}
      />
    );
    
    const clearBtn = screen.getByRole("button", { name: /clear/i });
    expect(clearBtn).toBeInTheDocument();
    
    fireEvent.click(clearBtn);
    expect(onClear).toHaveBeenCalled();
  });

  it("renders value tier select if valueTiers are provided", () => {
    const onSearchChange = vi.fn();
    const onValueTierChange = vi.fn();
    render(
      <FilterPanel 
        search="" 
        onSearchChange={onSearchChange} 
        valueTier="" 
        onValueTierChange={onValueTierChange}
        valueTiers={[{ label: "High-Value", value: "high" }]}
      />
    );
    expect(screen.getByRole("combobox")).toBeInTheDocument();
    expect(screen.getByText("High-Value")).toBeInTheDocument();
  });

  it("calls onValueTierChange when value tier option is selected", () => {
    const onSearchChange = vi.fn();
    const onValueTierChange = vi.fn();
    render(
      <FilterPanel 
        search="" 
        onSearchChange={onSearchChange} 
        valueTier="" 
        onValueTierChange={onValueTierChange}
        valueTiers={[{ label: "High-Value", value: "high" }]}
      />
    );
    
    const select = screen.getByRole("combobox");
    fireEvent.change(select, { target: { value: "high" } });
    
    expect(onValueTierChange).toHaveBeenCalledWith("high");
  });

  it("does not render region select if onRegionChange is not provided", () => {
    render(<FilterPanel search="" onSearchChange={vi.fn()} />);
    // Select elements should not be present (search is input[type=search], not select/combobox)
    expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
  });

  it("does not render value tier select if onValueTierChange is not provided", () => {
    render(<FilterPanel search="" onSearchChange={vi.fn()} region="" onRegionChange={vi.fn()} />);
    // There should only be one select (for region) instead of two
    const selects = screen.getAllByRole("combobox");
    expect(selects.length).toBe(1);
  });

  it("does not render clear button when filters are empty", () => {
    render(<FilterPanel search="" onSearchChange={vi.fn()} onClear={vi.fn()} />);
    expect(screen.queryByRole("button", { name: /clear/i })).not.toBeInTheDocument();
  });
});

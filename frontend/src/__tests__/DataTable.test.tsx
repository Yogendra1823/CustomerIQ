import { describe, expect, it, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { DataTable } from "../components/DataTable";
interface TestRow {
  id: string;
  name: string;
  role: string;
}

describe("DataTable", () => {
  const columns = [
    { key: "name", header: "Name" },
    { key: "role", header: "Role" },
  ];

  const data: TestRow[] = [
    { id: "1", name: "Alice", role: "Developer" },
    { id: "2", name: "Bob", role: "Designer" },
  ];

  const keyExtractor = (row: TestRow) => row.id;

  it("renders empty message if data is empty", () => {
    render(
      <DataTable
        columns={columns}
        data={[]}
        keyExtractor={keyExtractor}
        emptyMessage="No entries"
      />
    );
    expect(screen.getByText("No entries")).toBeInTheDocument();
  });

  it("renders table headers and rows correctly", () => {
    render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
      />
    );
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Role")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
  });

  it("calls onRowClick when a row is clicked", () => {
    const onRowClick = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
        onRowClick={onRowClick}
      />
    );

    fireEvent.click(screen.getByText("Alice"));
    expect(onRowClick).toHaveBeenCalledWith(data[0]);
  });

  it("triggers page change callback when pagination buttons are clicked", () => {
    const onPageChange = vi.fn();
    render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
        page={1}
        pages={3}
        onPageChange={onPageChange}
      />
    );

    expect(screen.getByText("Page 1 of 3")).toBeInTheDocument();
    
    // Find next page button. It contains ChevronRight SVG.
    const buttons = screen.getAllByRole("button");
    fireEvent.click(buttons[1]);
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("disables previous button on first page and next button on last page", () => {
    const onPageChange = vi.fn();
    
    // First page
    const { rerender } = render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
        page={1}
        pages={2}
        onPageChange={onPageChange}
      />
    );
    const buttonsFirst = screen.getAllByRole("button");
    expect(buttonsFirst[0]).toBeDisabled(); // Prev disabled
    expect(buttonsFirst[1]).not.toBeDisabled(); // Next enabled

    // Last page
    rerender(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
        page={2}
        pages={2}
        onPageChange={onPageChange}
      />
    );
    const buttonsLast = screen.getAllByRole("button");
    expect(buttonsLast[0]).not.toBeDisabled(); // Prev enabled
    expect(buttonsLast[1]).toBeDisabled(); // Next disabled
  });

  it("does not render pagination footer when pages count is 1", () => {
    render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
        page={1}
        pages={1}
        onPageChange={vi.fn()}
      />
    );
    expect(screen.queryByText(/page 1 of/i)).not.toBeInTheDocument();
    expect(screen.queryAllByRole("button").length).toBe(0);
  });

  it("renders custom cell content correctly using render column parameter", () => {
    const customColumns = [
      {
        key: "name",
        header: "Name",
        render: (row: TestRow) => <span data-testid="custom-cell">{row.name.toUpperCase()}</span>,
      },
    ];

    render(
      <DataTable
        columns={customColumns}
        data={data}
        keyExtractor={keyExtractor}
      />
    );
    expect(screen.getAllByTestId("custom-cell")[0]).toBeInTheDocument();
    expect(screen.getByText("ALICE")).toBeInTheDocument();
  });

  it("applies interactive classes when onRowClick callback is provided", () => {
    const { container } = render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
        onRowClick={vi.fn()}
      />
    );
    const row = container.querySelector("tbody tr");
    expect(row).toHaveClass("cursor-pointer");
    expect(row).toHaveClass("hover:bg-slate-800/40");
  });

  it("does not apply interactive classes when onRowClick is not provided", () => {
    const { container } = render(
      <DataTable
        columns={columns}
        data={data}
        keyExtractor={keyExtractor}
      />
    );
    const row = container.querySelector("tbody tr");
    expect(row).not.toHaveClass("cursor-pointer");
    expect(row).not.toHaveClass("hover:bg-slate-800/40");
  });
});

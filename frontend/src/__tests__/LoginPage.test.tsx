import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { LoginPage } from "../pages/LoginPage";
import { useAuth } from "../hooks/useAuth";
import { BrowserRouter } from "react-router-dom";

// Mock useAuth hook
vi.mock("../hooks/useAuth", () => ({
  useAuth: vi.fn(),
}));

// Helper to render with Router
const renderWithRouter = (ui: React.ReactElement) => {
  return render(ui, { wrapper: BrowserRouter });
};

describe("LoginPage", () => {
  const mockLogin = vi.fn();
  const mockClearError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      clearError: mockClearError,
    } as any);
  });

  it("renders email and password input fields and buttons", () => {
    renderWithRouter(<LoginPage />);
    expect(screen.getByPlaceholderText("you@company.com")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("••••••••")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Sign in" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Google" })).toBeInTheDocument();
  });

  it("shows validation error for empty fields on submit", async () => {
    renderWithRouter(<LoginPage />);
    const submitBtn = screen.getByRole("button", { name: "Sign in" });
    
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Enter a valid email")).toBeInTheDocument();
    });
  });

  it("shows validation error for invalid email format", async () => {
    renderWithRouter(<LoginPage />);
    const emailInput = screen.getByPlaceholderText("you@company.com");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });

    fireEvent.change(emailInput, { target: { value: "invalidemail" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Enter a valid email")).toBeInTheDocument();
    });
  });

  it("shows validation error for short password", async () => {
    renderWithRouter(<LoginPage />);
    const emailInput = screen.getByPlaceholderText("you@company.com");
    const passwordInput = screen.getByPlaceholderText("••••••••");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "123" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(screen.getByText("Password must be at least 6 characters")).toBeInTheDocument();
    });
  });

  it("calls login function on successful form submit", async () => {
    renderWithRouter(<LoginPage />);
    const emailInput = screen.getByPlaceholderText("you@company.com");
    const passwordInput = screen.getByPlaceholderText("••••••••");
    const submitBtn = screen.getByRole("button", { name: "Sign in" });

    fireEvent.change(emailInput, { target: { value: "test@example.com" } });
    fireEvent.change(passwordInput, { target: { value: "password123" } });
    fireEvent.click(submitBtn);

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: "test@example.com",
        password: "password123",
      });
    });
  });

  it("displays loading spinner when login is in progress", () => {
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: true,
      error: null,
      clearError: mockClearError,
    } as any);

    renderWithRouter(<LoginPage />);
    const submitBtn = screen.getByRole("button", { name: /sign in/i });
    expect(submitBtn).toBeDisabled();
    // Verify loader indicator spinner exists inside button
    const spinner = submitBtn.querySelector(".animate-spin");
    expect(spinner).toBeInTheDocument();
  });

  it("displays API authentication error message", () => {
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isAuthenticated: false,
      isLoading: false,
      error: "Invalid email or password",
      clearError: mockClearError,
    } as any);

    renderWithRouter(<LoginPage />);
    expect(screen.getByText("Invalid email or password")).toBeInTheDocument();
  });

  it("clears error state when rendering or changing input values", () => {
    renderWithRouter(<LoginPage />);
    // clearError is called initially inside LoginPage
    expect(mockClearError).toHaveBeenCalled();
  });

  it("redirects to home if already authenticated", () => {
    vi.mocked(useAuth).mockReturnValue({
      login: mockLogin,
      isAuthenticated: true,
      isLoading: false,
      error: null,
      clearError: mockClearError,
    } as any);

    renderWithRouter(<LoginPage />);
    // Redirect means page doesn't render sign in header anymore
    expect(screen.queryByText("Sign in")).not.toBeInTheDocument();
  });

  it("redirects window href to Google login endpoint when Google button clicked", () => {
    // Mock window.location
    const originalLocation = window.location;
    delete (window as any).location;
    window.location = { href: "" } as any;

    renderWithRouter(<LoginPage />);
    const googleBtn = screen.getByRole("button", { name: /google/i });
    fireEvent.click(googleBtn);

    expect(window.location.href).toContain("/api/v1/auth/google/login");

    // Restore window.location
    (window as any).location = originalLocation;
  });
});

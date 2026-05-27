import { useAuthStore } from "@/store/auth";

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const tokens = useAuthStore((s) => s.tokens);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const error = useAuthStore((s) => s.error);
  const login = useAuthStore((s) => s.login);
  const signup = useAuthStore((s) => s.signup);
  const logout = useAuthStore((s) => s.logout);
  const clearError = useAuthStore((s) => s.clearError);

  const isAdmin = user?.role === "admin";

  return {
    user,
    tokens,
    isAuthenticated,
    isLoading,
    error,
    login,
    signup,
    logout,
    clearError,
    isAdmin,
  };
}
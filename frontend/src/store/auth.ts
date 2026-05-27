import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { AuthTokens, LoginCredentials, SignupCredentials, User } from "@/types";
import { authApi } from "@/lib/api";

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  signup: (credentials: SignupCredentials) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const { data } = await authApi.login(credentials);
          const tokens: AuthTokens = {
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            token_type: data.token_type,
          };
          let user = data.user ?? null;
          if (!user) {
            const me = await authApi.me();
            user = me?.data ?? null;
          }
          if (!user) {
            user = {
              id: "local",
              email: credentials.email,
              full_name: credentials.email.split("@")[0],
              role: "analyst",
              is_active: true,
              created_at: new Date().toISOString(),
            };
          }
          set({ user, tokens, isAuthenticated: true, isLoading: false });
        } catch (err: unknown) {
          const message =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
            "Invalid email or password";
          set({
            error: typeof message === "string" ? message : "Login failed",
            isLoading: false,
            isAuthenticated: false,
          });
          throw err;
        }
      },

      signup: async (credentials) => {
        set({ isLoading: true, error: null });
        try {
          const { data } = await authApi.signup(credentials);
          const tokens: AuthTokens = {
            access_token: data.access_token,
            refresh_token: data.refresh_token,
            token_type: data.token_type,
          };
          let user = data.user ?? null;
          if (!user) {
            const me = await authApi.me();
            user = me?.data ?? null;
          }
          if (!user) {
            user = {
              id: "local",
              email: credentials.email,
              full_name: credentials.full_name || credentials.email.split("@")[0],
              role: "analyst",
              is_active: true,
              created_at: new Date().toISOString(),
            };
          }
          set({ user, tokens, isAuthenticated: true, isLoading: false });
        } catch (err: unknown) {
          const message =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
            "Signup failed";
          set({
            error: typeof message === "string" ? message : "Signup failed",
            isLoading: false,
            isAuthenticated: false,
          });
          throw err;
        }
      },

      logout: async () => {
        try {
          await authApi.logout();
        } catch {
          /* ignore */
        }
        set({ user: null, tokens: null, isAuthenticated: false, error: null });
      },

      clearError: () => set({ error: null }),
      setUser: (user) => set({ user }),

      setTokens: async (accessToken, refreshToken) => {
        const tokens: AuthTokens = {
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: "bearer",
        };
        try {
          // Fetch the user profile using the new access token
          const response = await authApi.me();
          if (response?.data) {
            set({ user: response.data, tokens, isAuthenticated: true });
          } else {
            set({ tokens, isAuthenticated: true });
          }
        } catch {
          set({ tokens, isAuthenticated: true });
        }
      },
    }),
    {
      name: "customeriq-auth",
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        if (state?.tokens?.access_token) {
          state.isAuthenticated = true;
        }
      },
    },
  ),
);
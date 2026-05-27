import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "@/store/auth";

export function AuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const setTokens = useAuthStore((state) => state.setTokens);

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");

    if (accessToken && refreshToken) {
      // Pre-seed sessionStorage so the axios interceptor can read the token
      // before setTokens calls authApi.me()
      const storageKey = "customeriq-auth";
      const existing = sessionStorage.getItem(storageKey);
      const parsed = existing ? JSON.parse(existing) : { state: {} };
      parsed.state = {
        ...parsed.state,
        tokens: {
          access_token: accessToken,
          refresh_token: refreshToken,
          token_type: "bearer",
        },
        isAuthenticated: true,
      };
      sessionStorage.setItem(storageKey, JSON.stringify(parsed));

      // Now call setTokens which will fetch /auth/me and update the store
      void setTokens(accessToken, refreshToken).then(() => {
        navigate("/", { replace: true });
      });
    } else {
      navigate("/login", { replace: true });
    }
  }, [searchParams, navigate, setTokens]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950">
      <div className="flex flex-col items-center space-y-4">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-cyan-500 border-t-transparent"></div>
        <p className="text-sm text-slate-400">Signing you in with Google...</p>
      </div>
    </div>
  );
}

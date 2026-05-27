import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";
import type {
  AnalyticsOverview,
  AuthTokens,
  ChurnAnalytics,
  CustomerDetail,
  CustomerFilters,
  DashboardStats,
  LoginCredentials,
  SignupCredentials,
  MLModel,
  MLTrainRequest,
  MLTrainResponse,
  PaginatedCustomers,
  RevenueAnalytics,
  Segment,
  SegmentCreate,
  UploadResponse,
  User,
} from "@/types";

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const api = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

let refreshPromise: Promise<string> | null = null;

function getStoredTokens(): AuthTokens | null {
  try {
    const raw = sessionStorage.getItem("customeriq-auth");
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { state?: { tokens?: AuthTokens } };
    return parsed.state?.tokens ?? null;
  } catch {
    return null;
  }
}

function setAccessToken(token: string) {
  const raw = sessionStorage.getItem("customeriq-auth");
  if (!raw) return;
  try {
    const parsed = JSON.parse(raw) as { state: { tokens: AuthTokens; user: User | null } };
    parsed.state.tokens.access_token = token;
    sessionStorage.setItem("customeriq-auth", JSON.stringify(parsed));
  } catch {
    /* ignore */
  }
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const tokens = getStoredTokens();
  if (tokens?.access_token && config.headers) {
    config.headers.Authorization = `Bearer ${tokens.access_token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status !== 401 || !original || original._retry) {
      return Promise.reject(error);
    }

    const tokens = getStoredTokens();
    if (!tokens?.refresh_token) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (!refreshPromise) {
      refreshPromise = api
        .post<AuthTokens>("/api/v1/auth/refresh", { refresh_token: tokens.refresh_token })
        .then((res) => {
          const newAccess = res.data.access_token;
          setAccessToken(newAccess);
          return newAccess;
        })
        .finally(() => {
          refreshPromise = null;
        });
    }

    try {
      const accessToken = await refreshPromise;
      if (original.headers) {
        original.headers.Authorization = `Bearer ${accessToken}`;
      }
      return api(original);
    } catch {
      sessionStorage.removeItem("customeriq-auth");
      window.location.href = "/login";
      return Promise.reject(error);
    }
  },
);

export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<AuthTokens & { user?: User }>("/api/v1/auth/login", credentials),
  signup: (credentials: SignupCredentials) =>
    api.post<AuthTokens & { user?: User }>("/api/v1/auth/signup", credentials),
  refresh: (refresh_token: string) =>
    api.post<AuthTokens>("/api/v1/auth/refresh", { refresh_token }),
  logout: () => api.post("/api/v1/auth/logout"),
  me: () => api.get<User>("/api/v1/auth/me").catch(() => null),
};

export const dashboardApi = {
  stats: () => api.get<DashboardStats>("/api/v1/dashboard/stats"),
};

export const customersApi = {
  list: (params?: CustomerFilters) =>
    api.get<PaginatedCustomers>("/api/v1/customers", { params }),
  get: (id: string) => api.get<CustomerDetail>(`/api/v1/customers/${id}`),
};

export const segmentsApi = {
  list: () => api.get<Segment[]>("/api/v1/segments"),
  create: (data: SegmentCreate) => api.post<Segment>("/api/v1/segments", data),
};

export const analyticsApi = {
  overview: () => api.get<AnalyticsOverview>("/api/v1/analytics/overview"),
  revenue: (group_by = "month") =>
    api.get<RevenueAnalytics>("/api/v1/analytics/revenue", { params: { group_by } }),
  churn: () => api.get<ChurnAnalytics>("/api/v1/analytics/churn"),
};

export const mlApi = {
  models: () => api.get<MLModel[]>("/api/v1/ml/models"),
  train: (data: MLTrainRequest) => api.post<MLTrainResponse>("/api/v1/ml/train", data),
};

export const uploadApi = {
  upload: (file: File, onProgress?: (pct: number) => void) => {
    const form = new FormData();
    form.append("file", file);
    return api.post<UploadResponse>("/api/v1/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total));
        }
      },
    });
  },
};
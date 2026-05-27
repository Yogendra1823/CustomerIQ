export type UserRole = "admin" | "analyst" | "viewer";

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials {
  email: string;
  password: string;
  full_name?: string;
}

export interface Segment {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  color_hex: string | null;
  icon: string | null;
  avg_clv: number | null;
  avg_order_value: number | null;
  churn_rate: number | null;
  size: number | null;
  revenue_share: number | null;
  marketing_strategy: string | null;
  priority_score: number | null;
  created_at: string;
}

export interface SegmentCreate {
  name: string;
  slug: string;
  description?: string | null;
  color_hex?: string | null;
  icon?: string | null;
  avg_clv?: number | null;
  avg_order_value?: number | null;
  churn_rate?: number | null;
  size?: number | null;
  revenue_share?: number | null;
  marketing_strategy?: string | null;
  priority_score?: number | null;
}

export interface Transaction {
  id: string;
  customer_id: string;
  order_id: string;
  transaction_date: string;
  amount: number;
  category: string | null;
  items_count: number | null;
  status: string | null;
  channel: string | null;
  discount_applied: number | null;
  created_at: string;
}

export interface Customer {
  id: string;
  external_id: string;
  age: number | null;
  gender: string | null;
  region: string | null;
  country: string;
  membership_status: string;
  annual_income: number | null;
  total_spend: number;
  avg_order_value: number;
  clv_estimate: number | null;
  purchase_frequency: number;
  days_since_last_purchase: number | null;
  cart_abandonment_rate: number | null;
  return_rate: number | null;
  email_open_rate: number | null;
  app_usage_score: number | null;
  loyalty_points: number;
  referral_count: number;
  rfm_score: number | null;
  engagement_index: number | null;
  churn_probability: number | null;
  value_tier: string | null;
  predicted_clv_90d: number | null;
  preferred_category: string | null;
  segment_id: number | null;
  created_at: string;
  updated_at: string | null;
}

export interface CustomerDetail extends Customer {
  transactions: Transaction[];
  segment: Segment | null;
}

export interface PaginatedCustomers {
  items: Customer[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface CustomerFilters {
  page?: number;
  limit?: number;
  search?: string;
  segment_id?: number;
  region?: string;
  value_tier?: string;
}

export interface DashboardStats {
  total_customers: number;
  total_revenue: number;
  avg_clv: number;
  churn_rate: number;
  segments_count: number;
  revenue_growth_pct?: number;
  new_customers_30d?: number;
  high_risk_count?: number;
}

export interface RevenueDataPoint {
  period: string;
  revenue: number;
  orders?: number;
}

export interface RevenueAnalytics {
  group_by: string;
  data: RevenueDataPoint[];
}

export interface ChurnDataPoint {
  period: string;
  churn_rate: number;
  at_risk: number;
}

export interface ChurnAnalytics {
  data: ChurnDataPoint[];
}

export interface AnalyticsOverview {
  total_customers: number;
  total_revenue: number;
  avg_clv: number;
  churn_rate: number;
  segments_count: number;
  top_segments: { name: string; size: number; revenue_share: number }[];
  regional_breakdown: { region: string; customers: number; revenue: number }[];
}

export interface MLModel {
  id: string;
  run_name: string | null;
  algorithm: string | null;
  n_clusters: number | null;
  silhouette_score: number | null;
  davies_bouldin_score: number | null;
  inertia: number | null;
  training_samples: number | null;
  feature_count: number | null;
  runtime_seconds: number | null;
  model_path: string | null;
  parameters: Record<string, unknown> | null;
  metrics: Record<string, unknown> | null;
  is_active: boolean;
  created_at: string;
}

export interface MLTrainRequest {
  algorithm?: string;
  n_clusters?: number;
  run_name?: string;
}

export interface MLTrainResponse {
  run_id: string;
  status: string;
}

export interface UploadResponse {
  filename: string;
  rows_imported: number;
  message: string;
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}

export type SortDirection = "asc" | "desc";

export interface TableColumn<T> {
  key: keyof T | string;
  header: string;
  render?: (row: T) => React.ReactNode;
  className?: string;
}

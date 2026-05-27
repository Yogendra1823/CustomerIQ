import { Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { AdminRoute } from "@/components/auth/AdminRoute";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { LoginPage } from "@/pages/LoginPage";
import { SignupPage } from "@/pages/SignupPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { CustomersPage } from "@/pages/CustomersPage";
import { CustomerDetailPage } from "@/pages/CustomerDetailPage";
import { SegmentsPage } from "@/pages/SegmentsPage";
import { AnalyticsPage } from "@/pages/AnalyticsPage";
import { MLStudioPage } from "@/pages/MLStudioPage";
import { UploadPage } from "@/pages/UploadPage";
import { AuthCallback } from "@/pages/AuthCallback";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/signup" element={<SignupPage />} />
      <Route path="/auth/callback" element={<AuthCallback />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="customers" element={<CustomersPage />} />
          <Route path="customers/:id" element={<CustomerDetailPage />} />
          <Route path="segments" element={<SegmentsPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="upload" element={<UploadPage />} />
          <Route element={<AdminRoute />}>
            <Route path="ml-studio" element={<MLStudioPage />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
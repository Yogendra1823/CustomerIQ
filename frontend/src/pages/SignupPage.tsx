import { useEffect } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { motion } from "framer-motion";
import { BarChart3, Lock, Mail, User } from "lucide-react";
import { useForm } from "react-hook-form";
import { Navigate, useLocation, useNavigate, Link } from "react-router-dom";
import { z } from "zod";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

const schema = z.object({
  full_name: z.string().min(2, "Full name must be at least 2 characters"),
  email: z.string().email("Enter a valid email"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

type FormData = z.infer<typeof schema>;

export function SignupPage() {
  const { signup, isAuthenticated, isLoading, error, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname ?? "/";

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { full_name: "", email: "", password: "" },
  });

  const emailValue = watch("email");
  const passwordValue = watch("password");

  useEffect(() => {
    clearError();
  }, [emailValue, passwordValue, clearError]);

  if (isAuthenticated) {
    return <Navigate to={from} replace />;
  }

  const onSubmit = async (data: FormData) => {
    clearError();
    try {
      await signup(data);
      navigate(from, { replace: true });
    } catch {
      /* handled in store */
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950">
      <div className="hidden flex-1 flex-col justify-between bg-gradient-to-br from-slate-900 via-slate-950 to-cyan-950/40 p-12 lg:flex">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400">
            <BarChart3 className="h-6 w-6" />
          </div>
          <span className="text-xl font-bold text-white">CustomerIQ</span>
        </div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-4xl font-bold leading-tight text-white">
            Join the leading analytics platform
          </h2>
          <p className="mt-4 max-w-md text-slate-400">
            Start transforming your customer data into actionable insights today.
          </p>
        </motion.div>
        <p className="text-sm text-slate-600">© 2026 CustomerIQ · Thiranex</p>
      </div>
      <div className="flex flex-1 items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-xl"
        >
          <h1 className="text-2xl font-bold text-slate-50">Sign up</h1>
          <p className="mt-1 text-sm text-slate-400">Create your analytics workspace</p>
          <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} className="mt-8 space-y-5" noValidate>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  {...register("full_name")}
                  type="text"
                  className="h-11 w-full rounded-lg border border-slate-700 bg-slate-950 pl-10 pr-3 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  placeholder="John Doe"
                />
              </div>
              {errors.full_name ? (
                <p className="mt-1 text-xs text-red-400">{errors.full_name.message}</p>
              ) : null}
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  {...register("email")}
                  type="email"
                  className="h-11 w-full rounded-lg border border-slate-700 bg-slate-950 pl-10 pr-3 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  placeholder="you@company.com"
                />
              </div>
              {errors.email ? (
                <p className="mt-1 text-xs text-red-400">{errors.email.message}</p>
              ) : null}
            </div>
            <div>
              <label className="mb-1.5 block text-xs font-medium text-slate-400">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
                <input
                  {...register("password")}
                  type="password"
                  className="h-11 w-full rounded-lg border border-slate-700 bg-slate-950 pl-10 pr-3 text-sm text-slate-100 focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                  placeholder="••••••••"
                />
              </div>
              {errors.password ? (
                <p className="mt-1 text-xs text-red-400">{errors.password.message}</p>
              ) : null}
            </div>
            {error ? <p className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-300">{error}</p> : null}
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Sign up
            </Button>
            
            <p className="mt-4 text-center text-sm text-slate-400">
              Already have an account?{" "}
              <Link to="/login" className="text-cyan-400 hover:text-cyan-300">
                Sign in
              </Link>
            </p>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t border-slate-800" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-slate-900/80 px-2 text-slate-500">Or continue with</span>
              </div>
            </div>
            
            <Button type="button" variant="secondary" className="w-full" onClick={() => window.location.href = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/v1/auth/google/login`}>
              <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
              </svg>
              Google
            </Button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}

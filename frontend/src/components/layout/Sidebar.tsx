import { NavLink } from "react-router-dom";
import {
  BarChart3,
  Brain,
  LayoutDashboard,
  Layers,
  Upload,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/customers", label: "Customers", icon: Users },
  { to: "/segments", label: "Segments", icon: Layers },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/upload", label: "Upload", icon: Upload },
];

export function Sidebar() {
  const { isAdmin } = useAuth();

  return (
    <aside className="flex w-60 flex-col border-r border-slate-800 bg-slate-950">
      <div className="flex h-16 items-center gap-2 border-b border-slate-800 px-5">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400">
          <span className="text-sm font-bold">IQ</span>
        </div>
        <div>
          <p className="text-sm font-bold text-slate-50">CustomerIQ</p>
          <p className="text-[10px] uppercase tracking-wider text-slate-500">Segmentation</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-cyan-500/15 text-cyan-400"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-100",
              )
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
        {isAdmin ? (
          <NavLink
            to="/ml-studio"
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-cyan-500/15 text-cyan-400"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-100",
              )
            }
          >
            <Brain className="h-4 w-4 shrink-0" />
            ML Studio
          </NavLink>
        ) : null}
      </nav>
      <div className="border-t border-slate-800 p-4 text-xs text-slate-600">
        v1.0 · Thiranex
      </div>
    </aside>
  );
}
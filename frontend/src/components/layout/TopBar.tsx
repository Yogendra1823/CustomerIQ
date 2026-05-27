import { Bell, LogOut, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/Button";
import { useAuth } from "@/hooks/useAuth";

export function TopBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 backdrop-blur">
      <div className="relative hidden max-w-md flex-1 md:block">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
        <input
          type="search"
          placeholder="Search customer ID..."
          className="h-9 w-full rounded-lg border border-slate-800 bg-slate-900 pl-10 pr-3 text-sm text-slate-200 placeholder:text-slate-600 focus:border-cyan-500 focus:outline-none"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              const val = e.currentTarget.value;
              if (val) {
                navigate(`/customers?search=${encodeURIComponent(val)}`);
                e.currentTarget.value = "";
              }
            }
          }}
        />
      </div>
      <div className="ml-auto flex items-center gap-3">
        <button
          type="button"
          className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-slate-100"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
        </button>
        <div className="hidden text-right sm:block">
          <p className="text-sm font-medium text-slate-100">{user?.full_name ?? user?.email}</p>
          <p className="text-xs capitalize text-slate-500">{user?.role}</p>
        </div>
        <Button variant="ghost" size="sm" onClick={() => void handleLogout()}>
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">Logout</span>
        </Button>
      </div>
    </header>
  );
}
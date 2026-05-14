"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Camera,
  LayoutDashboard,
  CalendarDays,
  Building2,
  CreditCard,
  LogOut,
  Settings,
} from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/events", label: "Events", icon: CalendarDays },
  { href: "/dashboard/organization", label: "Organization", icon: Building2 },
  { href: "/dashboard/billing", label: "Billing", icon: CreditCard },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuthStore();

  return (
    <div className="min-h-screen bg-surface flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-surface-border bg-surface-card flex-shrink-0 flex flex-col">
        {/* Logo */}
        <div className="h-16 border-b border-surface-border flex items-center px-6 gap-2">
          <div className="w-7 h-7 rounded-lg bg-gallery-600 flex items-center justify-center">
            <Camera className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-display font-bold text-lg">Gallery</span>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-4 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = item.exact
              ? pathname === item.href
              : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150",
                  isActive
                    ? "bg-gallery-600/15 text-gallery-300 border border-gallery-600/20"
                    : "text-gray-400 hover:text-white hover:bg-surface-elevated"
                )}
              >
                <Icon
                  className={cn(
                    "w-4 h-4 transition-colors",
                    isActive ? "text-gallery-400" : "group-hover:text-gallery-400"
                  )}
                />
                {item.label}
              </Link>
            );
          })}
        </nav>

        {/* User info + actions */}
        <div className="p-4 border-t border-surface-border space-y-1">
          {/* User avatar */}
          {user && (
            <div className="flex items-center gap-3 px-3 py-2.5 mb-2">
              {user.avatar_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={user.avatar_url}
                  alt={user.name}
                  className="w-7 h-7 rounded-full border border-surface-border"
                />
              ) : (
                <div className="w-7 h-7 rounded-full bg-gallery-600/20 border border-gallery-600/30 flex items-center justify-center text-xs font-bold text-gallery-400">
                  {user.name?.charAt(0).toUpperCase() || "?"}
                </div>
              )}
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{user.name}</p>
                <p className="text-xs text-gray-500 capitalize">{user.account_type}</p>
              </div>
            </div>
          )}

          <Link
            href="/dashboard/settings"
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-white hover:bg-surface-elevated transition-all duration-150"
          >
            <Settings className="w-4 h-4" />
            Settings
          </Link>
          <button
            id="logout-btn"
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-150 w-full text-left"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto min-h-screen">
        {children}
      </main>
    </div>
  );
}

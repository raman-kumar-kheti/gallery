"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Building2, HardDrive, Users, Settings } from "lucide-react";
import { api } from "@/lib/api";
import { formatBytes, storagePercent } from "@/lib/utils";
import clsx from "clsx";

export default function OrganizationPage() {
  const { data: org, isLoading } = useQuery({
    queryKey: ["organization"],
    queryFn: () => api.get("/organizations/me").then((r) => r.data),
  });

  const usedPercent = org
    ? storagePercent(org.storage_used_bytes, org.storage_limit_bytes)
    : 0;

  const storageColor =
    usedPercent >= 90
      ? "bg-red-500"
      : usedPercent >= 70
      ? "bg-amber-500"
      : "bg-gallery-500";

  if (isLoading) {
    return (
      <div className="p-8 space-y-4 animate-pulse">
        <div className="h-6 bg-surface-elevated rounded w-1/3" />
        <div className="h-32 bg-surface-elevated rounded-2xl" />
      </div>
    );
  }

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Organization</h1>
          <p className="text-gray-400 text-sm mt-1">Manage your studio workspace.</p>
        </div>
        <Link href="/dashboard/organization/members" className="btn-primary">
          <Users className="w-4 h-4" />
          Manage members
        </Link>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Org info */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-gallery-600/15 border border-gallery-600/20 flex items-center justify-center">
              <Building2 className="w-5 h-5 text-gallery-400" />
            </div>
            <div>
              <h2 className="font-semibold text-white">{org?.name || "—"}</h2>
              <p className="text-xs text-gray-500">@{org?.slug || "—"}</p>
            </div>
          </div>

          <div className="space-y-3 text-sm">
            {[
              { label: "Organization ID", value: org?.id ? `${org.id.slice(0, 8)}…` : "—" },
              { label: "Created", value: org?.created_at ? new Date(org.created_at).toLocaleDateString() : "—" },
            ].map((item) => (
              <div key={item.label} className="flex items-center justify-between py-2 border-b border-surface-border last:border-0">
                <span className="text-gray-500">{item.label}</span>
                <span className="text-white font-mono text-xs">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Storage usage */}
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl bg-gallery-600/15 border border-gallery-600/20 flex items-center justify-center">
              <HardDrive className="w-5 h-5 text-gallery-400" />
            </div>
            <div>
              <h2 className="font-semibold text-white">Storage</h2>
              <p className="text-xs text-gray-500">Cloudflare R2</p>
            </div>
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-400">
                {formatBytes(org?.storage_used_bytes || 0)} used
              </span>
              <span className="text-gray-500">
                of {formatBytes(org?.storage_limit_bytes || 0)}
              </span>
            </div>
            {/* Progress bar */}
            <div className="h-2 bg-surface-elevated rounded-full overflow-hidden">
              <div
                className={clsx("h-full rounded-full transition-all duration-500", storageColor)}
                style={{ width: `${usedPercent}%` }}
              />
            </div>
            <p className={clsx(
              "text-xs mt-2",
              usedPercent >= 90 ? "text-red-400" : "text-gray-500"
            )}>
              {usedPercent}% used
              {usedPercent >= 80 && " — Consider upgrading your plan"}
            </p>
          </div>
        </div>
      </div>

      {/* Quick links */}
      <div className="glass-card p-6">
        <h3 className="font-semibold text-white mb-4">Quick actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[
            { href: "/dashboard/organization/members", label: "Manage members", icon: Users },
            { href: "/dashboard/billing", label: "Billing & plans", icon: Settings },
            { href: "/dashboard/events/new", label: "New event", icon: Building2 },
          ].map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.href}
                href={action.href}
                className="flex items-center gap-3 p-3 rounded-xl border border-surface-border
                           hover:border-gallery-600/40 hover:bg-surface-elevated
                           transition-all duration-200 text-sm text-gray-300 hover:text-white"
              >
                <Icon className="w-4 h-4 text-gallery-400" />
                {action.label}
              </Link>
            );
          })}
        </div>
      </div>
    </div>
  );
}

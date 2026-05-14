import type { Metadata } from "next";
import Link from "next/link";
import { Plus, CalendarDays, ImageIcon, TrendingUp, Zap } from "lucide-react";

export const metadata: Metadata = { title: "Dashboard" };

export default function DashboardPage() {
  const stats = [
    { label: "Total Events", value: "0", icon: CalendarDays, change: "+0" },
    { label: "Photos Processed", value: "0", icon: ImageIcon, change: "+0" },
    { label: "Guest Searches", value: "0", icon: Zap, change: "+0" },
    { label: "Storage Used", value: "0 MB", icon: TrendingUp, change: "" },
  ];

  return (
    <div className="p-8 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Dashboard</h1>
          <p className="text-gray-400 text-sm mt-1">Welcome back. Here's what's happening.</p>
        </div>
        <Link href="/dashboard/events/new" id="create-event-btn" className="btn-primary">
          <Plus className="w-4 h-4" />
          New Event
        </Link>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="glass-card p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">{stat.label}</span>
                <Icon className="w-4 h-4 text-gallery-500" />
              </div>
              <div className="text-3xl font-display font-bold text-white">{stat.value}</div>
              {stat.change && (
                <div className="text-xs text-gray-500 mt-1">{stat.change} this month</div>
              )}
            </div>
          );
        })}
      </div>

      {/* Recent events */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-semibold text-white">Recent Events</h2>
          <Link href="/dashboard/events" className="text-sm text-gallery-400 hover:text-gallery-300 transition-colors">
            View all →
          </Link>
        </div>

        {/* Empty state */}
        <div className="py-16 text-center">
          <CalendarDays className="w-10 h-10 text-gray-600 mx-auto mb-4" />
          <h3 className="font-medium text-gray-400 mb-2">No events yet</h3>
          <p className="text-sm text-gray-600 mb-6">
            Create your first event to start uploading photos and generating QR codes.
          </p>
          <Link href="/dashboard/events/new" className="btn-primary">
            <Plus className="w-4 h-4" />
            Create your first event
          </Link>
        </div>
      </div>
    </div>
  );
}

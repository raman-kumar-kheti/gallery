"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { Plus, CalendarDays, ImageIcon, QrCode, ChevronRight, Search } from "lucide-react";
import { api } from "@/lib/api";
import clsx from "clsx";

const STATUS_BADGE: Record<string, string> = {
  active: "badge-active",
  draft: "badge-draft",
  archived: "badge-archived",
  expired: "badge-archived",
};

export default function EventsPage() {
  const [search, setSearch] = useState("");
  const { data, isLoading } = useQuery({
    queryKey: ["events"],
    queryFn: () => api.get("/events/").then((r) => r.data.events),
  });

  const events = (data || []).filter((e: any) =>
    e.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8 animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Events</h1>
          <p className="text-gray-400 text-sm mt-1">Manage your photo galleries and QR codes.</p>
        </div>
        <Link href="/dashboard/events/new" id="new-event-btn" className="btn-primary">
          <Plus className="w-4 h-4" />
          New Event
        </Link>
      </div>

      {/* Search */}
      <div className="relative mb-6">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          placeholder="Search events..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input pl-10"
        />
      </div>

      {/* Events grid */}
      {isLoading ? (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card p-6 animate-pulse">
              <div className="h-4 bg-surface-elevated rounded w-2/3 mb-4" />
              <div className="h-3 bg-surface-elevated rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : events.length === 0 ? (
        <div className="glass-card py-20 text-center">
          <CalendarDays className="w-10 h-10 text-gray-600 mx-auto mb-4" />
          <h3 className="font-medium text-gray-400 mb-2">No events found</h3>
          <p className="text-sm text-gray-600 mb-6">Create your first event to get started.</p>
          <Link href="/dashboard/events/new" className="btn-primary">
            <Plus className="w-4 h-4" /> Create event
          </Link>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {events.map((event: any) => (
            <Link
              key={event.id}
              href={`/dashboard/events/${event.id}`}
              className="glass-card p-6 hover:border-gallery-600/40 transition-all duration-200 group block"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-white group-hover:text-gallery-300 transition-colors">
                    {event.title}
                  </h3>
                  <p className="text-xs text-gray-500 capitalize mt-0.5">{event.event_type}</p>
                </div>
                <span className={STATUS_BADGE[event.status] || "badge-draft"}>
                  {event.status}
                </span>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span className="flex items-center gap-1.5">
                  <ImageIcon className="w-3.5 h-3.5" /> {event.image_count} photos
                </span>
                <span className="flex items-center gap-1.5">
                  <QrCode className="w-3.5 h-3.5" /> QR ready
                </span>
              </div>
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-surface-border">
                <span className="text-xs text-gray-600">
                  {new Date(event.created_at).toLocaleDateString()}
                </span>
                <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-gallery-400 transition-colors" />
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

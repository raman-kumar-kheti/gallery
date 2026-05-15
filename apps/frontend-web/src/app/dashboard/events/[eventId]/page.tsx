"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Upload, QrCode, ImageIcon, Settings2, Zap, Calendar } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

const STATUS_BADGE: Record<string, string> = {
  active: "badge-active",
  draft: "badge-draft",
  archived: "badge-archived",
};

export default function EventDetailPage() {
  const { eventId } = useParams<{ eventId: string }>();

  const { data: event, isLoading } = useQuery({
    queryKey: ["event", eventId],
    queryFn: () => api.get(`/events/${eventId}`).then((r) => r.data),
  });

  const activateMutation = useMutation({
    mutationFn: () => api.patch(`/events/${eventId}/activate`),
    onSuccess: () => toast.success("Event is now active!"),
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-surface-elevated rounded w-1/3" />
          <div className="h-4 bg-surface-elevated rounded w-1/4" />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 animate-fade-in">
      <Link href="/dashboard/events" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        All events
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <h1 className="text-2xl font-display font-bold text-white">{event?.title}</h1>
            <span className={STATUS_BADGE[event?.status] || "badge-draft"}>
              {event?.status}
            </span>
          </div>
          <p className="text-gray-400 text-sm capitalize">{event?.event_type} event</p>
        </div>
        {event?.status === "draft" && (
          <button
            id="activate-event-btn"
            onClick={() => activateMutation.mutate()}
            className="btn-primary"
          >
            <Zap className="w-4 h-4" />
            Activate event
          </button>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: "Photos", value: event?.image_count || 0, icon: ImageIcon },
          { label: "Index version", value: event?.index_version || 0, icon: Zap },
          { label: "Status", value: event?.status || "—", icon: Settings2 },
          {
            label: "Expires",
            value: event?.expires_at ? new Date(event.expires_at).toLocaleDateString() : "Never",
            icon: Calendar,
          },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="glass-card p-5">
              <div className="flex items-center gap-2 text-xs text-gray-500 mb-2">
                <Icon className="w-3.5 h-3.5" />
                {stat.label}
              </div>
              <div className="text-xl font-bold text-white">{stat.value}</div>
            </div>
          );
        })}
      </div>

      {/* Action cards */}
      <div className="grid md:grid-cols-3 gap-4">
        <Link href={`/dashboard/events/${eventId}/uploads`} className="glass-card p-6 hover:border-gallery-600/40 transition-all duration-200 group block">
          <div className="w-10 h-10 rounded-xl bg-gallery-600/15 border border-gallery-600/20 flex items-center justify-center text-gallery-400 mb-4 group-hover:bg-gallery-600/25 transition-colors">
            <Upload className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-white mb-1">Upload Photos</h3>
          <p className="text-sm text-gray-400">Upload and manage photos for this event.</p>
        </Link>

        <Link href={`/dashboard/events/${eventId}/qr`} className="glass-card p-6 hover:border-gallery-600/40 transition-all duration-200 group block">
          <div className="w-10 h-10 rounded-xl bg-gallery-600/15 border border-gallery-600/20 flex items-center justify-center text-gallery-400 mb-4 group-hover:bg-gallery-600/25 transition-colors">
            <QrCode className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-white mb-1">QR Code</h3>
          <p className="text-sm text-gray-400">Generate and display the guest QR code.</p>
        </Link>

        <div className="glass-card p-6">
          <div className="w-10 h-10 rounded-xl bg-surface-elevated flex items-center justify-center text-gray-500 mb-4">
            <ImageIcon className="w-5 h-5" />
          </div>
          <h3 className="font-semibold text-white mb-1">Gallery</h3>
          <p className="text-sm text-gray-400">{event?.image_count || 0} photos processed.</p>
          <p className="text-xs text-gray-600 mt-2">Search index v{event?.index_version || 0}</p>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

const EVENT_TYPES = [
  { value: "wedding", label: "Wedding" },
  { value: "corporate", label: "Corporate" },
  { value: "birthday", label: "Birthday" },
  { value: "conference", label: "Conference" },
  { value: "sports", label: "Sports" },
  { value: "other", label: "Other" },
];

export default function NewEventPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    title: "",
    event_type: "other",
    description: "",
    expires_at: "",
  });

  const mutation = useMutation({
    mutationFn: (data: typeof form) =>
      api.post("/events/", {
        ...data,
        expires_at: data.expires_at || undefined,
      }),
    onSuccess: (res) => {
      toast.success("Event created!");
      router.push(`/dashboard/events/${res.data.id}`);
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to create event");
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim()) {
      toast.error("Event title is required");
      return;
    }
    mutation.mutate(form);
  };

  return (
    <div className="p-8 animate-fade-in max-w-2xl">
      <Link href="/dashboard/events" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to events
      </Link>

      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white">Create new event</h1>
        <p className="text-gray-400 text-sm mt-1">Set up a gallery for your event.</p>
      </div>

      <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Event title *</label>
          <input
            id="event-title"
            type="text"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            placeholder="e.g. Sarah & John's Wedding"
            className="input"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Event type</label>
          <select
            id="event-type"
            value={form.event_type}
            onChange={(e) => setForm({ ...form, event_type: e.target.value })}
            className="input"
          >
            {EVENT_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
          <textarea
            id="event-description"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            placeholder="Optional event description..."
            rows={3}
            className="input resize-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Expires at <span className="text-gray-500">(optional)</span>
          </label>
          <input
            id="event-expires"
            type="datetime-local"
            value={form.expires_at}
            onChange={(e) => setForm({ ...form, expires_at: e.target.value })}
            className="input"
          />
          <p className="text-xs text-gray-500 mt-1">After this date, guests can no longer search.</p>
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            id="submit-event-btn"
            disabled={mutation.isPending}
            className="btn-primary flex-1 justify-center py-3"
          >
            {mutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : null}
            {mutation.isPending ? "Creating..." : "Create event"}
          </button>
          <Link href="/dashboard/events" className="btn-ghost py-3 px-6">
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}

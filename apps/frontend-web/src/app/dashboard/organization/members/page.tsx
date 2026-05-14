"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, UserPlus, Trash2, Loader2, Users, Shield } from "lucide-react";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import toast from "react-hot-toast";
import clsx from "clsx";

const ROLES = ["owner", "manager", "uploader"] as const;
type Role = (typeof ROLES)[number];

const ROLE_COLORS: Record<Role, string> = {
  owner: "bg-gallery-600/15 text-gallery-400 border-gallery-600/25",
  manager: "bg-violet-500/15 text-violet-400 border-violet-500/25",
  uploader: "bg-emerald-500/15 text-emerald-400 border-emerald-500/25",
};

const ROLE_DESCRIPTIONS: Record<Role, string> = {
  owner: "Full access — billing, users, events",
  manager: "Create & manage events and uploads",
  uploader: "Upload photos only",
};

export default function MembersPage() {
  const qc = useQueryClient();
  const [showInvite, setShowInvite] = useState(false);
  const [inviteForm, setInviteForm] = useState({ user_id: "", role_name: "uploader" as Role });

  const { data, isLoading } = useQuery({
    queryKey: ["members"],
    queryFn: () => api.get("/organizations/me/members").then((r) => r.data.members),
  });

  const inviteMutation = useMutation({
    mutationFn: (body: { user_id: string; role_name: string }) =>
      api.post("/organizations/me/members", body),
    onSuccess: () => {
      toast.success("Member added!");
      qc.invalidateQueries({ queryKey: ["members"] });
      setShowInvite(false);
      setInviteForm({ user_id: "", role_name: "uploader" });
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || "Failed to add member"),
  });

  const removeMutation = useMutation({
    mutationFn: (memberId: string) => api.delete(`/organizations/me/members/${memberId}`),
    onSuccess: () => {
      toast.success("Member removed");
      qc.invalidateQueries({ queryKey: ["members"] });
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || "Failed to remove"),
  });

  const members = data || [];

  return (
    <div className="p-8 animate-fade-in">
      <Link href="/dashboard/organization" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Organization
      </Link>

      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-display font-bold text-white">Team Members</h1>
          <p className="text-gray-400 text-sm mt-1">Manage who has access to your studio workspace.</p>
        </div>
        <button
          id="invite-member-btn"
          onClick={() => setShowInvite(!showInvite)}
          className="btn-primary"
        >
          <UserPlus className="w-4 h-4" />
          Add member
        </button>
      </div>

      {/* Invite form */}
      {showInvite && (
        <div className="glass-card p-6 mb-6 animate-slide-up border-gallery-600/30">
          <h3 className="font-semibold text-white mb-4">Add team member</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-gray-400 mb-1.5">User ID</label>
              <input
                id="invite-user-id"
                type="text"
                value={inviteForm.user_id}
                onChange={(e) => setInviteForm({ ...inviteForm, user_id: e.target.value })}
                placeholder="UUID of the user to invite"
                className="input"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-400 mb-1.5">Role</label>
              <select
                id="invite-role"
                value={inviteForm.role_name}
                onChange={(e) => setInviteForm({ ...inviteForm, role_name: e.target.value as Role })}
                className="input"
              >
                {ROLES.map((r) => (
                  <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Role descriptions */}
          <div className="mt-4 flex flex-wrap gap-2">
            {ROLES.map((r) => (
              <div key={r} className={clsx("badge border", ROLE_COLORS[r])}>
                <Shield className="w-3 h-3" />
                {r}: <span className="text-gray-400 font-normal">{ROLE_DESCRIPTIONS[r]}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-3 mt-4">
            <button
              id="confirm-invite-btn"
              onClick={() => inviteMutation.mutate(inviteForm)}
              disabled={!inviteForm.user_id || inviteMutation.isPending}
              className="btn-primary disabled:opacity-50"
            >
              {inviteMutation.isPending && <Loader2 className="w-3 h-3 animate-spin" />}
              Add member
            </button>
            <button onClick={() => setShowInvite(false)} className="btn-ghost">Cancel</button>
          </div>
        </div>
      )}

      {/* Members list */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="glass-card p-4 animate-pulse flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-surface-elevated" />
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-surface-elevated rounded w-1/3" />
                <div className="h-3 bg-surface-elevated rounded w-1/4" />
              </div>
            </div>
          ))}
        </div>
      ) : members.length === 0 ? (
        <div className="glass-card py-16 text-center">
          <Users className="w-10 h-10 text-gray-600 mx-auto mb-4" />
          <h3 className="font-medium text-gray-400 mb-2">No team members yet</h3>
          <p className="text-sm text-gray-600">Add your first team member to collaborate on events.</p>
        </div>
      ) : (
        <div className="glass-card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="border-b border-surface-border">
              <tr className="text-left">
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Member</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Role</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wide">Added</th>
                <th className="px-6 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {members.map((member: any) => (
                <tr key={member.id} className="hover:bg-surface-elevated/30 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gallery-600/20 border border-gallery-600/30 flex items-center justify-center text-sm font-bold text-gallery-400">
                        {member.user_name?.charAt(0).toUpperCase() || "?"}
                      </div>
                      <div>
                        <p className="font-medium text-white">{member.user_name}</p>
                        <p className="text-xs text-gray-500">{member.user_email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={clsx("badge border", ROLE_COLORS[member.role as Role] || "bg-gray-500/15 text-gray-400 border-gray-500/25")}>
                      {member.role}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500">
                    {formatDate(member.created_at)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {member.role !== "owner" && (
                      <button
                        onClick={() => {
                          if (confirm(`Remove ${member.user_name} from your organization?`)) {
                            removeMutation.mutate(member.id);
                          }
                        }}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Camera, Building2, User, ShoppingBag, ChevronRight, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import clsx from "clsx";

type AccountType = "studio" | "photographer" | "customer";

const ACCOUNT_TYPES = [
  {
    type: "studio" as AccountType,
    icon: <Building2 className="w-6 h-6" />,
    title: "Studio",
    subtitle: "Organization workspace",
    description: "Team RBAC, multiple events, billing management, internal users.",
    color: "gallery",
  },
  {
    type: "photographer" as AccountType,
    icon: <Camera className="w-6 h-6" />,
    title: "Photographer",
    subtitle: "Individual professional",
    description: "Create and manage multiple events, subscription-based.",
    color: "violet",
  },
  {
    type: "customer" as AccountType,
    icon: <ShoppingBag className="w-6 h-6" />,
    title: "Customer",
    subtitle: "Pay per event",
    description: "Create events, pay per event, invite temporary uploaders.",
    color: "emerald",
  },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [selected, setSelected] = useState<AccountType | null>(null);
  const [orgName, setOrgName] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!selected) return;
    if (selected === "studio" && !orgName.trim()) {
      toast.error("Please enter your studio name");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/onboarding", {
        account_type: selected,
        organization_name: selected === "studio" ? orgName : undefined,
      });
      toast.success("Welcome to Gallery!");
      router.push("/dashboard");
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-6 py-12">
      <div className="w-full max-w-2xl animate-slide-up">
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-gallery-600 flex items-center justify-center">
              <Camera className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-xl">Gallery</span>
          </div>
          <h1 className="text-3xl font-display font-bold text-white mb-2">
            What best describes you?
          </h1>
          <p className="text-gray-400">Choose your account type to get started.</p>
        </div>

        {/* Account type selector */}
        <div className="grid gap-4 mb-6">
          {ACCOUNT_TYPES.map((account) => (
            <button
              key={account.type}
              id={`account-type-${account.type}`}
              onClick={() => setSelected(account.type)}
              className={clsx(
                "glass-card p-5 flex items-center gap-5 text-left transition-all duration-200 w-full",
                selected === account.type
                  ? "border-gallery-600/70 bg-gallery-600/10"
                  : "hover:border-surface-border/80 hover:bg-surface-elevated/50"
              )}
            >
              <div className={clsx(
                "w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 transition-colors",
                selected === account.type
                  ? "bg-gallery-600 text-white"
                  : "bg-surface-elevated text-gray-400"
              )}>
                {account.icon}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-0.5">
                  <span className="font-semibold text-white">{account.title}</span>
                  <span className="text-xs text-gray-500">{account.subtitle}</span>
                </div>
                <p className="text-sm text-gray-400">{account.description}</p>
              </div>
              <div className={clsx(
                "w-5 h-5 rounded-full border-2 flex-shrink-0 transition-colors",
                selected === account.type
                  ? "border-gallery-500 bg-gallery-500"
                  : "border-surface-border"
              )} />
            </button>
          ))}
        </div>

        {/* Studio name input */}
        {selected === "studio" && (
          <div className="mb-6 animate-slide-up">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Studio / Organization name
            </label>
            <input
              id="org-name-input"
              type="text"
              value={orgName}
              onChange={(e) => setOrgName(e.target.value)}
              placeholder="e.g. Pixel Perfect Studios"
              className="input"
            />
          </div>
        )}

        <button
          id="complete-onboarding-btn"
          onClick={handleSubmit}
          disabled={!selected || loading}
          className="btn-primary w-full justify-center py-3 text-base disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
          {loading ? "Setting up..." : "Continue"}
          {!loading && <ChevronRight className="w-4 h-4" />}
        </button>
      </div>
    </div>
  );
}

"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CreditCard, Check, Zap, HardDrive, CalendarDays, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { formatBytes } from "@/lib/utils";
import toast from "react-hot-toast";
import clsx from "clsx";

// Hardcoded plans for MVP display — in production fetch from /plans endpoint
const PLANS = [
  {
    id: "starter",
    name: "Starter",
    price: 999,
    storage_gb: 50,
    event_limit: 10,
    features: ["10 events/month", "50 GB storage", "AI face search", "QR codes", "Email support"],
    popular: false,
  },
  {
    id: "pro",
    name: "Pro",
    price: 2499,
    storage_gb: 250,
    event_limit: null,
    features: ["Unlimited events", "250 GB storage", "AI face search", "QR codes", "Priority support", "Team members (5)"],
    popular: true,
  },
  {
    id: "studio",
    name: "Studio",
    price: 5999,
    storage_gb: 1000,
    event_limit: null,
    features: ["Unlimited events", "1 TB storage", "AI face search", "QR codes", "Dedicated support", "Unlimited team members", "Custom branding"],
    popular: false,
  },
];

export default function BillingPage() {
  const { data: subscription } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.get("/organizations/me").then((r) => r.data),
    retry: false,
  });

  const orderMutation = useMutation({
    mutationFn: (amount: number) =>
      api.post("/payments/create-order", { amount }),
    onSuccess: (res) => {
      // Open Razorpay checkout
      const options = {
        key: res.data.razorpay_key,
        amount: res.data.amount,
        currency: res.data.currency,
        order_id: res.data.order_id,
        name: "Gallery",
        description: "Subscription payment",
        handler: async (response: any) => {
          try {
            await api.post("/payments/verify", {
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            toast.success("Payment successful! Subscription activated.");
          } catch {
            toast.error("Payment verification failed.");
          }
        },
        theme: { color: "#4b52e5" },
      };
      // @ts-ignore — Razorpay is loaded via CDN script tag
      const rzp = new window.Razorpay(options);
      rzp.open();
    },
    onError: () => toast.error("Failed to initiate payment"),
  });

  return (
    <div className="p-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white">Billing</h1>
        <p className="text-gray-400 text-sm mt-1">Manage your subscription and storage plan.</p>
      </div>

      {/* Current plan info */}
      {subscription && (
        <div className="glass-card p-5 mb-8 flex items-center gap-4 border-gallery-600/30">
          <div className="w-10 h-10 rounded-xl bg-gallery-600/15 border border-gallery-600/20 flex items-center justify-center">
            <CreditCard className="w-5 h-5 text-gallery-400" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">Current storage usage</p>
            <p className="text-xs text-gray-400 mt-0.5">
              {formatBytes(subscription.storage_used_bytes)} of{" "}
              {formatBytes(subscription.storage_limit_bytes)} used
            </p>
          </div>
          <span className="badge-active">Active</span>
        </div>
      )}

      {/* Plans grid */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {PLANS.map((plan) => (
          <div
            key={plan.id}
            className={clsx(
              "glass-card p-6 flex flex-col relative transition-all duration-200",
              plan.popular
                ? "border-gallery-600/60 shadow-lg shadow-gallery-600/10"
                : "hover:border-gallery-600/30"
            )}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="px-3 py-1 rounded-full bg-gallery-600 text-white text-xs font-semibold">
                  Most Popular
                </span>
              </div>
            )}

            <div className="mb-5">
              <h3 className="font-display font-bold text-white text-lg">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mt-2">
                <span className="text-3xl font-bold text-white">
                  ₹{plan.price.toLocaleString("en-IN")}
                </span>
                <span className="text-gray-500 text-sm">/month</span>
              </div>
            </div>

            {/* Stats */}
            <div className="flex gap-4 mb-5 text-xs text-gray-400">
              <span className="flex items-center gap-1">
                <HardDrive className="w-3.5 h-3.5 text-gallery-500" />
                {plan.storage_gb} GB
              </span>
              <span className="flex items-center gap-1">
                <CalendarDays className="w-3.5 h-3.5 text-gallery-500" />
                {plan.event_limit ? `${plan.event_limit} events` : "Unlimited events"}
              </span>
            </div>

            {/* Features */}
            <ul className="space-y-2 mb-6 flex-1">
              {plan.features.map((f) => (
                <li key={f} className="flex items-center gap-2.5 text-sm text-gray-300">
                  <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>

            <button
              id={`subscribe-${plan.id}-btn`}
              onClick={() => orderMutation.mutate(plan.price)}
              disabled={orderMutation.isPending}
              className={clsx(
                "w-full py-2.5 rounded-xl font-semibold text-sm transition-all duration-200",
                plan.popular
                  ? "btn-primary"
                  : "btn-ghost"
              )}
            >
              {orderMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin mx-auto" />
              ) : (
                "Get started"
              )}
            </button>
          </div>
        ))}
      </div>

      {/* Payment info */}
      <div className="glass-card p-5 flex items-start gap-3">
        <Zap className="w-4 h-4 text-gallery-400 mt-0.5 flex-shrink-0" />
        <div className="text-sm text-gray-400">
          <p className="font-medium text-white mb-1">Powered by Razorpay</p>
          <p>All payments are securely processed via Razorpay. Subscriptions auto-renew monthly. Cancel anytime.</p>
        </div>
      </div>
    </div>
  );
}

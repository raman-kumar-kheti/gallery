"use client";

import { Camera, Chrome } from "lucide-react";
import Link from "next/link";

export default function LoginPage() {
  const handleGoogleLogin = () => {
    window.location.href = `${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/google`;
  };

  return (
    <div className="min-h-screen bg-surface flex items-center justify-center px-6">
      {/* Background glow */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-gallery-600/8 rounded-full blur-3xl" />
      </div>

      <div className="w-full max-w-md animate-slide-up relative">
        {/* Logo */}
        <div className="text-center mb-10">
          <Link href="/" className="inline-flex items-center gap-2 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gallery-600 flex items-center justify-center">
              <Camera className="w-5 h-5 text-white" />
            </div>
            <span className="font-display font-bold text-2xl">Gallery</span>
          </Link>
          <h1 className="text-3xl font-display font-bold text-white mb-2">Welcome back</h1>
          <p className="text-gray-400 text-sm">Sign in to manage your event galleries</p>
        </div>

        {/* Card */}
        <div className="glass-card p-8">
          <button
            id="google-login-btn"
            onClick={handleGoogleLogin}
            className="w-full flex items-center justify-center gap-3 py-3 px-6 rounded-xl
                       border border-surface-border hover:border-gallery-600/50
                       bg-surface-elevated hover:bg-surface-elevated/80
                       text-white font-medium transition-all duration-200
                       hover:shadow-lg hover:shadow-gallery-600/10 active:scale-98"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Continue with Google
          </button>

          <div className="mt-6 pt-6 border-t border-surface-border text-center">
            <p className="text-xs text-gray-500 leading-relaxed">
              By continuing, you agree to our{" "}
              <Link href="/terms" className="text-gallery-400 hover:underline">Terms of Service</Link>
              {" "}and{" "}
              <Link href="/privacy" className="text-gallery-400 hover:underline">Privacy Policy</Link>.
            </p>
          </div>
        </div>

        {/* Account types info */}
        <div className="mt-6 glass-card p-5">
          <p className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-3">Account types</p>
          <div className="space-y-2 text-sm">
            {[
              { type: "Studio", desc: "Organization workspace with team RBAC" },
              { type: "Photographer", desc: "Individual professional account" },
              { type: "Customer", desc: "Pay-per-event account" },
            ].map((a) => (
              <div key={a.type} className="flex items-center gap-3">
                <span className="font-semibold text-gallery-400 w-24">{a.type}</span>
                <span className="text-gray-500">{a.desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

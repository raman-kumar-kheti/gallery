import type { Metadata } from "next";
import Link from "next/link";
import { Camera, Zap, Shield, Users, ChevronRight, Star } from "lucide-react";

export const metadata: Metadata = {
  title: "Gallery — AI-Powered Event Photo Delivery",
};

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface text-white overflow-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 inset-x-0 z-50 border-b border-surface-border/50 backdrop-blur-md bg-surface/80">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gallery-600 flex items-center justify-center">
              <Camera className="w-4 h-4 text-white" />
            </div>
            <span className="font-display font-bold text-xl">Gallery</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-400">
            <Link href="#features" className="hover:text-white transition-colors">Features</Link>
            <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
            <Link href="#how-it-works" className="hover:text-white transition-colors">How it works</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/auth/login" className="btn-ghost text-sm py-2 px-4">
              Sign in
            </Link>
            <Link href="/auth/login" className="btn-primary text-sm py-2 px-4">
              Get started free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-24 px-6 relative">
        {/* Background glow */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-gallery-600/10 rounded-full blur-3xl" />
        </div>

        <div className="max-w-5xl mx-auto text-center relative animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-gallery-600/15 border border-gallery-600/30 text-gallery-400 text-sm font-medium mb-8">
            <Zap className="w-3.5 h-3.5" />
            AI-Powered Photo Delivery
          </div>

          <h1 className="font-display text-5xl md:text-7xl font-bold tracking-tight leading-tight mb-6">
            Find your photos
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gallery-400 to-gallery-600">
              in seconds
            </span>
          </h1>

          <p className="text-gray-400 text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
            Event guests scan a QR code, upload a selfie, and instantly receive
            every photo of themselves from the event. No scrolling through thousands of images.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link href="/auth/login" className="btn-primary px-8 py-3 text-base">
              Start for free
              <ChevronRight className="w-4 h-4" />
            </Link>
            <Link href="#how-it-works" className="btn-ghost px-8 py-3 text-base">
              See how it works
            </Link>
          </div>

          {/* Social proof */}
          <div className="mt-12 flex items-center justify-center gap-6 text-sm text-gray-500">
            <div className="flex -space-x-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="w-8 h-8 rounded-full bg-gallery-600/30 border-2 border-surface flex items-center justify-center text-xs font-bold text-gallery-400">
                  {String.fromCharCode(64 + i)}
                </div>
              ))}
            </div>
            <span>Trusted by <strong className="text-white">500+</strong> event studios</span>
            <div className="flex items-center gap-1 text-amber-400">
              {[...Array(5)].map((_, i) => <Star key={i} className="w-3.5 h-3.5 fill-current" />)}
              <span className="text-gray-500 ml-1">4.9/5</span>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="section-title">How it works</h2>
            <p className="section-subtitle">Three steps. Zero friction for guests.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Scan QR Code",
                description: "Guests scan the event QR code displayed at the venue. No app download required.",
                icon: "📷",
              },
              {
                step: "02",
                title: "Upload a Selfie",
                description: "Take or upload a selfie directly in the browser. Our AI instantly identifies your facial features.",
                icon: "🤳",
              },
              {
                step: "03",
                title: "See Your Photos",
                description: "Instantly see every photo of you from the event — delivered in seconds by our smart photo matching.",
                icon: "✨",
              },
            ].map((item) => (
              <div key={item.step} className="glass-card p-8 relative group hover:border-gallery-600/50 transition-all duration-300">
                <div className="text-5xl mb-4">{item.icon}</div>
                <div className="text-xs font-mono text-gallery-500 font-semibold mb-2">{item.step}</div>
                <h3 className="text-xl font-display font-bold mb-3">{item.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-6 bg-surface-card/50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="section-title">Built for professionals</h2>
            <p className="section-subtitle">Everything studios and photographers need.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: <Users className="w-5 h-5" />, title: "Studio Workspaces", desc: "Team RBAC with owner, manager, and uploader roles." },
              { icon: <Shield className="w-5 h-5" />, title: "Event Isolation", desc: "Each event is completely isolated. No cross-event data leakage." },
              { icon: <Zap className="w-5 h-5" />, title: "Instant Search", desc: "Sub-second photo search powered by intelligent photo matching." },
              { icon: <Camera className="w-5 h-5" />, title: "Bulk Upload", desc: "Upload thousands of photos. AI processes them asynchronously." },
              { icon: <Shield className="w-5 h-5" />, title: "QR Access Control", desc: "Time-limited QR codes for secure guest access." },
              { icon: <Zap className="w-5 h-5" />, title: "Cloudflare R2 Storage", desc: "Zero egress fee storage. Built for scale." },
            ].map((f, i) => (
              <div key={i} className="glass-card p-6 hover:border-gallery-600/30 transition-all duration-300">
                <div className="w-10 h-10 rounded-xl bg-gallery-600/15 border border-gallery-600/20 flex items-center justify-center text-gallery-400 mb-4">
                  {f.icon}
                </div>
                <h3 className="font-semibold text-white mb-2">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <div className="glass-card p-12 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-gallery-600/10 to-transparent pointer-events-none" />
            <h2 className="font-display text-4xl font-bold mb-4 relative">
              Ready to transform your event delivery?
            </h2>
            <p className="text-gray-400 mb-8 relative">
              Join studios and photographers delivering AI-powered galleries.
            </p>
            <Link href="/auth/login" className="btn-primary px-10 py-3 text-base relative">
              Get started free
              <ChevronRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-surface-border py-8 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <Camera className="w-4 h-4 text-gallery-500" />
            <span className="font-semibold text-white">Gallery</span>
            <span>— AI-powered event photo delivery</span>
          </div>
          <p>© 2026 Gallery. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}

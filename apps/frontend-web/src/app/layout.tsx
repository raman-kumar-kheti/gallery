import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { Providers } from "@/components/providers";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: {
    default: "Gallery — AI-Powered Event Photos",
    template: "%s | Gallery",
  },
  description:
    "Instantly find your photos from any event using AI face recognition. Scan a QR code, upload a selfie, get your photos.",
  keywords: ["event photos", "face recognition", "AI gallery", "wedding photos", "event photography"],
  openGraph: {
    title: "Gallery — AI-Powered Event Photos",
    description: "Find your event photos in seconds using AI face search.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans`}>
        <Providers>{children}</Providers>
        {/* Razorpay Checkout SDK — loaded only when needed (billing page) */}
        <Script src="https://checkout.razorpay.com/v1/checkout.js" strategy="lazyOnload" />
      </body>
    </html>
  );
}


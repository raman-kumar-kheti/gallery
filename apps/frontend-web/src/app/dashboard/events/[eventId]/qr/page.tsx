"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, QrCode, Download, Copy, Loader2, ExternalLink } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import { QRCodeSVG } from "qrcode.react";

export default function QRPage() {
  const { eventId } = useParams<{ eventId: string }>();

  const generateMutation = useMutation({
    mutationFn: () => api.post(`/qr/generate/${eventId}`).then((r) => r.data),
    onSuccess: () => toast.success("QR code generated!"),
    onError: (err: any) => toast.error(err?.response?.data?.detail || "Failed to generate QR"),
  });

  const qrData = generateMutation.data;
  const guestUrl = qrData?.guest_url;

  const copyLink = () => {
    if (guestUrl) {
      navigator.clipboard.writeText(guestUrl);
      toast.success("Link copied!");
    }
  };

  return (
    <div className="p-8 animate-fade-in">
      <Link href={`/dashboard/events/${eventId}`} className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to event
      </Link>

      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white">QR Code</h1>
        <p className="text-gray-400 text-sm mt-1">
          Display this QR code at your event. Guests scan it to find their photos.
        </p>
      </div>

      <div className="max-w-md">
        {!qrData ? (
          <div className="glass-card p-10 text-center">
            <QrCode className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <h3 className="font-medium text-white mb-2">No QR code generated yet</h3>
            <p className="text-sm text-gray-400 mb-6">Generate a QR code to give guests access to the AI photo search.</p>
            <button
              id="generate-qr-btn"
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="btn-primary"
            >
              {generateMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
              Generate QR Code
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* QR display */}
            <div className="glass-card p-8 flex items-center justify-center">
              <div className="bg-white p-4 rounded-2xl">
                <QRCodeSVG value={guestUrl} size={200} level="H" />
              </div>
            </div>

            {/* Guest URL */}
            <div className="glass-card p-4 flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 mb-0.5">Guest URL</p>
                <p className="text-sm text-white truncate font-mono">{guestUrl}</p>
              </div>
              <button onClick={copyLink} className="btn-ghost py-2 px-3 flex-shrink-0">
                <Copy className="w-4 h-4" />
              </button>
              <Link href={guestUrl} target="_blank" className="btn-ghost py-2 px-3 flex-shrink-0">
                <ExternalLink className="w-4 h-4" />
              </Link>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => window.open(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/qr/image/${eventId}`, "_blank")}
                className="btn-ghost flex-1 justify-center"
              >
                <Download className="w-4 h-4" />
                Download PNG
              </button>
              <button
                onClick={() => generateMutation.mutate()}
                className="btn-ghost flex-1 justify-center"
              >
                Regenerate
              </button>
            </div>

            {qrData.expires_at && (
              <p className="text-xs text-gray-500 text-center">
                Expires: {new Date(qrData.expires_at).toLocaleDateString()}
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

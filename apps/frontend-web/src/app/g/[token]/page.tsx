"use client";

import { useCallback, useState, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter, useParams } from "next/navigation";
import { Camera, Loader2, Upload, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import clsx from "clsx";

export default function GuestScanPage() {
  const { token } = useParams<{ token: string }>();
  const router = useRouter();
  const [event, setEvent] = useState<{ event_id: string; event_title: string; event_type: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Resolve QR token → event info
  useEffect(() => {
    const resolve = async () => {
      try {
        const res = await api.get(`/qr/resolve/${token}`);
        setEvent(res.data);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Invalid or expired QR code.");
      } finally {
        setLoading(false);
      }
    };
    resolve();
  }, [token]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (!event || acceptedFiles.length === 0) return;
      const file = acceptedFiles[0];
      const previewUrl = URL.createObjectURL(file);
      setPreview(previewUrl);
      setUploading(true);

      try {
        const formData = new FormData();
        formData.append("selfie", file);

        // Check for existing session token
        const existingToken = localStorage.getItem(`session_${event.event_id}`);
        const headers: Record<string, string> = {};
        if (existingToken) {
          headers["X-Session-Token"] = existingToken;
        }

        const res = await api.post(
          `/search/selfie/${event.event_id}`,
          formData,
          { headers: { ...headers, "Content-Type": "multipart/form-data" } }
        );

        const { session_token } = res.data;
        // Save session token for caching
        localStorage.setItem(`session_${event.event_id}`, session_token);

        // Navigate to results with polling
        router.push(`/g/${token}/results?session=${session_token}`);
      } catch (err: any) {
        toast.error(err?.response?.data?.detail || "Upload failed. Please try again.");
        setPreview(null);
      } finally {
        setUploading(false);
      }
    },
    [event, router, token]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    maxFiles: 1,
    multiple: false,
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-gallery-400" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center px-6">
        <div className="text-center max-w-sm">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h1 className="text-xl font-bold text-white mb-2">QR Code Error</h1>
          <p className="text-gray-400 text-sm">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-surface flex flex-col">
      {/* Header */}
      <header className="border-b border-surface-border bg-surface-card/80 backdrop-blur px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gallery-600 flex items-center justify-center">
            <Camera className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-display font-bold">Gallery</span>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm animate-slide-up">
          {/* Event info */}
          <div className="text-center mb-8">
            <div className="inline-block px-3 py-1 rounded-full bg-gallery-600/15 border border-gallery-600/30 text-gallery-400 text-xs font-medium mb-4 capitalize">
              {event?.event_type}
            </div>
            <h1 className="text-2xl font-display font-bold text-white mb-2">
              {event?.event_title}
            </h1>
            <p className="text-gray-400 text-sm">
              Upload a selfie to instantly find <strong className="text-white">your photos</strong> from this event.
            </p>
          </div>

          {/* Selfie upload */}
          {preview ? (
            <div className="glass-card p-6 text-center">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={preview} alt="Your selfie" className="w-32 h-32 rounded-full mx-auto mb-4 object-cover border-4 border-gallery-600/50" />
              {uploading && (
                <div className="flex items-center justify-center gap-2 text-gallery-400">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Finding your photos...</span>
                </div>
              )}
            </div>
          ) : (
            <div
              {...getRootProps()}
              id="selfie-dropzone"
              className={clsx(
                "glass-card p-10 text-center cursor-pointer border-2 transition-all duration-200",
                isDragActive
                  ? "border-gallery-500 bg-gallery-600/10"
                  : "border-surface-border hover:border-gallery-600/50"
              )}
            >
              <input {...getInputProps()} />
              <div className="w-20 h-20 rounded-full bg-gallery-600/15 border-2 border-gallery-600/30 flex items-center justify-center mx-auto mb-4">
                <Camera className="w-8 h-8 text-gallery-400" />
              </div>
              <h2 className="font-semibold text-white mb-2">Upload your selfie</h2>
              <p className="text-sm text-gray-400 mb-4">
                Take a photo or upload one from your gallery.
              </p>
              <button id="selfie-upload-btn" className="btn-primary mx-auto">
                <Upload className="w-4 h-4" />
                Choose photo
              </button>
            </div>
          )}

          <p className="text-xs text-gray-600 text-center mt-6">
            Your selfie is only used for face matching and is not stored permanently.
          </p>
        </div>
      </div>
    </div>
  );
}

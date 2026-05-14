"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Camera, Loader2, Download, ImageIcon } from "lucide-react";
import { api } from "@/lib/api";

interface MatchedImage {
  id: string;
  image_url: string;
  thumbnail_url: string;
  width: number;
  height: number;
}

export default function GuestResultsPage() {
  const searchParams = useSearchParams();
  const sessionToken = searchParams.get("session");
  const [status, setStatus] = useState<"processing" | "completed" | "error">("processing");
  const [images, setImages] = useState<MatchedImage[]>([]);
  const [pollCount, setPollCount] = useState(0);

  useEffect(() => {
    if (!sessionToken) {
      setStatus("error");
      return;
    }

    const poll = async () => {
      try {
        const res = await api.get(`/search/results/${sessionToken}`);
        const { status: s, images: imgs } = res.data;
        if (s === "completed") {
          setImages(imgs || []);
          setStatus("completed");
        } else {
          // Continue polling
          setPollCount((c) => c + 1);
        }
      } catch {
        setStatus("error");
      }
    };

    // Poll every 2 seconds while processing
    if (status === "processing") {
      const timer = setTimeout(poll, 2000);
      return () => clearTimeout(timer);
    }
  }, [sessionToken, status, pollCount]);

  return (
    <div className="min-h-screen bg-surface">
      {/* Header */}
      <header className="border-b border-surface-border bg-surface-card/80 backdrop-blur px-6 py-4 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gallery-600 flex items-center justify-center">
            <Camera className="w-3.5 h-3.5 text-white" />
          </div>
          <span className="font-display font-bold">Gallery</span>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {status === "processing" && (
          <div className="text-center py-24 animate-fade-in">
            <div className="relative inline-block mb-6">
              <div className="w-20 h-20 rounded-full bg-gallery-600/15 border-2 border-gallery-600/30 flex items-center justify-center">
                <Loader2 className="w-8 h-8 text-gallery-400 animate-spin" />
              </div>
              <div className="absolute inset-0 rounded-full bg-gallery-600/10 animate-ping" />
            </div>
            <h1 className="text-2xl font-display font-bold text-white mb-2">
              Finding your photos...
            </h1>
            <p className="text-gray-400 text-sm">
              Our AI is scanning the event gallery for your face. This usually takes a few seconds.
            </p>
          </div>
        )}

        {status === "completed" && (
          <div className="animate-fade-in">
            <div className="text-center mb-10">
              <h1 className="text-3xl font-display font-bold text-white mb-2">
                Your Photos 🎉
              </h1>
              <p className="text-gray-400">
                Found <strong className="text-white">{images.length}</strong> photo{images.length !== 1 ? "s" : ""} of you.
              </p>
            </div>

            {images.length === 0 ? (
              <div className="glass-card py-20 text-center">
                <ImageIcon className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="font-medium text-gray-400 mb-2">No photos found</h3>
                <p className="text-sm text-gray-600">
                  We couldn't find any photos matching your face. Try uploading a clearer selfie.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {images.map((img) => (
                  <div key={img.id} className="group relative rounded-2xl overflow-hidden bg-surface-elevated aspect-square">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={img.thumbnail_url || img.image_url}
                      alt="Your photo"
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                    {/* Download overlay */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors duration-200 flex items-center justify-center">
                      <a
                        href={img.image_url}
                        download
                        target="_blank"
                        rel="noopener noreferrer"
                        className="opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <div className="w-10 h-10 rounded-full bg-white/20 backdrop-blur flex items-center justify-center hover:bg-white/30">
                          <Download className="w-5 h-5 text-white" />
                        </div>
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {status === "error" && (
          <div className="text-center py-24">
            <h1 className="text-2xl font-display font-bold text-white mb-2">Something went wrong</h1>
            <p className="text-gray-400 text-sm">Invalid session. Please scan the QR code again.</p>
          </div>
        )}
      </div>
    </div>
  );
}

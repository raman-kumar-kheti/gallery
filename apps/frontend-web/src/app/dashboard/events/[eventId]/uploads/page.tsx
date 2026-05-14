"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useMutation, useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Upload, ImageIcon, CheckCircle2, Clock, XCircle, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import toast from "react-hot-toast";
import clsx from "clsx";

const STATUS_ICONS: Record<string, React.ReactNode> = {
  pending: <Clock className="w-3 h-3 text-amber-400" />,
  processing: <Loader2 className="w-3 h-3 text-blue-400 animate-spin" />,
  completed: <CheckCircle2 className="w-3 h-3 text-emerald-400" />,
  failed: <XCircle className="w-3 h-3 text-red-400" />,
};

export default function UploadsPage() {
  const { eventId } = useParams<{ eventId: string }>();
  const [uploading, setUploading] = useState(false);

  const { data, refetch } = useQuery({
    queryKey: ["images", eventId],
    queryFn: () => api.get(`/images/event/${eventId}`).then((r) => r.data.images),
    refetchInterval: 5000, // Poll every 5s for processing updates
  });

  const uploadMutation = useMutation({
    mutationFn: async (files: File[]) => {
      for (const file of files) {
        const formData = new FormData();
        formData.append("file", file);
        await api.post(`/images/upload/${eventId}`, formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
    },
    onSuccess: () => {
      toast.success("Photos uploaded! AI processing started.");
      refetch();
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Upload failed");
    },
  });

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (acceptedFiles.length === 0) return;
      setUploading(true);
      try {
        await uploadMutation.mutateAsync(acceptedFiles);
      } finally {
        setUploading(false);
      }
    },
    [uploadMutation]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"] },
    multiple: true,
  });

  const images = data || [];

  return (
    <div className="p-8 animate-fade-in">
      <Link href={`/dashboard/events/${eventId}`} className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-white mb-6 transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to event
      </Link>

      <div className="mb-8">
        <h1 className="text-2xl font-display font-bold text-white">Upload Photos</h1>
        <p className="text-gray-400 text-sm mt-1">
          Drop photos here. AI processing starts automatically after upload.
        </p>
      </div>

      {/* Drop zone */}
      <div
        {...getRootProps()}
        id="photo-dropzone"
        className={clsx(
          "border-2 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all duration-200 mb-8",
          isDragActive
            ? "border-gallery-500 bg-gallery-600/10"
            : "border-surface-border hover:border-gallery-600/50 hover:bg-surface-elevated/30"
        )}
      >
        <input {...getInputProps()} />
        <Upload className={clsx("w-10 h-10 mx-auto mb-4", isDragActive ? "text-gallery-400" : "text-gray-600")} />
        <p className="font-medium text-gray-300 mb-1">
          {isDragActive ? "Drop photos here..." : "Drag & drop photos here"}
        </p>
        <p className="text-sm text-gray-500">
          or click to browse. Supports JPEG, PNG, WebP.
        </p>
        {uploading && (
          <div className="mt-4 flex items-center justify-center gap-2 text-gallery-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Uploading...</span>
          </div>
        )}
      </div>

      {/* Photos grid */}
      {images.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">{images.length} Photos</h2>
            <div className="flex items-center gap-4 text-xs text-gray-500">
              {["pending", "processing", "completed", "failed"].map((s) => (
                <span key={s} className="flex items-center gap-1">
                  {STATUS_ICONS[s]}
                  {images.filter((i: any) => i.processing_status === s).length} {s}
                </span>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            {images.map((img: any) => (
              <div key={img.id} className="relative group rounded-xl overflow-hidden bg-surface-elevated aspect-square">
                {img.thumbnail_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={img.thumbnail_url} alt="" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <ImageIcon className="w-6 h-6 text-gray-600" />
                  </div>
                )}
                {/* Status indicator */}
                <div className="absolute top-2 right-2 w-5 h-5 rounded-full bg-surface/80 flex items-center justify-center">
                  {STATUS_ICONS[img.processing_status]}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

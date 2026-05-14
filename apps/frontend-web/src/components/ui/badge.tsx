import { cn } from "@/lib/utils";
import type { EventStatus } from "@/types";

type BadgeVariant = EventStatus | "owner" | "manager" | "uploader" | string;

const VARIANT_CLASSES: Record<string, string> = {
  active: "badge-active",
  draft: "badge-draft",
  archived: "badge-archived",
  expired: "badge-archived",
  owner: "badge bg-gallery-600/15 text-gallery-400 border border-gallery-600/25",
  manager: "badge bg-violet-500/15 text-violet-400 border border-violet-500/25",
  uploader: "badge bg-emerald-500/15 text-emerald-400 border border-emerald-500/25",
  processing: "badge bg-blue-500/15 text-blue-400 border border-blue-500/25",
  pending: "badge bg-amber-500/15 text-amber-400 border border-amber-500/25",
  completed: "badge-active",
  failed: "badge bg-red-500/15 text-red-400 border border-red-500/25",
};

interface BadgeProps {
  variant: BadgeVariant;
  children?: React.ReactNode;
  className?: string;
}

export function Badge({ variant, children, className }: BadgeProps) {
  return (
    <span className={cn(VARIANT_CLASSES[variant] || "badge bg-gray-500/15 text-gray-400 border border-gray-500/25", className)}>
      {children ?? variant}
    </span>
  );
}

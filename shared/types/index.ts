// ── Shared types across frontend and any cross-app tooling ────────────────

export type AccountType = "studio" | "photographer" | "customer";
export type EventStatus = "draft" | "active" | "archived" | "expired";
export type EventType = "wedding" | "corporate" | "birthday" | "conference" | "sports" | "other";
export type ProcessingStatus = "pending" | "processing" | "completed" | "failed";

export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
  studio: "Studio",
  photographer: "Photographer",
  customer: "Customer",
};

export const EVENT_STATUS_LABELS: Record<EventStatus, string> = {
  draft: "Draft",
  active: "Active",
  archived: "Archived",
  expired: "Expired",
};

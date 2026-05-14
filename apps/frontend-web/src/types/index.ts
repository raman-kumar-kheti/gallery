// ── Enums ──────────────────────────────────────────────────────────────────

export type AccountType = "studio" | "photographer" | "customer";
export type AuthProvider = "google";
export type EventType = "wedding" | "corporate" | "birthday" | "conference" | "sports" | "other";
export type EventStatus = "draft" | "active" | "archived" | "expired";
export type ProcessingStatus = "pending" | "processing" | "completed" | "failed";
export type SubscriptionStatus = "active" | "past_due" | "cancelled" | "trialing";
export type PaymentStatus = "pending" | "captured" | "failed" | "refunded";

// ── Models ─────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  auth_provider: AuthProvider;
  account_type: AccountType | null;
  onboarding_completed: boolean;
  created_at: string;
}

export interface Organization {
  id: string;
  owner_user_id: string;
  name: string;
  slug: string;
  storage_limit_bytes: number;
  storage_used_bytes: number;
  created_at: string;
}

export interface OrganizationMember {
  id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  role: string;
  created_at: string;
}

export interface Event {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  event_type: EventType;
  status: EventStatus;
  image_count: number;
  storage_used_bytes: number;
  faiss_index_path: string | null;
  index_version: number;
  expires_at: string | null;
  created_at: string;
}

export interface Image {
  id: string;
  event_id: string;
  image_url: string;
  thumbnail_url: string | null;
  file_size: number;
  mime_type: string;
  width: number | null;
  height: number | null;
  faiss_pos: number | null;
  processing_status: ProcessingStatus;
  created_at: string;
}

export interface QRCode {
  id: string;
  event_id: string;
  qr_token: string;
  guest_url: string;
  expires_at: string | null;
  created_at: string;
}

export interface SearchSession {
  id: string;
  event_id: string;
  session_token: string;
  matched_image_ids: string[] | null;
  index_version: number;
  expires_at: string;
}

export interface Plan {
  id: string;
  name: string;
  storage_limit_bytes: number;
  event_limit: number | null;
  monthly_price: number;
}

export interface Payment {
  id: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  provider_payment_id: string | null;
  created_at: string;
}

// ── API Response Types ─────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  is_new_user: boolean;
  onboarding_completed: boolean;
  user: Pick<User, "id" | "email" | "name" | "avatar_url" | "account_type">;
}

export interface SearchResult {
  session_token: string;
  from_cache: boolean;
  status: "processing" | "completed";
  images?: Image[];
}

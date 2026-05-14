import { z } from "zod";

export const envSchema = z.object({
  // App
  APP_ENV: z.enum(["development", "staging", "production"]).default("development"),
  APP_URL: z.string().url(),
  API_URL: z.string().url(),

  // Auth
  NEXTAUTH_URL: z.string().url(),
  NEXTAUTH_SECRET: z.string().min(32),

  // Backend API
  NEXT_PUBLIC_API_URL: z.string().url(),

  // Google OAuth
  GOOGLE_CLIENT_ID: z.string(),
  GOOGLE_CLIENT_SECRET: z.string(),
});

export type Env = z.infer<typeof envSchema>;

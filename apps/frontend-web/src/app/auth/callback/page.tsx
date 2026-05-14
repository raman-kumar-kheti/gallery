"use client";

import { useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2, Camera } from "lucide-react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";
import toast from "react-hot-toast";

function CallbackHandler() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuthStore();

  useEffect(() => {
    // The backend redirects with tokens as query params
    // OR we can handle the code here and exchange it with the backend
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    const isNewUser = searchParams.get("is_new_user") === "true";
    const onboardingCompleted = searchParams.get("onboarding_completed") === "true";

    if (!accessToken) {
      toast.error("Authentication failed. Please try again.");
      router.push("/auth/login");
      return;
    }

    // Fetch user profile with the token
    const fetchUser = async () => {
      try {
        // Temporarily set token for the /me call
        localStorage.setItem("access_token", accessToken);
        if (refreshToken) localStorage.setItem("refresh_token", refreshToken);

        const res = await api.get("/auth/me");
        const user = res.data;

        login(user, accessToken, refreshToken || "");

        if (isNewUser || !onboardingCompleted) {
          router.push("/auth/onboarding");
        } else {
          router.push("/dashboard");
        }
      } catch (err) {
        toast.error("Failed to load user profile.");
        router.push("/auth/login");
      }
    };

    fetchUser();
  }, [searchParams, router, login]);

  return (
    <div className="min-h-screen bg-surface flex flex-col items-center justify-center gap-4">
      <div className="w-12 h-12 rounded-xl bg-gallery-600 flex items-center justify-center">
        <Camera className="w-6 h-6 text-white" />
      </div>
      <Loader2 className="w-6 h-6 animate-spin text-gallery-400" />
      <p className="text-gray-400 text-sm">Completing sign in...</p>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-surface flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-gallery-400" />
        </div>
      }
    >
      <CallbackHandler />
    </Suspense>
  );
}

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { User } from "@/types";
import { setAuthTokens, clearAuthTokens } from "@/lib/api";

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;

  login: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      login: (user, accessToken, refreshToken) => {
        setAuthTokens(accessToken, refreshToken);
        set({ user, accessToken, refreshToken, isAuthenticated: true });
      },

      logout: () => {
        clearAuthTokens();
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
        window.location.href = "/auth/login";
      },

      setUser: (user) => set({ user }),
    }),
    {
      name: "gallery-auth",
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

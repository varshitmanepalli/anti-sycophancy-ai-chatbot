import { create } from "zustand";
import { persist } from "zustand/middleware";

import { STORAGE_KEYS } from "@/config";
import { authTokenStore } from "@/lib/api";

import type { AuthUser, UserProfile } from "./types";

interface AuthState {
  user: AuthUser | null;
  profile: UserProfile;
  isAuthenticated: boolean;
  isLoading: boolean;

  setUser: (user: AuthUser | null) => void;
  setProfile: (updates: Partial<UserProfile>) => void;
  setLoading: (loading: boolean) => void;
  login: (user: AuthUser, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  syncFromTokenStore: () => void;
}

const defaultProfile: UserProfile = {
  name: "Alex Morgan",
  email: "alex@example.com",
  avatarUrl: null,
  bio: "Building with honest AI — no sycophancy allowed.",
  joinedAt: "2026-01-15T00:00:00.000Z",
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      profile: defaultProfile,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) =>
        set({
          user,
          isAuthenticated: Boolean(user),
          profile: user
            ? {
                ...get().profile,
                name: user.name,
                email: user.email,
                avatarUrl: user.avatarUrl,
              }
            : get().profile,
        }),

      setProfile: (updates) =>
        set((state) => ({
          profile: { ...state.profile, ...updates },
        })),

      setLoading: (isLoading) => set({ isLoading }),

      login: (user, accessToken, refreshToken) => {
        authTokenStore.set({ accessToken, refreshToken });
        set({
          user,
          isAuthenticated: true,
          profile: {
            ...get().profile,
            name: user.name,
            email: user.email,
            avatarUrl: user.avatarUrl,
          },
        });
      },

      logout: () => {
        authTokenStore.clear();
        set({ user: null, isAuthenticated: false });
      },

      syncFromTokenStore: () => {
        const token = authTokenStore.getAccessToken();
        set({ isAuthenticated: Boolean(token) });
      },
    }),
    {
      name: STORAGE_KEYS.authSession,
      partialize: (state) => ({
        user: state.user,
        profile: state.profile,
        isAuthenticated: state.isAuthenticated,
      }),
      merge: (persisted, current) => {
        const merged = { ...current, ...(persisted as Partial<AuthState>) };
        migrateLegacyUserProfile(merged);
        return merged;
      },
    },
  ),
);

function migrateLegacyUserProfile(state: AuthState): void {
  if (typeof window === "undefined") return;

  const profileDiffersFromDefault =
    state.profile.name !== defaultProfile.name ||
    state.profile.email !== defaultProfile.email ||
    state.profile.bio !== defaultProfile.bio;

  if (profileDiffersFromDefault) return;

  try {
    const raw = localStorage.getItem(STORAGE_KEYS.user);
    if (!raw) return;
    const legacy = JSON.parse(raw) as { profile?: UserProfile };
    if (legacy.profile) state.profile = legacy.profile;
  } catch {
    // ignore
  }
}

export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

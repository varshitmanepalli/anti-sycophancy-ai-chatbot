/** Shared store domain types. */

export interface UserProfile {
  name: string;
  email: string;
  avatarUrl: string | null;
  bio: string;
  joinedAt: string;
}

export interface UserSettings {
  emailNotifications: boolean;
  streamResponses: boolean;
  showConfidence: boolean;
}

export type ThemePreference = "light" | "dark" | "system";

export interface AuthUser {
  id: string;
  email: string;
  name: string;
  avatarUrl: string | null;
}

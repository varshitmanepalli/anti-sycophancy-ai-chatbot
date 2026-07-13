/**
 * @deprecated Use `useAuthStore` for profile and `useSettingsStore` for settings.
 * Kept for backward compatibility during migration.
 */
import { useAuthStore } from "./auth-store";
import { useSettingsStore } from "./settings-store";

export type { UserProfile, UserSettings } from "./types";
export { getInitials } from "./auth-store";

type UserStoreState = {
  profile: ReturnType<typeof useAuthStore.getState>["profile"];
  settings: ReturnType<typeof useSettingsStore.getState>["settings"];
  updateProfile: ReturnType<typeof useAuthStore.getState>["setProfile"];
  updateSettings: ReturnType<typeof useSettingsStore.getState>["updateSettings"];
};

export function useUserStore<T>(selector: (state: UserStoreState) => T): T {
  const profile = useAuthStore((s) => s.profile);
  const setProfile = useAuthStore((s) => s.setProfile);
  const settings = useSettingsStore((s) => s.settings);
  const updateSettings = useSettingsStore((s) => s.updateSettings);

  return selector({
    profile,
    settings,
    updateProfile: setProfile,
    updateSettings,
  });
}

useUserStore.getState = (): UserStoreState => ({
  profile: useAuthStore.getState().profile,
  settings: useSettingsStore.getState().settings,
  updateProfile: useAuthStore.getState().setProfile,
  updateSettings: useSettingsStore.getState().updateSettings,
});

useUserStore.setState = () => {
  console.warn("useUserStore.setState is deprecated; use useAuthStore or useSettingsStore.");
};

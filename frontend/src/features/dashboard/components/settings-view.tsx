"use client";

import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";

import {
  MotionButton,
  MotionCard,
  MotionCardContent,
  MotionCardHeader,
  MotionCardTitle,
  StaggerItem,
  StaggerList,
} from "@/components/motion";
import { Separator } from "@/components/ui/separator";
import { CHAT_MODES } from "@/config";
import { useMounted } from "@/hooks";
import { applyThemePreference } from "@/providers/theme-sync";
import {
  useChatStore,
  useConversationStore,
  useSettingsStore,
  useThemeStore,
} from "@/stores";
import { cn } from "@/utils";

const THEMES = [
  { value: "light", label: "Light", icon: Sun },
  { value: "dark", label: "Dark", icon: Moon },
  { value: "system", label: "System", icon: Monitor },
] as const;

function SettingRow({
  title,
  description,
  children,
}: {
  title: string;
  description: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="space-y-0.5">
        <p className="text-sm font-medium">{title}</p>
        <p className="text-xs text-muted-foreground">{description}</p>
      </div>
      {children}
    </div>
  );
}

function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: (value: boolean) => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={cn(
        "relative inline-flex h-8 w-14 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors touch-manipulation sm:h-6 sm:w-11",
        checked ? "bg-primary" : "bg-muted",
      )}
    >
      <span
        className={cn(
          "pointer-events-none block h-7 w-7 rounded-full bg-background shadow-lg ring-0 transition-transform sm:h-5 sm:w-5",
          checked ? "translate-x-6 sm:translate-x-5" : "translate-x-0",
        )}
      />
    </button>
  );
}

/** Settings page content with appearance and chat preferences. */
export function SettingsView() {
  const mounted = useMounted();
  const { setTheme } = useTheme();
  const chatMode = useChatStore((s) => s.chatMode);
  const setChatMode = useChatStore((s) => s.setChatMode);
  const themePreference = useThemeStore((s) => s.theme);
  const settings = useSettingsStore((s) => s.settings);
  const updateSettings = useSettingsStore((s) => s.updateSettings);
  const clearAllConversations = useConversationStore((s) => s.clearAllConversations);
  const resetSettings = useSettingsStore((s) => s.resetSettings);

  return (
    <div className="flex-1 overflow-y-auto">
      <StaggerList className="mx-auto max-w-3xl space-y-6 p-4 sm:p-6 lg:p-8">
        <StaggerItem>
          <MotionCard>
            <MotionCardHeader>
              <MotionCardTitle className="text-base">Appearance</MotionCardTitle>
            </MotionCardHeader>
            <MotionCardContent>
              <SettingRow
                title="Theme"
                description="Choose light, dark, or match your system preference."
              >
                <div className="flex gap-1 rounded-lg border p-1">
                  {THEMES.map(({ value, label, icon: Icon }) => (
                    <MotionButton
                      key={value}
                      type="button"
                      variant={mounted && themePreference === value ? "secondary" : "ghost"}
                      size="sm"
                      className="h-10 gap-1.5 px-3 sm:h-8"
                      onClick={() => {
                        applyThemePreference(value);
                        setTheme(value);
                      }}
                    >
                      <Icon className="h-3.5 w-3.5" />
                      {label}
                    </MotionButton>
                  ))}
                </div>
              </SettingRow>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>

        <StaggerItem>
          <MotionCard>
            <MotionCardHeader>
              <MotionCardTitle className="text-base">Chat</MotionCardTitle>
            </MotionCardHeader>
            <MotionCardContent className="divide-y">
              <SettingRow
                title="Default mode"
                description="Mode used when starting a new conversation."
              >
                <div className="flex gap-1 rounded-lg border p-1">
                  {CHAT_MODES.map((mode) => (
                    <MotionButton
                      key={mode}
                      type="button"
                      variant={chatMode === mode ? "secondary" : "ghost"}
                      size="sm"
                      className="h-10 capitalize sm:h-8"
                      onClick={() => setChatMode(mode)}
                    >
                      {mode}
                    </MotionButton>
                  ))}
                </div>
              </SettingRow>

              <SettingRow
                title="Stream responses"
                description="Show assistant replies as they are generated."
              >
                <Toggle
                  label="Stream responses"
                  checked={settings.streamResponses}
                  onChange={(v) => updateSettings({ streamResponses: v })}
                />
              </SettingRow>

              <SettingRow
                title="Show confidence scores"
                description="Display confidence badges in reasoning mode."
              >
                <Toggle
                  label="Show confidence scores"
                  checked={settings.showConfidence}
                  onChange={(v) => updateSettings({ showConfidence: v })}
                />
              </SettingRow>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>

        <StaggerItem>
          <MotionCard>
            <MotionCardHeader>
              <MotionCardTitle className="text-base">Notifications</MotionCardTitle>
            </MotionCardHeader>
            <MotionCardContent>
              <SettingRow
                title="Email notifications"
                description="Receive updates about your account and usage."
              >
                <Toggle
                  label="Email notifications"
                  checked={settings.emailNotifications}
                  onChange={(v) => updateSettings({ emailNotifications: v })}
                />
              </SettingRow>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>

        <StaggerItem>
          <MotionCard className="border-destructive/30" hover={false}>
            <MotionCardHeader>
              <MotionCardTitle className="text-base text-destructive">Danger zone</MotionCardTitle>
            </MotionCardHeader>
            <MotionCardContent>
              <SettingRow
                title="Delete all conversations"
                description="Permanently remove all chat history from this device."
              >
                <MotionButton
                  variant="outline"
                  size="sm"
                  className="border-destructive/50 text-destructive hover:bg-destructive/10"
                  onClick={() => {
                    if (confirm("Delete all conversations? This cannot be undone.")) {
                      clearAllConversations();
                    }
                  }}
                >
                  Delete all
                </MotionButton>
              </SettingRow>
              <Separator className="my-2" />
              <SettingRow
                title="Reset settings"
                description="Restore default preferences."
              >
                <MotionButton
                  variant="outline"
                  size="sm"
                  onClick={() => resetSettings()}
                >
                  Reset defaults
                </MotionButton>
              </SettingRow>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>
      </StaggerList>
    </div>
  );
}

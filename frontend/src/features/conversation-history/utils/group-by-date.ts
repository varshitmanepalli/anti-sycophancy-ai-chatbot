import type { Conversation } from "@/types/chat";

export type DateGroupKey =
  | "pinned"
  | "today"
  | "yesterday"
  | "previous_7_days"
  | "previous_30_days"
  | "older";

export interface DateGroup {
  key: DateGroupKey;
  label: string;
  conversations: Conversation[];
}

export const DATE_GROUP_LABELS: Record<DateGroupKey, string> = {
  pinned: "Pinned",
  today: "Today",
  yesterday: "Yesterday",
  previous_7_days: "Previous 7 days",
  previous_30_days: "Previous 30 days",
  older: "Older",
};

const GROUP_ORDER: DateGroupKey[] = [
  "pinned",
  "today",
  "yesterday",
  "previous_7_days",
  "previous_30_days",
  "older",
];

function startOfDay(date: Date): Date {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  return d;
}

function getDateGroupKey(date: Date, now = new Date()): DateGroupKey {
  const today = startOfDay(now);
  const target = startOfDay(date);
  const diffDays = Math.floor((today.getTime() - target.getTime()) / 86400000);

  if (diffDays === 0) return "today";
  if (diffDays === 1) return "yesterday";
  if (diffDays <= 7) return "previous_7_days";
  if (diffDays <= 30) return "previous_30_days";
  return "older";
}

/** Group conversations by pinned status and calendar date. */
export function groupConversationsByDate(conversations: Conversation[]): DateGroup[] {
  const buckets = new Map<DateGroupKey, Conversation[]>();

  for (const key of GROUP_ORDER) {
    buckets.set(key, []);
  }

  for (const conversation of conversations) {
    if (conversation.pinned) {
      buckets.get("pinned")!.push(conversation);
      continue;
    }
    const group = getDateGroupKey(new Date(conversation.updatedAt));
    buckets.get(group)!.push(conversation);
  }

  return GROUP_ORDER.map((key) => ({
    key,
    label: DATE_GROUP_LABELS[key],
    conversations: buckets.get(key) ?? [],
  })).filter((group) => group.conversations.length > 0);
}

/** TanStack Query key factory — prevents typos and enables targeted invalidation. */

export const queryKeys = {
  health: {
    all: ["health"] as const,
    liveness: () => [...queryKeys.health.all, "liveness"] as const,
    readiness: () => [...queryKeys.health.all, "readiness"] as const,
  },
  chat: {
    all: ["chat"] as const,
    conversation: (id: string) => [...queryKeys.chat.all, "conversation", id] as const,
  },
} as const;

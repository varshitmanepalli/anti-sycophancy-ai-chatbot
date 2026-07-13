import { z } from "zod";

export const chatMessageSchema = z.object({
  message: z
    .string()
    .min(1, "Message cannot be empty")
    .max(32000, "Message is too long (max 32,000 characters)"),
});

export type ChatMessageFormValues = z.infer<typeof chatMessageSchema>;

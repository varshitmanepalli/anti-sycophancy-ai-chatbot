"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { AnimatePresence, motion } from "framer-motion";
import { Calendar, Mail, MessageSquare, User } from "lucide-react";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import {
  MotionButton,
  MotionCard,
  MotionCardContent,
  MotionCardHeader,
  MotionCardTitle,
  StaggerItem,
  StaggerList,
} from "@/components/motion";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { FormField } from "@/features/auth/components/form-field";
import { getInitials, useAuthStore, useConversationStore } from "@/stores";
import { cn, formatRelativeTime } from "@/utils";

const profileSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters").max(64),
  email: z.string().email("Enter a valid email"),
  bio: z.string().max(280, "Bio is too long").optional(),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

/** Profile page content. */
export function ProfileView() {
  const profile = useAuthStore((s) => s.profile);
  const updateProfile = useAuthStore((s) => s.setProfile);
  const conversationCount = useConversationStore((s) => Object.keys(s.conversations).length);
  const [saved, setSaved] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isDirty },
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: profile.name,
      email: profile.email,
      bio: profile.bio,
    },
  });

  const onSubmit = (values: ProfileFormValues) => {
    updateProfile(values);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex-1 overflow-y-auto">
      <StaggerList className="mx-auto max-w-3xl space-y-6 p-4 sm:p-6 lg:p-8">
        <StaggerItem>
          <MotionCard hover={false}>
            <MotionCardContent className="flex flex-col items-center gap-4 p-6 sm:flex-row sm:items-start sm:p-8">
              <Avatar className="h-20 w-20">
                <AvatarFallback className="text-lg font-medium">
                  {getInitials(profile.name)}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 text-center sm:text-left">
                <h2 className="text-xl font-semibold">{profile.name}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{profile.email}</p>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{profile.bio}</p>
                <div className="mt-4 flex flex-wrap justify-center gap-4 text-xs text-muted-foreground sm:justify-start">
                  <span className="inline-flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5" />
                    Joined {formatRelativeTime(new Date(profile.joinedAt))}
                  </span>
                  <span className="inline-flex items-center gap-1.5">
                    <MessageSquare className="h-3.5 w-3.5" />
                    {conversationCount} conversation{conversationCount !== 1 ? "s" : ""}
                  </span>
                </div>
              </div>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>

        <StaggerItem>
          <MotionCard>
            <MotionCardHeader>
              <MotionCardTitle className="flex items-center gap-2 text-base">
                <User className="h-4 w-4" />
                Edit profile
              </MotionCardTitle>
            </MotionCardHeader>
            <MotionCardContent>
              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <FormField label="Full name" htmlFor="name" error={errors.name?.message}>
                  <Input
                    id="name"
                    className={cn("h-10", errors.name && "border-destructive")}
                    {...register("name")}
                  />
                </FormField>

                <FormField label="Email" htmlFor="email" error={errors.email?.message}>
                  <Input
                    id="email"
                    type="email"
                    className={cn("h-10", errors.email && "border-destructive")}
                    {...register("email")}
                  />
                </FormField>

                <FormField label="Bio" htmlFor="bio" error={errors.bio?.message}>
                  <Textarea
                    id="bio"
                    rows={3}
                    placeholder="Tell us a bit about yourself…"
                    className={cn(errors.bio && "border-destructive")}
                    {...register("bio")}
                  />
                </FormField>

                <div className="flex items-center gap-3">
                  <MotionButton
                    type="submit"
                    disabled={!isDirty}
                    className="min-h-11 touch-manipulation sm:min-h-9"
                  >
                    Save changes
                  </MotionButton>
                  <AnimatePresence mode="wait">
                    {saved && (
                      <motion.span
                        initial={{ opacity: 0, x: -4 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0 }}
                        className="text-sm text-emerald-600 dark:text-emerald-400"
                      >
                        Saved
                      </motion.span>
                    )}
                  </AnimatePresence>
                </div>
              </form>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>

        <StaggerItem>
          <MotionCard>
            <MotionCardHeader>
              <MotionCardTitle className="flex items-center gap-2 text-base">
                <Mail className="h-4 w-4" />
                Account
              </MotionCardTitle>
            </MotionCardHeader>
            <MotionCardContent className="space-y-3 text-sm text-muted-foreground">
              <p>Password and security settings are managed from the Settings page.</p>
              <p>
                Email verification status:{" "}
                <span className="font-medium text-foreground">Verified</span>
              </p>
            </MotionCardContent>
          </MotionCard>
        </StaggerItem>
      </StaggerList>
    </div>
  );
}

import type { Metadata } from "next";
import { Suspense } from "react";

import { AuthFormSkeleton } from "@/components/feedback";
import { AuthLayout, ResetPasswordForm } from "@/features/auth";

export const metadata: Metadata = {
  title: "Reset password",
};

function ResetPasswordFallback() {
  return (
    <div className="rounded-xl border p-6 sm:p-8">
      <AuthFormSkeleton fields={3} />
    </div>
  );
}

/** Reset password page — expects ?token= from email link. */
export default function ResetPasswordPage() {
  return (
    <AuthLayout title="Reset password" subtitle="Choose a new password for your account">
      <Suspense fallback={<ResetPasswordFallback />}>
        <ResetPasswordForm />
      </Suspense>
    </AuthLayout>
  );
}

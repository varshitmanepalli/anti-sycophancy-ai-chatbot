import type { Metadata } from "next";
import { Suspense } from "react";

import { OtpFormSkeleton } from "@/components/feedback";
import { AuthLayout, OtpForm } from "@/features/auth";

export const metadata: Metadata = {
  title: "Verify email",
};

function OtpFallback() {
  return (
    <div className="rounded-xl border p-6 sm:p-8">
      <OtpFormSkeleton />
    </div>
  );
}

/** OTP verification page — expects ?email= from signup flow. */
export default function VerifyOtpPage() {
  return (
    <AuthLayout title="Verify your email" subtitle="Enter the 6-digit code we sent you">
      <Suspense fallback={<OtpFallback />}>
        <OtpForm />
      </Suspense>
    </AuthLayout>
  );
}

import type { Metadata } from "next";

import { AuthLayout, SignupForm } from "@/features/auth";

export const metadata: Metadata = {
  title: "Sign up",
};

/** Signup page. */
export default function SignupPage() {
  return (
    <AuthLayout title="Create an account" subtitle="Start getting honest, reasoned answers">
      <SignupForm />
    </AuthLayout>
  );
}

import type { Metadata } from "next";

import { AuthLayout, LoginForm } from "@/features/auth";

export const metadata: Metadata = {
  title: "Sign in",
};

/** Login page. */
export default function LoginPage() {
  return (
    <AuthLayout title="Welcome back" subtitle="Sign in to continue to Reasoning Engine">
      <LoginForm />
    </AuthLayout>
  );
}

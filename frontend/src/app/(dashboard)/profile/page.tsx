import type { Metadata } from "next";

import { ProfileView } from "@/features/dashboard";

export const metadata: Metadata = {
  title: "Profile",
};

/** User profile page. */
export default function ProfilePage() {
  return <ProfileView />;
}

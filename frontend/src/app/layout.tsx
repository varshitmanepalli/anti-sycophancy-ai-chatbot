import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Anti-Sycophancy Chatbot",
  description: "An AI assistant that prioritizes honesty over flattery.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

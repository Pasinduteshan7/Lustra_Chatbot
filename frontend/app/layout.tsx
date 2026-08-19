import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Lustra - Beauty Assistant",
  description: "Your personalized beauty and skincare assistant",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

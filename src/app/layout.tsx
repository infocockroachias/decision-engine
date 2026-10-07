import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UPSC Test Analysis | Decision Engine",
  description: "UPSC Prelims test analysis platform with detailed mistake analysis and personalized recommendations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50">{children}</body>
    </html>
  );
}
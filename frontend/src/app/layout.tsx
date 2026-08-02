import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "ShellGuard AI — Safe Linux Command Execution Engine",
  description: "OS-Native Explainable AI Intent Engine & Safety Layer for Linux Shell",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0b0f19] text-gray-100 min-h-screen">
        {children}
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "enterprise ai agent",
  description: "night console platform coordinating langgraph, chroma, deterministic tools, and persistent memory",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 p-3 md:p-6">
          {children}
        </main>
        <footer className="text-center py-5 text-xs text-[var(--color-muted)] border-t border-[var(--color-rule)] bg-[var(--color-paper-2)]">
          enterprise ai agent &bull; 8-node state machine &bull; verified telemetry
        </footer>
      </body>
    </html>
  );
}

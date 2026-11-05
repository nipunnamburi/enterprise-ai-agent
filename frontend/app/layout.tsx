import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "agent@enterprise: ~ · terminal",
  description: "terminal surface coordinating langgraph state machine, chroma vector store, deterministic ast tools, and persistent memory",
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
          href="https://fonts.googleapis.com/css2?family=Martian+Mono:wdth,wght@75..112.5,400..700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen flex flex-col antialiased bg-[var(--color-paper)] text-[var(--color-ink)]">
        <Navbar />
        <main className="flex-1 p-3 md:p-6">
          {children}
        </main>
        <footer className="py-3 px-4 md:px-8 text-xs text-[var(--color-muted)] border-t border-[var(--color-rule)] bg-[var(--color-paper-2)] flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="text-[var(--color-accent)] font-bold">[0:agent-core]</span>
            <span className="text-[var(--color-rule-2)]">|</span>
            <span>langgraph 0.0.30</span>
            <span className="text-[var(--color-rule-2)]">|</span>
            <span>tty: /dev/pts/1</span>
          </div>
          <div className="flex items-center gap-3">
            <span>status: 0 (ok)</span>
            <span className="text-[var(--color-rule-2)]">|</span>
            <span className="text-[var(--color-ink-2)]">theme: terminal</span>
          </div>
        </footer>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";

export const metadata: Metadata = {
  title: "Enterprise AI Research & Automation Agent",
  description: "Production Agentic AI Platform with LangGraph, RAG, Chroma, Tool Calling, and Persistent Memory",
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
          href="https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@600&family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 p-3 md:p-6">
          {children}
        </main>
        <footer className="text-center py-4 text-xs font-medium text-[var(--color-muted)] border-t border-[var(--color-rule-2)] bg-[var(--color-paper-2)]">
          ENTERPRISE AI RESEARCH &amp; AUTOMATION &bull; DWG SPEC 01 &bull; LANGGRAPH STATE MACHINE
        </footer>
      </body>
    </html>
  );
}

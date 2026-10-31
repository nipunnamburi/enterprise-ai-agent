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
      <body className="min-h-screen flex flex-col font-sans text-slate-800 antialiased">
        <Navbar />
        <main className="flex-1 p-4 md:p-6">
          {children}
        </main>
        <footer className="text-center py-4 text-xs font-semibold text-slate-500 border-t border-slate-300 bg-white/60">
          Enterprise AI Research & Automation Agent &bull; Department of AI Engineering &bull; 2026
        </footer>
      </body>
    </html>
  );
}

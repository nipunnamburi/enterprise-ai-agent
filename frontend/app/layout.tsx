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
      <body className="min-h-screen flex flex-col font-sans text-slate-100 antialiased bg-[#080c14]">
        <Navbar />
        <main className="flex-1 p-3 md:p-6">
          {children}
        </main>
        <footer className="text-center py-4 text-xs font-semibold text-slate-500 border-t border-slate-800/80 bg-slate-950/40 backdrop-blur-md">
          Enterprise AI Research & Automation Agent &bull; Powered by LangGraph, Chroma &amp; Elysia &bull; 2026
        </footer>
      </body>
    </html>
  );
}

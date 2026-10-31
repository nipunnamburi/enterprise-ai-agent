"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, ExternalLink, Sparkles, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { name: "Dashboard", href: "/" },
  { name: "Agent Chat & Workspace", href: "/chat" },
  { name: "Elysia Decision Tree", href: "/elysia" },
  { name: "Knowledge Base (RAG)", href: "/documents" },
  { name: "Memory Records", href: "/memory" },
  { name: "Tool Activity & Logs", href: "/tools" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="w-full bg-[#0b0f19]/80 backdrop-blur-md border-b border-slate-800/80 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Title / Brand */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 text-white flex items-center justify-center font-bold text-sm shadow-glow-emerald">
            <Sparkles className="w-5 h-5 text-emerald-100" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <Link href="/" className="font-extrabold text-white text-sm hover:text-emerald-400 transition-colors">
                Enterprise AI Agent
              </Link>
              <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Live 24x7
              </span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">LangGraph &bull; Chroma RAG &bull; Elysia Tree &bull; MCP &bull; PostgreSQL</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex flex-wrap items-center gap-1.5 text-xs font-semibold">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "px-3 py-1.5 rounded-lg transition-all",
                  isActive
                    ? "bg-slate-800 text-emerald-400 border border-slate-700 shadow-sm font-bold"
                    : "text-slate-400 hover:bg-slate-800/60 hover:text-white"
                )}
              >
                {link.name}
              </Link>
            );
          })}
          
          <div className="h-4 w-[1px] bg-slate-800 mx-1 hidden sm:block" />

          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-2.5 py-1.5 rounded-lg bg-slate-900 text-slate-300 hover:bg-slate-800 hover:text-white transition-all flex items-center gap-1 border border-slate-800 text-[11px]"
          >
            <span>FastAPI</span>
            <ExternalLink className="h-3 w-3 text-slate-500" />
          </a>
          <a
            href="http://127.0.0.1:8000/elysia"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 text-white hover:from-emerald-500 hover:to-teal-500 transition-all flex items-center gap-1.5 font-bold shadow-glow-emerald text-[11px]"
            title="Launch Mounted Elysia AI Studio"
          >
            <Sparkles className="h-3 w-3 text-amber-300" />
            <span>Elysia Studio</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </nav>
      </div>
    </header>
  );
}

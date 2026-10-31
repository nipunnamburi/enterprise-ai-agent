"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, ExternalLink } from "lucide-react";
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
    <header className="w-full bg-white border-b border-slate-300 shadow-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Title / Brand */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#1e3a8a] text-white flex items-center justify-center font-bold text-sm">
            AI
          </div>
          <div>
            <Link href="/" className="font-bold text-[#1e3a8a] text-base hover:text-[#16a34a] transition-colors">
              Enterprise AI Research & Automation Agent
            </Link>
            <p className="text-[11px] text-slate-500 font-medium">LangGraph &bull; RAG &bull; Tool Calling &bull; Memory &bull; PostgreSQL</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex flex-wrap items-center gap-1.5 text-xs font-bold">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "px-3 py-1.5 rounded-md transition-all",
                  isActive
                    ? "bg-[#1e3a8a] text-white"
                    : "text-slate-700 hover:bg-slate-100 hover:text-[#1e3a8a]"
                )}
              >
                {link.name}
              </Link>
            );
          })}
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 rounded-md bg-slate-100 text-slate-700 hover:bg-[#16a34a] hover:text-white transition-all flex items-center gap-1 border border-slate-200"
          >
            <span>FastAPI Docs</span>
            <ExternalLink className="h-3 w-3" />
          </a>
          <a
            href="http://127.0.0.1:8000/elysia"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 rounded-md bg-emerald-50 text-emerald-800 hover:bg-emerald-600 hover:text-white transition-all flex items-center gap-1 border border-emerald-300 font-bold"
            title="Launch Mounted Elysia AI Studio"
          >
            <span>Elysia Studio</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </nav>
      </div>
    </header>
  );
}

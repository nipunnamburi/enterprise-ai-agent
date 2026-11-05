"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, ExternalLink, Sparkles, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { name: "Dashboard", href: "/" },
  { name: "Agent Chat & Workspace", href: "/chat" },
  { name: "Knowledge Base (RAG)", href: "/documents" },
  { name: "Memory Records", href: "/memory" },
  { name: "Tool Activity & Logs", href: "/tools" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="w-full bg-[var(--color-paper-2)] border-b border-[var(--color-rule)] sticky top-0 z-50">
      <div className="max-w-[1140px] mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3 font-mono">
        {/* Title / Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-[var(--color-ink)] text-[var(--color-accent-ink)] flex items-center justify-center font-bold text-xs border border-[var(--color-rule)]">
            AI
          </div>
          <div>
            <div className="flex items-center gap-2">
              <Link href="/" className="font-semibold text-[var(--color-ink)] text-sm tracking-tight hover:underline">
                ENTERPRISE AI AGENT
              </Link>
              <span className="inline-flex items-center gap-1 px-1.5 py-0.2 text-[10px] border border-[var(--color-rule)] text-[var(--color-ink)]">
                SPEC 2.4 &bull; LIVE
              </span>
            </div>
            <p className="text-[11px] text-[var(--color-muted)] font-normal">LANGGRAPH &bull; CHROMA RAG &bull; MCP &bull; POSTGRES</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex flex-wrap items-center gap-1 text-xs">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "px-2.5 py-1 transition-all border",
                  isActive
                    ? "bg-[var(--color-paper-3)] text-[var(--color-ink)] border-[var(--color-ink)] font-semibold"
                    : "text-[var(--color-muted)] border-transparent hover:border-[var(--color-rule-2)] hover:text-[var(--color-ink)]"
                )}
              >
                {link.name}
              </Link>
            );
          })}
          
          <div className="h-4 w-[1px] bg-[var(--color-rule-2)] mx-1 hidden sm:block" />

          <a
            href="https://enterprise-ai-agent-k2h9.onrender.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-2 py-1 bg-[var(--color-paper)] text-[var(--color-ink)] border border-[var(--color-rule)] hover:bg-[var(--color-paper-3)] transition-all flex items-center gap-1 text-[11px]"
          >
            <span>FASTAPI DOCS</span>
            <ExternalLink className="h-3 w-3" />
          </a>
        </nav>
      </div>
    </header>
  );
}

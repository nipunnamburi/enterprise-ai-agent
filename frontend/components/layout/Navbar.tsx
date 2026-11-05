"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_LINKS = [
  { name: "dashboard", href: "/" },
  { name: "agent chat", href: "/chat" },
  { name: "knowledge base", href: "/documents" },
  { name: "memory", href: "/memory" },
  { name: "tools & logs", href: "/tools" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="w-full bg-[var(--color-paper-2)] border-b border-[var(--color-rule)] sticky top-0 z-50">
      <div className="max-w-[1100px] mx-auto px-4 py-3 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        {/* Title / Brand */}
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-[var(--radius-card)] bg-[var(--color-accent)] text-[var(--color-accent-ink)] flex items-center justify-center font-serif text-sm">
            l
          </div>
          <div>
            <div className="flex items-center gap-2">
              <Link href="/" className="font-serif text-lg text-[var(--color-ink)] hover:text-[var(--color-accent)] transition-colors">
                enterprise ai agent
              </Link>
              <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-[var(--radius-pill)] text-[11px] border border-[var(--color-rule)] text-[var(--color-ink-2)]">
                <span className="w-1.5 h-1.5 rounded-full bg-[var(--color-live)]" />
                online
              </span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex flex-wrap items-center gap-1.5 text-xs">
          {NAV_LINKS.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.name}
                href={link.href}
                className={cn(
                  "px-3 py-1.5 rounded-[var(--radius-pill)] transition-all",
                  isActive
                    ? "bg-[var(--color-paper-3)] text-[var(--color-ink)] font-medium"
                    : "text-[var(--color-muted)] hover:bg-[var(--color-paper)] hover:text-[var(--color-ink)]"
                )}
              >
                {link.name}
              </Link>
            );
          })}
          
          <div className="h-4 w-[1px] bg-[var(--color-rule)] mx-1 hidden sm:block" />

          <a
            href="https://enterprise-ai-agent-k2h9.onrender.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-3 py-1.5 rounded-[var(--radius-pill)] bg-[var(--color-paper)] text-[var(--color-ink-2)] border border-[var(--color-rule)] hover:border-[var(--color-rule-2)] transition-all flex items-center gap-1 text-[11px]"
          >
            <span>fastapi</span>
            <ExternalLink className="h-3 w-3 text-[var(--color-muted)]" />
          </a>
        </nav>
      </div>
    </header>
  );
}

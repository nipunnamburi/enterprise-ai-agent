"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_WINDOWS = [
  { id: 1, name: "dash", href: "/" },
  { id: 2, name: "chat", href: "/chat" },
  { id: 3, name: "docs", href: "/documents" },
  { id: 4, name: "memory", href: "/memory" },
  { id: 5, name: "tools", href: "/tools" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="w-full bg-[var(--color-paper-2)] border-b border-[var(--color-rule)] sticky top-0 z-50 text-xs">
      <div className="max-w-[1280px] mx-auto px-3 md:px-6 flex items-stretch justify-between min-h-[48px]">
        {/* Left: Multiplexer Session + Windows */}
        <div className="flex items-stretch overflow-x-auto scrollbar-none">
          {/* Session Name Badge */}
          <Link
            href="/"
            className="flex items-center px-3 py-2 bg-[var(--color-accent)] text-[var(--color-accent-ink)] font-bold tracking-tight text-xs flex-shrink-0 hover:opacity-90 transition-opacity"
          >
            [AGENT]
          </Link>

          {/* Numbered Windows */}
          <nav className="flex items-stretch flex-shrink-0" aria-label="Multiplexer windows">
            {NAV_WINDOWS.map((win) => {
              const isActive = pathname === win.href;
              return (
                <Link
                  key={win.id}
                  href={win.href}
                  className={cn(
                    "flex items-center px-3 py-2 text-xs border-r border-[var(--color-rule)] transition-colors whitespace-nowrap",
                    isActive
                      ? "bg-[var(--color-paper-3)] text-[var(--color-ink)] font-semibold shadow-[inset_0_-2px_0_var(--color-accent)]"
                      : "text-[var(--color-ink-2)] hover:bg-[var(--color-paper-3)] hover:text-[var(--color-ink)]"
                  )}
                >
                  <span className="text-[var(--color-muted)] mr-1">{win.id}:</span>
                  <span>{win.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Right: Telemetry Meta & External Documentation */}
        <div className="flex items-center gap-3 pl-2 flex-shrink-0">
          <div className="hidden sm:flex items-center gap-2 text-[var(--color-muted)] text-[11px]">
            <span className="w-1.5 h-1.5 bg-[var(--color-accent)]" />
            <span>sys:up</span>
            <span className="text-[var(--color-rule-2)]">|</span>
            <span className="text-[var(--color-ink-2)]">0.05s</span>
          </div>

          <div className="h-4 w-[1px] bg-[var(--color-rule)] hidden sm:block" />

          <a
            href="https://enterprise-ai-agent-k2h9.onrender.com/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] text-[var(--color-ink-2)] border border-[var(--color-rule-2)] hover:border-[var(--color-accent)] hover:text-[var(--color-accent)] transition-colors"
          >
            <span>fastapi</span>
            <ExternalLink className="h-3 w-3 text-[var(--color-muted)]" />
          </a>
        </div>
      </div>
    </header>
  );
}

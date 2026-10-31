"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  MessageSquareCode,
  FileText,
  Brain,
  Wrench,
  Layers,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  {
    name: "Dashboard",
    href: "/",
    icon: LayoutDashboard,
    description: "System KPIs & metrics",
  },
  {
    name: "Agent Workspace",
    href: "/chat",
    icon: MessageSquareCode,
    description: "LangGraph execution & chat",
    badge: "5 Demos",
  },
  {
    name: "Knowledge Base",
    href: "/documents",
    icon: FileText,
    description: "RAG vector ingestion",
  },
  {
    name: "Agent Memory",
    href: "/memory",
    icon: Brain,
    description: "Persistent user context",
  },
  {
    name: "Tool Activity",
    href: "/tools",
    icon: Wrench,
    description: "Audit trail & runner",
  },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 border-r border-slate-200/80 bg-white/80 backdrop-blur-sm flex flex-col justify-between p-4 min-h-[calc(100vh-4rem)] shadow-sm">
      <div className="space-y-6">
        <div>
          <p className="px-3 text-[11px] font-bold tracking-wider text-slate-500 uppercase">
            Platform Capabilities
          </p>
          <nav className="mt-3 space-y-1.5">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    "flex items-center justify-between rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all group",
                    isActive
                      ? "bg-[#1e3a8a] text-white shadow-md"
                      : "text-slate-700 hover:bg-slate-100 hover:text-[#1e3a8a]"
                  )}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      className={cn(
                        "h-4 w-4 transition-colors",
                        isActive ? "text-white" : "text-slate-500 group-hover:text-[#1e3a8a]"
                      )}
                    />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span className={cn(
                      "rounded-md px-2 py-0.5 text-[10px] font-bold",
                      isActive ? "bg-white/20 text-white" : "bg-blue-100 text-[#1e3a8a]"
                    )}>
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Architecture Specs Card */}
        <div className="rounded-xl bg-slate-50 p-4 space-y-2 border border-slate-200">
          <div className="flex items-center gap-2 text-xs font-bold text-[#1e3a8a]">
            <Layers className="h-4 w-4" />
            <span>Agent Architecture</span>
          </div>
          <div className="space-y-1.5 text-xs text-slate-600 font-medium">
            <div className="flex justify-between">
              <span>Graph Nodes:</span>
              <span className="text-slate-900 font-bold">8 Nodes</span>
            </div>
            <div className="flex justify-between">
              <span>Vector Store:</span>
              <span className="text-emerald-700 font-bold">Chroma HNSW</span>
            </div>
            <div className="flex justify-between">
              <span>Database:</span>
              <span className="text-blue-800 font-bold">PostgreSQL/SQLite</span>
            </div>
            <div className="flex justify-between">
              <span>Tools Registered:</span>
              <span className="text-amber-700 font-bold">6 Tools</span>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-200 pt-4">
        <div className="flex items-center gap-3 px-2">
          <div className="h-9 w-9 rounded-full bg-[#1e3a8a] flex items-center justify-center text-xs font-bold text-white shadow-sm">
            AM
          </div>
          <div className="truncate">
            <p className="text-xs font-bold text-slate-800 truncate">Alex Mercer</p>
            <p className="text-[11px] text-slate-500 truncate">analyst@enterprise.ai</p>
          </div>
        </div>
      </div>
    </aside>
  );
}

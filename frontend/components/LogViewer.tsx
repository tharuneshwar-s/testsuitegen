"use client";

import { useState, useEffect, useRef } from "react";
import {
  Terminal,
  Filter,
  ChevronDown,
  ChevronUp,
  AlertCircle,
  Info,
  Bug,
} from "lucide-react";

interface LogEntry {
  message: string;
  log_type: "info" | "debug" | "error";
  created_at: string;
}

interface LogViewerProps {
  logs: LogEntry[];
  isLive?: boolean;
}

export default function LogViewer({ logs, isLive = false }: LogViewerProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [filters, setFilters] = useState<Record<string, boolean>>({
    info: true,
    debug: true,
    error: true,
  });
  const [autoScroll, setAutoScroll] = useState(true);
  const logsEndRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs, autoScroll]);

  const toggleFilter = (type: string) => {
    setFilters((prev) => ({ ...prev, [type]: !prev[type] }));
  };

  const filteredLogs = logs.filter((log) => filters[log.log_type]);

  const getLogIcon = (type: string) => {
    switch (type) {
      case "error":
        return <AlertCircle className="w-3.5 h-3.5 text-rose-600" />;
      case "debug":
        return <Bug className="w-3.5 h-3.5 text-amber-600" />;
      default:
        return <Info className="w-3.5 h-3.5 text-sky-600" />;
    }
  };

  const getLogBadgeClass = (type: string) => {
    switch (type) {
      case "error":
        return "bg-rose-100 text-rose-800 border-rose-200";
      case "debug":
        return "bg-amber-100 text-amber-800 border-amber-200";
      default:
        return "bg-sky-100 text-sky-800 border-sky-200";
    }
  };

  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return "";
    }
  };

  const logCounts = {
    info: logs.filter((l) => l.log_type === "info").length,
    debug: logs.filter((l) => l.log_type === "debug").length,
    error: logs.filter((l) => l.log_type === "error").length,
  };

  return (
    <div className="bg-white rounded-lg border border-stone-300 shadow-sm mb-4 overflow-hidden">
      {/* Header */}
      <div
        className="flex items-center justify-between px-4 py-3 bg-stone-100 border-b border-stone-300 cursor-pointer hover:bg-stone-150"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-800" />
          <h3 className="text-sm font-semibold text-stone-800">
            Pipeline Logs
          </h3>
          {isLive && (
            <span className="flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-emerald-100 text-emerald-800 rounded-full">
              <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
              Live
            </span>
          )}
          <span className="text-xs text-stone-500">
            {filteredLogs.length} of {logs.length} entries
          </span>
        </div>
        <div className="flex items-center gap-2">
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-stone-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-stone-500" />
          )}
        </div>
      </div>

      {isExpanded && (
        <>
          {/* Filter Bar */}
          <div className="flex items-center gap-2 px-4 py-2 bg-stone-50 border-b border-stone-200">
            <Filter className="w-3.5 h-3.5 text-stone-500" />
            <span className="text-xs text-stone-600">Filter:</span>
            <div className="flex gap-1.5">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFilter("info");
                }}
                className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                  filters.info
                    ? "bg-sky-100 text-sky-800 border-sky-300"
                    : "bg-stone-100 text-stone-500 border-stone-300"
                }`}
              >
                <Info className="w-3 h-3" />
                Info ({logCounts.info})
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFilter("debug");
                }}
                className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                  filters.debug
                    ? "bg-amber-100 text-amber-800 border-amber-300"
                    : "bg-stone-100 text-stone-500 border-stone-300"
                }`}
              >
                <Bug className="w-3 h-3" />
                Debug ({logCounts.debug})
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFilter("error");
                }}
                className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                  filters.error
                    ? "bg-rose-100 text-rose-800 border-rose-300"
                    : "bg-stone-100 text-stone-500 border-stone-300"
                }`}
              >
                <AlertCircle className="w-3 h-3" />
                Error ({logCounts.error})
              </button>
            </div>
            <div className="ml-auto">
              <label className="flex items-center gap-1.5 text-xs text-stone-600 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoScroll}
                  onChange={(e) => setAutoScroll(e.target.checked)}
                  className="rounded border-stone-300 text-emerald-600 focus:ring-emerald-500"
                />
                Auto-scroll
              </label>
            </div>
          </div>

          {/* Logs Container */}
          <div
            ref={containerRef}
            className="max-h-64 overflow-y-auto bg-stone-900 font-mono text-xs"
          >
            {filteredLogs.length === 0 ? (
              <div className="p-4 text-center text-stone-500">
                No logs to display
              </div>
            ) : (
              <div className="divide-y divide-stone-800">
                {filteredLogs.map((log, idx) => (
                  <div
                    key={idx}
                    className={`flex items-start gap-2 px-3 py-1.5 hover:bg-stone-800 ${
                      log.log_type === "error" ? "bg-rose-950/30" : ""
                    }`}
                  >
                    <span className="text-stone-500 shrink-0 w-16">
                      {formatTime(log.created_at)}
                    </span>
                    <span
                      className={`shrink-0 px-1.5 py-0.5 text-[10px] font-semibold rounded uppercase border ${getLogBadgeClass(
                        log.log_type,
                      )}`}
                    >
                      {log.log_type}
                    </span>
                    <span
                      className={`flex-1 break-all ${
                        log.log_type === "error"
                          ? "text-rose-400"
                          : log.log_type === "debug"
                            ? "text-amber-300"
                            : "text-stone-200"
                      }`}
                    >
                      {log.message}
                    </span>
                  </div>
                ))}
              </div>
            )}
            <div ref={logsEndRef} />
          </div>
        </>
      )}
    </div>
  );
}

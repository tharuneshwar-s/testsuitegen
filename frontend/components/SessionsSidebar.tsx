import { Terminal, X, Sparkles, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { deleteJob } from "@/lib/api";

interface SessionRecord {
  jobId: string;
  timestamp: number;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
}

interface SessionsSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  sessions: SessionRecord[];
  currentJobId: string | null;
  onSelectSession: (jobId: string) => void;
  onNewSession: () => void;
  onDeleteSession?: (jobId: string) => void;
}

export default function SessionsSidebar({
  isOpen,
  onClose,
  sessions,
  currentJobId,
  onSelectSession,
  onNewSession,
  onDeleteSession,
}: SessionsSidebarProps) {
  const router = useRouter();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDeleteSession = async (jobId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (
      !confirm(
        "Are you sure you want to delete this session? This cannot be undone.",
      )
    )
      return;

    setDeletingId(jobId);
    try {
      await deleteJob(jobId);
      onDeleteSession?.(jobId);
    } catch (error) {
      console.error("Failed to delete session:", error);
      alert("Failed to delete session");
    } finally {
      setDeletingId(null);
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black/30 z-40" onClick={onClose} />

      {/* Sidebar Panel */}
      <div className="fixed left-0 top-0 h-full w-80 bg-stone-50 shadow-2xl z-50 flex flex-col border-r border-stone-300">
        {/* Sidebar Header */}
        <div className="p-4 border-b border-stone-300 bg-stone-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-emerald-800" />
            <h3 className="text-sm font-semibold text-stone-800">Sessions</h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-stone-200 rounded-lg transition-colors"
            title="Close sidebar"
          >
            <X className="w-4 h-4 text-stone-600" />
          </button>
        </div>

        {/* New Session Button */}
        <div className="p-4 border-b border-stone-300">
          <button
            onClick={onNewSession}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 text-sm font-medium text-white bg-gradient-to-r from-emerald-800 to-emerald-900 hover:from-emerald-900 hover:to-emerald-950 rounded-lg transition-all shadow-lg shadow-emerald-900/20"
          >
            <Sparkles className="w-4 h-4" />
            New Session
          </button>
        </div>

        {/* Sessions List */}
        <div className="flex-1 overflow-y-auto p-4">
          {sessions.length === 0 ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-stone-200 rounded-full mb-3">
                <Terminal className="w-6 h-6 text-stone-500" />
              </div>
              <p className="text-sm text-stone-600">No sessions yet</p>
              <p className="text-xs text-stone-500 mt-1">
                Start generating tests to create sessions
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((session) => {
                const statusColors = {
                  pending: "bg-stone-200 text-stone-700",
                  running: "bg-sky-100 text-sky-800 animate-pulse",
                  completed: "bg-emerald-100 text-emerald-800",
                  failed: "bg-rose-100 text-rose-800",
                };
                const statusLabels = {
                  pending: "Pending",
                  running: "Running",
                  completed: "Completed",
                  failed: "Failed",
                };
                return (
                  <div
                    key={session.jobId}
                    className={`p-3 rounded-lg transition-all ${
                      currentJobId === session.jobId
                        ? "bg-emerald-50 border-2 border-emerald-400 shadow-sm"
                        : "hover:bg-stone-100 border-2 border-stone-300 hover:border-stone-400"
                    }`}
                  >
                    <button
                      onClick={() => {
                        onSelectSession(session.jobId);
                        router.push(`?jobId=${session.jobId}`);
                        onClose();
                      }}
                      className="w-full text-left"
                    >
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <div className="flex-1 min-w-0">
                          <code className="text-xs font-mono text-stone-700 truncate block">
                            {session.jobId.slice(0, 8)}-
                            {session.jobId.slice(9, 13)}
                          </code>
                          <p className="text-xs text-stone-500 mt-1">
                            {new Date(session.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <span
                          className={`text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ${statusColors[session.status]}`}
                        >
                          {statusLabels[session.status]}
                        </span>
                      </div>
                      {/* Progress Bar */}
                      <div className="w-full bg-stone-200 rounded-full h-1.5">
                        <div
                          className={`h-1.5 rounded-full transition-all ${
                            session.status === "completed"
                              ? "bg-emerald-600"
                              : session.status === "failed"
                                ? "bg-rose-600"
                                : "bg-sky-600"
                          }`}
                          style={{ width: `${session.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-stone-600 mt-1 font-medium">
                        {session.progress}% complete
                      </p>
                    </button>
                    {/* Delete Button */}
                    <button
                      onClick={(e) => handleDeleteSession(session.jobId, e)}
                      disabled={deletingId === session.jobId}
                      className="mt-2 w-full flex items-center justify-center gap-2 px-2 py-1.5 text-xs font-medium text-rose-700 hover:text-rose-800 bg-rose-50 hover:bg-rose-100 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg transition-colors"
                      title="Delete this session"
                    >
                      <Trash2 className="w-3 h-3" />
                      {deletingId === session.jobId ? "Deleting..." : "Delete"}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </>
  );
}

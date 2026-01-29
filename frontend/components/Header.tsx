import { Terminal, Menu, X } from "lucide-react";

interface HeaderProps {
  sidebarOpen: boolean;
  onToggleSidebar: () => void;
}

export default function Header({ sidebarOpen, onToggleSidebar }: HeaderProps) {
  return (
    <header className="bg-stone-50 border-b border-stone-300 shrink-0">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={onToggleSidebar}
              className="p-2 hover:bg-stone-200 rounded-lg transition-colors"
              title="Toggle sessions sidebar"
            >
              {sidebarOpen ? (
                <X className="w-5 h-5 text-stone-700" />
              ) : (
                <Menu className="w-5 h-5 text-stone-700" />
              )}
            </button>
            <div className="bg-gradient-to-br from-emerald-800 to-emerald-900 p-2 rounded-xl shadow-lg shadow-emerald-900/20">
              <Terminal className="w-5 h-5 text-emerald-50" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-stone-900">TestGen AI</h1>
              <p className="text-xs text-stone-500">
                Intelligent Test Suite Generator
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

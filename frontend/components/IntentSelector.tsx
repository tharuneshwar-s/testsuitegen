"use client";

import { useState } from "react";
import { createPortal } from "react-dom";
import { CheckCircle2, Circle } from "lucide-react";

interface Intent {
  id: string;
  label: string;
  category: string;
  description: string;
}

interface IntentSelectorProps {
  intents: Intent[];
  selectedIntents: string[];
  onToggle: (intentId: string) => void;
  categories: Record<string, { label: string; color: string }>;
}

export default function IntentSelector({
  intents,
  selectedIntents,
  onToggle,
  categories,
}: IntentSelectorProps) {
  const [hoveredIntent, setHoveredIntent] = useState<Intent | null>(null);
  const [coords, setCoords] = useState<{ top: number; left: number } | null>(
    null,
  );

  // Group intents by category (compact-only view)
  const groupedIntents = intents.reduce(
    (acc, intent) => {
      if (!acc[intent.category]) acc[intent.category] = [];
      acc[intent.category].push(intent);
      return acc;
    },
    {} as Record<string, Intent[]>,
  );

  const isSelected = (id: string) => selectedIntents.includes(id);

  const handleMouseEnter = (intent: Intent, e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setCoords({
      top: rect.top,
      left: rect.left + rect.width / 2,
    });
    setHoveredIntent(intent);
  };

  const handleMouseLeave = () => {
    setHoveredIntent(null);
    setCoords(null);
  };

  return (
    <div className="space-y-3 w-full">
      <div className="flex items-center justify-between mb-2">
        <div>
          <div className="text-xs text-stone-500">Tap chips to toggle</div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() =>
              intents.forEach((i) => !isSelected(i.id) && onToggle(i.id))
            }
            className="text-xs px-2 py-1 rounded bg-emerald-100 text-emerald-800 hover:bg-emerald-200 font-medium"
          >
            Select All
          </button>
          <button
            onClick={() => selectedIntents.forEach((id) => onToggle(id))}
            className="text-xs px-2 py-1 rounded bg-stone-200 text-stone-700 hover:bg-stone-300 font-medium"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid gap-3">
        {Object.entries(groupedIntents).map(([category, categoryIntents]) => {
          const catInfo = categories[category];
          return (
            <div key={category}>
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-2 h-2 rounded-full bg-${catInfo.color}-600`}
                />
                <h4 className="text-xs font-medium text-stone-600 uppercase tracking-wide">
                  {catInfo.label}
                </h4>
              </div>
              <div className="flex gap-2 flex-wrap">
                {categoryIntents.map((intent) => {
                  const selected = isSelected(intent.id);
                  return (
                    <button
                      key={intent.id}
                      onClick={() => onToggle(intent.id)}
                      onMouseEnter={(e) => handleMouseEnter(intent, e)}
                      onMouseLeave={handleMouseLeave}
                      className={`text-xs px-3 py-1 rounded-full transition-colors font-medium ${
                        selected
                          ? "bg-emerald-800 text-emerald-50"
                          : "bg-stone-200 text-stone-700 hover:bg-stone-300"
                      }`}
                    >
                      {intent.id}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="pt-3 border-t border-stone-300">
        <div className="text-xs text-stone-600">
          {selectedIntents.length} of {intents.length} intents selected
        </div>
      </div>

      {/* Portal Tooltip */}
      {hoveredIntent &&
        coords &&
        typeof document !== "undefined" &&
        createPortal(
          <div
            className="fixed z-[9999] pointer-events-none transition-opacity duration-200"
            style={{
              top: coords.top - 8,
              left: coords.left,
              transform: "translate(-50%, -100%)",
            }}
          >
            <div className="bg-stone-900/95 backdrop-blur-sm text-stone-50 text-xs rounded-lg p-3 shadow-xl border border-stone-700/50 w-64">
              <div className="font-semibold mb-1 text-emerald-300">
                {hoveredIntent.label}
              </div>
              <div className="leading-relaxed mb-2 text-stone-300">
                {hoveredIntent.description}
              </div>
              {(hoveredIntent as any).example && (
                <div className="bg-black/50 rounded p-2 font-mono text-[10px] text-emerald-200 overflow-x-auto whitespace-pre-wrap border border-stone-800">
                  {(hoveredIntent as any).example}
                </div>
              )}
              {/* Arrow */}
              <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-2 h-2 bg-stone-900/95 rotate-45 border-r border-b border-stone-700/50"></div>
            </div>
          </div>,
          document.body,
        )}
    </div>
  );
}

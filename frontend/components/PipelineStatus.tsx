"use client";

import { useState } from "react";
import {
  CheckCircle,
  Circle,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Activity,
} from "lucide-react";

interface PipelineStep {
  id: number;
  name: string;
  description: string;
  status: "pending" | "running" | "completed" | "error";
}

interface PipelineStatusProps {
  data: {
    status: string;
    currentStep: number;
    steps: PipelineStep[];
  };
}

export default function PipelineStatus({ data }: PipelineStatusProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const total = data.steps.length;
  const current = Math.max(0, Math.min(data.currentStep, total));
  const progressPct = total > 0 ? Math.round((current / total) * 100) : 0;

  // Use data.status directly for overall status
  const running = data.status === "running";
  const failed = data.status === "failed";
  const completed = data.status === "completed";

  const getStatusIcon = () => {
    if (running)
      return <Loader2 className="w-5 h-5 text-sky-700 animate-spin" />;
    if (failed) return <AlertCircle className="w-5 h-5 text-rose-700" />;
    if (completed) return <CheckCircle className="w-5 h-5 text-emerald-700" />;
    return <Circle className="w-5 h-5 text-stone-400" />;
  };

  const getStatusLabel = () => {
    if (running) return "Processing...";
    if (failed) return "Failed";
    if (completed) return "Completed";
    return "Pending";
  };

  const getStatusBgColor = () => {
    if (running) return "bg-sky-100";
    if (failed) return "bg-rose-100";
    if (completed) return "bg-emerald-100";
    return "bg-stone-100";
  };

  return (
    <div className="bg-white rounded-lg border border-stone-300 shadow-sm overflow-hidden mb-4">
      {/* Header - clickable accordion toggle */}
      <div
        className="flex items-center justify-between px-4 py-3 bg-stone-100 border-b border-stone-200 cursor-pointer hover:bg-stone-150"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-md ${getStatusBgColor()}`}>
            {getStatusIcon()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-800" />
              <h3 className="text-sm font-semibold text-stone-800">
                Pipeline Status
              </h3>
            </div>
            <p className="text-xs text-stone-500">{getStatusLabel()}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Progress bar */}
          <div className="w-32 hidden sm:block">
            <div className="h-2 bg-stone-200 rounded-full overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-300 ${running ? "bg-sky-600" : failed ? "bg-rose-600" : "bg-emerald-700"}`}
                style={{ width: `${progressPct}%` }}
              />
            </div>
            <div className="text-xs text-stone-500 text-right mt-0.5">
              {progressPct}%
            </div>
          </div>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-stone-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-stone-500" />
          )}
        </div>
      </div>

      {/* Expandable steps */}
      {isExpanded && (
        <div className="relative pl-12 pr-4 py-4 space-y-3">
          {/* Vertical line */}
          <div className="absolute left-6 top-6 bottom-6 w-px bg-stone-200" />

          {data.steps.map((step) => {
           
            const isFailed = step.status === "error";
            let isCompleted = false;
            let isActive = false;

            if (completed) {
              // Job is done, all steps are completed
              isCompleted = true;
            } else if (running) {
              // Job is running
              isActive = step.id === data.currentStep;
              isCompleted = step.id < data.currentStep;
            } else {
              // Pending or other
              isCompleted =
                step.status === "completed" || step.id < data.currentStep;
            }

            return (
              <div key={step.id} className="flex items-start gap-4">
                <div className="shrink-0 w-8">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium ${
                      isFailed
                        ? "bg-rose-700 text-white"
                        : isCompleted
                          ? "bg-emerald-700 text-white"
                          : isActive
                            ? "bg-sky-600 text-white"
                            : "bg-white text-stone-600 border border-stone-300"
                    }`}
                  >
                    {isFailed ? (
                      <AlertCircle className="w-4 h-4" />
                    ) : isCompleted ? (
                      <CheckCircle className="w-4 h-4" />
                    ) : isActive ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      step.id
                    )}
                  </div>
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-stone-800">
                        {step.name}
                      </div>
                      <div className="text-xs text-stone-500">
                        {step.description}
                      </div>
                    </div>
                    <div>
                      {isFailed && (
                        <span className="text-xs text-rose-800 px-2 py-0.5 bg-rose-100 rounded">
                          Error
                        </span>
                      )}
                      {isActive && !isFailed && (
                        <span className="text-xs text-sky-800 px-2 py-0.5 bg-sky-100 rounded">
                          Running
                        </span>
                      )}
                      {isCompleted && !isFailed && !isActive && (
                        <span className="text-xs text-emerald-800 px-2 py-0.5 bg-emerald-100 rounded">
                          Done
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

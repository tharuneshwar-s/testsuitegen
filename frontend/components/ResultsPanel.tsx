"use client";

import { FileCode, CheckCircle, AlertTriangle, Copy } from "lucide-react";

interface ResultsPanelProps {
  data: {
    status: string;
    testCases: any[];
  };
}

export default function ResultsPanel({ data }: ResultsPanelProps) {
  if (data.status === "idle") {
    return (
      <div className="text-center py-16">
        <FileCode className="w-12 h-12 text-slate-300 mx-auto mb-3" />
        <p className="text-slate-500 text-sm">
          Run the pipeline to see results
        </p>
      </div>
    );
  }

  const copyText = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {}
  };

  if (data.testCases.length === 0) {
    return null;
  }

  return (
    <div className="space-y-5">
      {/* Test Cases Summary */}
      <div>
        <h4 className="font-medium text-slate-900 mb-3 text-sm">
          Generated Test Cases ({data.testCases.length})
        </h4>
        <div className="space-y-2">
          {data.testCases.slice(0, 5).map((test) => (
            <div
              key={test.id}
              className="bg-white rounded-lg p-4 border border-slate-200"
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {test.intent === "HAPPY_PATH" ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-slate-900 text-sm">
                      {test.name}
                    </span>
                    <span
                      className={`text-xs px-1.5 py-0.5 rounded ${
                        test.intent === "HAPPY_PATH"
                          ? "bg-green-50 text-green-700"
                          : "bg-amber-50 text-amber-700"
                      }`}
                    >
                      {test.intent}
                    </span>
                    <button
                      onClick={() => copyText(`${test.name}: ${test.description}`)}
                      className="ml-auto px-2 py-1 text-xs rounded bg-slate-100 text-slate-700 hover:bg-slate-200 flex items-center gap-1"
                    >
                      <Copy className="w-3 h-3" /> Copy
                    </button>
                  </div>
                  <p className="text-sm text-slate-600">
                    {test.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
        {data.testCases.length > 5 && (
          <p className="text-center text-sm text-slate-500 mt-3">
            ... and {data.testCases.length - 5} more tests
          </p>
        )}
      </div>
    </div>
  );
}

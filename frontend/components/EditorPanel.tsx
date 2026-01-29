import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Upload, FileText } from "lucide-react";

const Editor = dynamic(() => import("@monaco-editor/react"), { ssr: false });

type InputType = "openapi" | "python" | "typescript";
type OutputLanguage = "jest" | "pytest";

interface EditorPanelProps {
  inputType: InputType;
  onInputTypeChange: (type: InputType) => void;
  apiDefinition: string;
  onApiDefinitionChange: (content: string) => void;
  outputLanguage: OutputLanguage;
  onOutputLanguageChange: (lang: OutputLanguage) => void;
  selectedIntents: string[];
  onToggleIntent: (intentId: string) => void;
  onGenerateClick: () => void;
  isRunning: boolean;
  intents: any[];
  categories: any;
  onFileUpload: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

export default function EditorPanel({
  inputType,
  onInputTypeChange,
  apiDefinition,
  onApiDefinitionChange,
  outputLanguage,
  onOutputLanguageChange,
  selectedIntents,
  onToggleIntent,
  onGenerateClick,
  isRunning,
  intents,
  categories,
  onFileUpload,
}: EditorPanelProps) {
  // Auto-set framework based on source type
  useEffect(() => {
    if (inputType === "python") {
      onOutputLanguageChange("pytest");
    } else if (inputType === "typescript") {
      onOutputLanguageChange("jest");
    }
  }, [inputType, onOutputLanguageChange]);

  const getEditorLanguage = () => {
    switch (inputType) {
      case "openapi":
        return apiDefinition.trim().startsWith("{") ? "json" : "yaml";
      case "python":
        return "python";
      case "typescript":
        return "typescript";
      default:
        return "yaml";
    }
  };

  // Determine which frameworks are available based on source type
  const getAvailableFrameworks = (): OutputLanguage[] => {
    if (inputType === "python") {
      return ["pytest"];
    } else if (inputType === "typescript") {
      return ["jest"];
    } else {
      // OpenAPI: both frameworks available
      return ["jest", "pytest"];
    }
  };

  const availableFrameworks = getAvailableFrameworks();
  const showFrameworkSelector = availableFrameworks.length > 1;

  const inputTypes = [
    {
      id: "openapi" as InputType,
      label: "OpenAPI 3.x",
      icon: FileText,
      color: "emerald",
      desc: "OpenAPI/Swagger 3.0+ spec",
    },
    {
      id: "python" as InputType,
      label: "Python",
      icon: FileText,
      color: "violet",
      desc: "Python function signatures",
    },
    {
      id: "typescript" as InputType,
      label: "TypeScript",
      icon: FileText,
      color: "blue",
      desc: "TS functions & types",
    },
  ];

  return (
    <div className="flex flex-col bg-stone-50 border-r border-stone-300 h-full">
      {/* Input Type Selector */}
      <div className="p-4 border-b border-stone-300 shrink-0">
        <div className="grid grid-cols-2 gap-3">
          {inputTypes.map((type) => {
            const Icon = type.icon;
            const selected = inputType === type.id;
            return (
              <button
                key={type.id}
                onClick={() => onInputTypeChange(type.id)}
                aria-pressed={selected}
                className={`p-3 rounded-lg border text-left transition-all transform ${selected ? "border-emerald-700 bg-emerald-50 shadow-md" : "border-stone-300 hover:border-stone-400 bg-white hover:shadow-sm"} focus:outline-none focus:ring-2 focus:ring-emerald-300`}
              >
                <div className="flex items-center gap-3 w-full">
                  <div
                    className={`p-1 rounded ${selected ? "bg-emerald-200" : "bg-stone-100"}`}
                  >
                    <Icon
                      className={`w-3 h-3 ${selected ? "text-emerald-800" : "text-stone-500"}`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div
                      className={`text-sm font-semibold ${selected ? "text-emerald-900" : "text-stone-800"}`}
                    >
                      {type.label}
                    </div>
                    <div className="text-xs text-stone-500 mt-1">
                      {type.desc}
                    </div>
                  </div>
                </div>
              </button>
            );
          })}

          {/* Upload Button - as 4th card */}
          <label
            htmlFor="file-upload"
            className="p-3 rounded-lg border border-stone-300 hover:border-stone-400 bg-white hover:shadow-sm text-left transition-all transform focus-within:ring-2 focus-within:ring-emerald-300 cursor-pointer flex flex-col items-center justify-center gap-2"
          >
            <div className="p-1 rounded bg-stone-100">
              <Upload className="w-3 h-3 text-stone-500" />
            </div>
            <div className="flex-1 min-w-0 text-center">
              <div className="text-sm font-semibold text-stone-800">Upload</div>
              <div className="text-xs text-stone-500 mt-1">Select file</div>
            </div>
            <input
              id="file-upload"
              type="file"
              accept=".yaml,.yml,.json,.ts,.py"
              className="hidden"
              onChange={onFileUpload}
            />
          </label>
        </div>
      </div>

      {/* Code Editor */}
      <div className="flex-1 min-h-0 flex flex-col">
        <div className="flex-1 min-h-0 p-4">
          <div className="h-full bg-white rounded-lg border border-stone-300 shadow-sm overflow-hidden">
            <Editor
              height="100%"
              language={getEditorLanguage()}
              value={apiDefinition}
              onChange={(value) => onApiDefinitionChange(value || "")}
              theme="vs-light"
              options={{
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: "on",
                wordWrap: "on",
                padding: { top: 12, bottom: 12 },
                smoothScrolling: true,
                folding: true,
                glyphMargin: true,
                automaticLayout: true,
              }}
            />
          </div>
        </div>
      </div>

      {/* Output Language & Generate Button */}
      <div className="p-4 border-t border-stone-300 space-y-4 shrink-0">
        {apiDefinition && (
          <>
            {/* Framework selector - only show if multiple options */}
            {showFrameworkSelector && (
              <div>
                <div className="flex gap-2">
                  {availableFrameworks.includes("jest") && (
                    <button
                      onClick={() => onOutputLanguageChange("jest")}
                      className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        outputLanguage === "jest"
                          ? "bg-emerald-800 text-white shadow-sm"
                          : "bg-stone-200 text-stone-700 hover:bg-stone-300"
                      }`}
                    >
                      Jest / TypeScript
                    </button>
                  )}
                  {availableFrameworks.includes("pytest") && (
                    <button
                      onClick={() => onOutputLanguageChange("pytest")}
                      className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                        outputLanguage === "pytest"
                          ? "bg-emerald-800 text-white shadow-sm"
                          : "bg-stone-200 text-stone-700 hover:bg-stone-300"
                      }`}
                    >
                      Pytest / Python
                    </button>
                  )}
                </div>
              </div>
            )}

            {/* Show selected framework badge when only one option */}
            {!showFrameworkSelector && (
              <div className="flex items-center justify-center">
                <span className="px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                  {outputLanguage === "pytest"
                    ? "Pytest / Python"
                    : "Jest / TypeScript"}
                </span>
              </div>
            )}

            <button
              onClick={onGenerateClick}
              disabled={isRunning || !apiDefinition.trim()}
              className="w-full bg-gradient-to-r from-emerald-800 to-emerald-900 hover:from-emerald-900 hover:to-emerald-950 disabled:from-stone-300 disabled:to-stone-300 text-white disabled:text-stone-500 font-semibold py-3 px-6 rounded-lg transition-all duration-150 flex items-center justify-center gap-2 disabled:cursor-not-allowed shadow-lg shadow-emerald-900/20 disabled:shadow-none"
            >
              {isRunning ? (
                <>
                  <div className="w-4 h-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Generating Tests...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Generate Test Suite
                </>
              )}
            </button>
          </>
        )}
      </div>
    </div>
  );
}

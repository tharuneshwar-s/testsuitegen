"use client";

import { useState, useEffect } from "react";
import {
  FileCode2,
  Database,
  Copy,
  Check,
  ChevronDown,
  ChevronRight,
  Download,
  Code2,
  TestTube2,
  Loader2,
  Sparkles,
  Filter,
} from "lucide-react";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import { SkeletonArtifacts } from "./Skeletons";

interface ArtifactsTabsProps {
  testFiles: Record<string, string>;
  payloads: Array<{
    intent?: string;
    operation?: string;
    operation_id?: string;
    method?: string;
    path?: string;
    payload?: any;
    request_body?: any;
    response?: any;
    expected_status?: number;
  }>;
  enhancedPayloads?: Array<any>;
  isLoading?: boolean;
  inputType?: "openapi" | "python" | "typescript";
}

export default function ArtifactsTabs({
  testFiles,
  payloads,
  enhancedPayloads,
  isLoading = false,
  inputType = "openapi",
}: ArtifactsTabsProps) {
  const [activeTab, setActiveTab] = useState<"tests" | "payloads">("tests");
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [expandedPayloads, setExpandedPayloads] = useState<Set<number>>(
    new Set(),
  );
  const [expandedTests, setExpandedTests] = useState<Set<string>>(new Set());
  const [isDownloading, setIsDownloading] = useState(false);
  const [methodFilters, setMethodFilters] = useState<Record<string, boolean>>({
    GET: true,
    POST: true,
    PUT: true,
    PATCH: true,
    DELETE: true,
  });
  const [statusFilters, setStatusFilters] = useState<Record<number, boolean>>(
    {},
  );

  const toggleMethodFilter = (method: string) => {
    setMethodFilters((prev) => ({ ...prev, [method]: !prev[method] }));
  };

  const toggleStatusFilter = (status: number) => {
    setStatusFilters((prev) => ({ ...prev, [status]: !prev[status] }));
  };

  // Initialize status filters when payloads change
  useEffect(() => {
    if (inputType === "openapi") return;

    const statuses = new Set<number>();
    payloads.forEach((p) => {
      if (p.expected_status) statuses.add(p.expected_status);
    });

    setStatusFilters((prev) => {
      const next = { ...prev };
      statuses.forEach((s) => {
        if (next[s] === undefined) next[s] = true;
      });
      return next;
    });
  }, [payloads, inputType]);

  const allTestFileNames = Object.keys(testFiles);

  // Only display actual test files (e.g., files starting with 'test', located in '/tests/', or common test extensions)
  const testFileNames = allTestFileNames.filter((name) => {
    const lower = name.toLowerCase();
    const filename = lower.includes("/")
      ? lower.split("/").pop() || lower
      : lower;
    return (
      filename.startsWith("test") ||
      lower.includes("/tests/") ||
      /\.(py|ts|js)$/.test(filename)
    );
  });

  // Filter payloads to only show those with non-empty request bodies
  const payloadsWithBody = payloads.filter((item) => {
    const body = item.payload || item.request_body;
    return body && typeof body === "object" && Object.keys(body).length > 0;
  });

  // Determine HTTP method from operation_id
  const getMethodFromOperationId = (opId: string): string => {
    const lower = opId?.toLowerCase() || "";

    // First priority: check suffix (most reliable for OpenAPI generated IDs)
    if (lower.endsWith("_get") || lower.endsWith("get")) return "GET";
    if (lower.endsWith("_post") || lower.endsWith("post")) return "POST";
    if (lower.endsWith("_put") || lower.endsWith("put")) return "PUT";
    if (lower.endsWith("_patch") || lower.endsWith("patch")) return "PATCH";
    if (lower.endsWith("_delete") || lower.endsWith("delete")) return "DELETE";

    // Second priority: check for method keywords in the middle
    if (lower.includes("_get_")) return "GET";
    if (lower.includes("_post_")) return "POST";
    if (lower.includes("_put_")) return "PUT";
    if (lower.includes("_patch_")) return "PATCH";
    if (lower.includes("_delete_")) return "DELETE";

    // Third priority: check for action-based keywords (less reliable)
    if (
      lower.startsWith("get") ||
      lower.includes("list") ||
      lower.includes("read") ||
      lower.includes("fetch")
    )
      return "GET";
    if (
      lower.startsWith("post") ||
      lower.includes("create") ||
      lower.includes("add")
    )
      return "POST";
    if (
      lower.startsWith("put") ||
      lower.includes("update") ||
      lower.includes("replace")
    )
      return "PUT";
    if (lower.startsWith("patch") || lower.includes("modify")) return "PATCH";
    if (lower.startsWith("delete") || lower.includes("remove")) return "DELETE";

    return "POST"; // Default fallback
  };

  // Count payloads by method
  const methodCounts = {
    GET: payloadsWithBody.filter(
      (p) => getMethodFromOperationId(p.operation_id || "") === "GET",
    ).length,
    POST: payloadsWithBody.filter(
      (p) => getMethodFromOperationId(p.operation_id || "") === "POST",
    ).length,
    PUT: payloadsWithBody.filter(
      (p) => getMethodFromOperationId(p.operation_id || "") === "PUT",
    ).length,
    PATCH: payloadsWithBody.filter(
      (p) => getMethodFromOperationId(p.operation_id || "") === "PATCH",
    ).length,
    DELETE: payloadsWithBody.filter(
      (p) => getMethodFromOperationId(p.operation_id || "") === "DELETE",
    ).length,
  };

  // Count payloads by status
  const statusCounts = payloadsWithBody.reduce(
    (acc, p) => {
      const s = p.expected_status || 0;
      acc[s] = (acc[s] || 0) + 1;
      return acc;
    },
    {} as Record<number, number>,
  );

  // Apply filter based on inputType
  const filteredPayloads = payloadsWithBody.filter((p) => {
    if (inputType === "openapi") {
      return (
        methodFilters[getMethodFromOperationId(p.operation_id || "")] ?? true
      );
    } else {
      return statusFilters[p.expected_status || 0] ?? true;
    }
  });

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCode(id);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch {}
  };

  const downloadFile = (filename: string, content: string) => {
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadAllAsZip = async () => {
    if (testFileNames.length === 0) return;

    setIsDownloading(true);
    try {
      const zip = new JSZip();

      // Add all test files to the zip
      testFileNames.forEach((filename) => {
        zip.file(filename, testFiles[filename]);
      });

      // Generate the zip file
      const content = await zip.generateAsync({ type: "blob" });

      // Download the zip
      saveAs(content, "test-scripts.zip");
    } catch (error) {
      console.error("Failed to create zip file:", error);
    } finally {
      setIsDownloading(false);
    }
  };

  const togglePayload = (index: number) => {
    setExpandedPayloads((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  const toggleTest = (filename: string) => {
    setExpandedTests((prev) => {
      const next = new Set(prev);
      if (next.has(filename)) {
        next.delete(filename);
      } else {
        next.add(filename);
      }
      return next;
    });
  };

  const getMethodColor = (method: string) => {
    const colors: Record<string, string> = {
      GET: "bg-sky-700 text-sky-50",
      POST: "bg-emerald-800 text-emerald-50",
      PUT: "bg-amber-700 text-amber-50",
      PATCH: "bg-orange-700 text-orange-50",
      DELETE: "bg-rose-800 text-rose-50",
    };
    return colors[method?.toUpperCase()] || "bg-stone-600 text-stone-50";
  };

  const getIntentColor = (intent: string) => {
    const colors: Record<string, string> = {
      HAPPY_PATH: "bg-emerald-800 text-emerald-50",
      EDGE_CASE: "bg-amber-700 text-amber-50",
      ERROR_HANDLING: "bg-rose-700 text-rose-50",
      SECURITY: "bg-violet-700 text-violet-50",
      PERFORMANCE: "bg-sky-700 text-sky-50",
    };
    return colors[intent?.toUpperCase()] || "bg-stone-600 text-stone-50";
  };

  // Show skeleton while loading
  if (isLoading) {
    return (
      <div className="bg-stone-50 rounded-lg border border-stone-300 overflow-hidden shadow-sm p-4">
        <SkeletonArtifacts />
      </div>
    );
  }

  return (
    <div className="bg-stone-50 rounded-lg border border-stone-300 overflow-hidden shadow-sm">
      {/* Tabs Header */}
      <div className="border-b border-stone-300 bg-stone-100">
        <div className="flex">
          <button
            onClick={() => setActiveTab("tests")}
            className={`flex items-center gap-2 px-5 py-3.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "tests"
                ? "border-emerald-800 text-emerald-800 bg-white"
                : "border-transparent text-stone-600 hover:text-stone-900 hover:bg-stone-200"
            }`}
          >
            <TestTube2 className="w-4 h-4" />
            Test Scripts
            <span className="ml-1.5 px-2 py-0.5 text-xs rounded-full bg-emerald-800 text-emerald-50 font-medium">
              {testFileNames.length}
            </span>
          </button>
          <button
            onClick={() => setActiveTab("payloads")}
            className={`flex items-center gap-2 px-5 py-3.5 text-sm font-medium border-b-2 transition-colors ${
              activeTab === "payloads"
                ? "border-emerald-800 text-emerald-800 bg-white"
                : "border-transparent text-stone-600 hover:text-stone-900 hover:bg-stone-200"
            }`}
          >
            <Sparkles className="w-4 h-4" />
            Mock Data
            <span className="ml-1.5 px-2 py-0.5 text-xs rounded-full bg-emerald-800 text-emerald-50 font-medium">
              {filteredPayloads.length}
            </span>
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-h-[600px] overflow-y-auto">
        {activeTab === "tests" ? (
          <div className="divide-y divide-slate-100">
            {testFileNames.length === 0 ? (
              <div className="p-8 text-center text-slate-500">
                <Code2 className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                <p className="text-sm">No test files generated yet</p>
              </div>
            ) : (
              testFileNames.map((filename) => (
                <div key={filename} className="bg-white">
                  <div
                    className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-50 transition-colors"
                    onClick={() => toggleTest(filename)}
                  >
                    <div className="flex items-center gap-3">
                      {expandedTests.has(filename) ? (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      )}
                      <FileCode2 className="w-4 h-4 text-emerald-600" />
                      <span className="font-mono text-sm text-slate-900">
                        {filename}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          downloadFile(filename, testFiles[filename]);
                        }}
                        className="flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md bg-slate-100 text-slate-700 hover:bg-slate-200 transition-colors"
                      >
                        <Download className="w-3 h-3" />
                        Download
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(testFiles[filename], filename);
                        }}
                        className="flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md bg-emerald-100 text-emerald-700 hover:bg-emerald-200 transition-colors"
                      >
                        {copiedCode === filename ? (
                          <Check className="w-3 h-3" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                        {copiedCode === filename ? "Copied!" : "Copy"}
                      </button>
                    </div>
                  </div>
                  {expandedTests.has(filename) && (
                    <div className="px-4 pb-4">
                      <pre className="bg-slate-900 text-slate-50 rounded-lg p-4 overflow-x-auto text-xs font-mono leading-relaxed max-h-96 overflow-y-auto">
                        {testFiles[filename]}
                      </pre>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        ) : (
          <>
            {/* Filter Bar for Mock Data */}
            <div className="flex items-center gap-2 px-4 py-2 bg-stone-50 border-b border-stone-200">
              <Filter className="w-3.5 h-3.5 text-stone-500" />
              <span className="text-xs text-stone-600">Filter:</span>
              <div className="flex gap-1.5 flex-wrap">
                {inputType === "openapi" ? (
                  <>
                    <button
                      onClick={() => toggleMethodFilter("GET")}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.GET
                          ? "bg-sky-100 text-sky-800 border-sky-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      GET ({methodCounts.GET})
                    </button>
                    <button
                      onClick={() => toggleMethodFilter("POST")}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.POST
                          ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      POST ({methodCounts.POST})
                    </button>
                    <button
                      onClick={() => toggleMethodFilter("PUT")}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.PUT
                          ? "bg-amber-100 text-amber-800 border-amber-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      PUT ({methodCounts.PUT})
                    </button>
                    <button
                      onClick={() => toggleMethodFilter("PATCH")}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.PATCH
                          ? "bg-orange-100 text-orange-800 border-orange-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      PATCH ({methodCounts.PATCH})
                    </button>
                    <button
                      onClick={() => toggleMethodFilter("DELETE")}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.DELETE
                          ? "bg-rose-100 text-rose-800 border-rose-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      DELETE ({methodCounts.DELETE})
                    </button>
                  </>
                ) : (
                  Object.keys(statusCounts).map((status) => (
                    <button
                      key={status}
                      onClick={() => toggleStatusFilter(Number(status))}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        statusFilters[Number(status)]
                          ? "bg-stone-800 text-stone-50 border-stone-600"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      {status} ({statusCounts[Number(status)]})
                    </button>
                  ))
                )}
              </div>
            </div>

            {/* Payloads List */}
            <div className="divide-y divide-stone-200">
              {filteredPayloads.length === 0 ? (
                <div className="p-8 text-center text-stone-500">
                  <Database className="w-12 h-12 mx-auto mb-3 text-stone-300" />
                  <p className="text-sm">No payloads matching filter</p>
                </div>
              ) : (
                filteredPayloads.map((item, idx) => (
                  <div key={idx} className="bg-white">
                    <div
                      className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-slate-50 transition-colors"
                      onClick={() => togglePayload(idx)}
                    >
                      <div className="flex items-center gap-3">
                        {expandedPayloads.has(idx) ? (
                          <ChevronDown className="w-4 h-4 text-slate-400" />
                        ) : (
                          <ChevronRight className="w-4 h-4 text-slate-400" />
                        )}
                        {inputType === "openapi" && (
                          <span
                            className={`px-2 py-0.5 text-xs font-mono font-medium rounded ${getMethodColor(getMethodFromOperationId(item.operation_id || ""))}`}
                          >
                            {getMethodFromOperationId(item.operation_id || "")}
                          </span>
                        )}
                        <span className="font-mono text-sm text-slate-700 truncate max-w-xs">
                          {item.path ||
                            item.operation ||
                            item.operation_id ||
                            "Unknown endpoint"}
                        </span>
                        {item.intent && (
                          <span
                            className={`px-2 py-0.5 text-xs font-medium rounded ${getIntentColor(item.intent)}`}
                          >
                            {item.intent}
                          </span>
                        )}
                        {item.expected_status && (
                          <span
                            className={`px-2 py-0.5 text-xs font-mono font-medium rounded ${
                              item.expected_status >= 200 &&
                              item.expected_status < 300
                                ? "bg-emerald-100 text-emerald-700"
                                : item.expected_status >= 400
                                  ? "bg-rose-100 text-rose-700"
                                  : "bg-amber-100 text-amber-700"
                            }`}
                          >
                            {item.expected_status}
                          </span>
                        )}
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          copyToClipboard(
                            JSON.stringify(
                              item.request_body || item.payload || item,
                              null,
                              2,
                            ),
                            `payload-${idx}`,
                          );
                        }}
                        className="flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-md bg-emerald-100 text-emerald-700 hover:bg-emerald-200 transition-colors"
                      >
                        {copiedCode === `payload-${idx}` ? (
                          <Check className="w-3 h-3" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                        {copiedCode === `payload-${idx}` ? "Copied!" : "Copy"}
                      </button>
                    </div>
                    {expandedPayloads.has(idx) && (
                      <div className="px-4 pb-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                          {/* Request Body / Payload */}
                          <div className="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                            <div className="flex items-center gap-2 px-3 py-2 bg-slate-100 border-b border-slate-200">
                              <div className="w-2 h-2 rounded-full bg-sky-500"></div>
                              <h5 className="text-xs font-semibold text-slate-700 uppercase tracking-wide">
                                Request Body
                              </h5>
                            </div>
                            <pre className="bg-slate-900 text-slate-50 p-3 overflow-x-auto text-xs font-mono leading-relaxed max-h-80 overflow-y-auto m-0 rounded-none">
                              {JSON.stringify(
                                item.payload || item.request_body || {},
                                null,
                                2,
                              )}
                            </pre>
                          </div>

                          {/* Expected Response */}
                          {item.response && (
                            <div className="bg-slate-50 rounded-lg border border-slate-200 overflow-hidden">
                              <div className="flex items-center gap-2 px-3 py-2 bg-emerald-50 border-b border-emerald-200">
                                <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                                <h5 className="text-xs font-semibold text-emerald-700 uppercase tracking-wide">
                                  Expected Response
                                </h5>
                                {item.response.status && (
                                  <span
                                    className={`ml-auto px-2 py-0.5 text-xs font-mono font-medium rounded ${
                                      item.response.status >= 200 &&
                                      item.response.status < 300
                                        ? "bg-emerald-100 text-emerald-700"
                                        : item.response.status >= 400
                                          ? "bg-rose-100 text-rose-700"
                                          : "bg-amber-100 text-amber-700"
                                    }`}
                                  >
                                    {item.response.status}
                                  </span>
                                )}
                              </div>
                              <pre className="bg-slate-800 text-emerald-300 p-3 overflow-x-auto text-xs font-mono leading-relaxed max-h-80 overflow-y-auto m-0 rounded-none">
                                {JSON.stringify(
                                  item.response.body ?? item.response,
                                  null,
                                  2,
                                )}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      {(testFileNames.length > 0 || payloads.length > 0) && (
        <div className="border-t border-slate-200 bg-slate-50 px-4 py-3 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            {activeTab === "tests"
              ? `${testFileNames.length} test file${testFileNames.length !== 1 ? "s" : ""} ready`
              : `${filteredPayloads.length} mock data item${filteredPayloads.length !== 1 ? "s" : ""} generated`}
          </span>
          {activeTab === "tests" && testFileNames.length > 0 && (
            <button
              onClick={downloadAllAsZip}
              disabled={isDownloading}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-emerald-600 text-white hover:bg-emerald-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  Creating Zip...
                </>
              ) : (
                <>
                  <Download className="w-3.5 h-3.5" />
                  Download All (ZIP)
                </>
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

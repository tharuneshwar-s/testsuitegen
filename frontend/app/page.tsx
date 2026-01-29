"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import Header from "@/components/Header";
import SessionsSidebar from "@/components/SessionsSidebar";
import EditorPanel from "@/components/EditorPanel";
import OutputPanel from "@/components/OutputPanel";
import { PipelineData, INITIAL_PIPELINE_DATA } from "@/lib/types";

import {
  OPENAPI_INTENTS,
  PYTHON_INTENTS,
  TYPESCRIPT_INTENTS,
  INTENT_CATEGORIES,
} from "@/lib/intents";
import {
  DEFAULT_PAYLOAD_ENHANCEMENT_PROVIDER,
  DEFAULT_PAYLOAD_ENHANCEMENT_MODEL,
  DEFAULT_TEST_ENHANCEMENT_PROVIDER,
  DEFAULT_TEST_ENHANCEMENT_MODEL,
} from "@/lib/llm_config";
import {
  createJob,
  subscribeToJobStatus,
  subscribeToLogs,
  fetchSessionsFromSupabase,
  fetchJobArtifacts,
  fetchJobLogs,
  base64ToString,
  type JobStatus,
  type LogEntry,
} from "@/lib/api";

type InputType = "openapi" | "python" | "typescript";
type OutputLanguage = "jest" | "pytest";

interface SessionRecord {
  jobId: string;
  timestamp: number;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
}

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const urlJobId = searchParams?.get("jobId");

  // UI State
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [leftWidth, setLeftWidth] = useState(38);
  const [isDragging, setIsDragging] = useState(false);

  // Input State
  const [inputType, setInputType] = useState<InputType>("openapi");
  const [outputLanguage, setOutputLanguage] =
    useState<OutputLanguage>("pytest");
  const [apiDefinition, setApiDefinition] = useState("");
  const [baseUrl, setBaseUrl] = useState("http://localhost:8000");
  const [baseUrlOpen, setBaseUrlOpen] = useState(false);

  // LLM Config State
  const [llmProvider, setLlmProvider] = useState(
    DEFAULT_TEST_ENHANCEMENT_PROVIDER,
  );
  const [llmModel, setLlmModel] = useState(DEFAULT_TEST_ENHANCEMENT_MODEL);
  const [payloadEnhancementProvider, setPayloadEnhancementProvider] = useState(
    DEFAULT_PAYLOAD_ENHANCEMENT_PROVIDER,
  );
  const [payloadEnhancementModel, setPayloadEnhancementModel] = useState(
    DEFAULT_PAYLOAD_ENHANCEMENT_MODEL,
  );
  const [llmConfigOpen, setLlmConfigOpen] = useState(false);

  // Job State
  const [isRunning, setIsRunning] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoadingData, setIsLoadingData] = useState(false);

  // Pipeline State
  const [pipelineData, setPipelineData] = useState<PipelineData>(
    INITIAL_PIPELINE_DATA,
  );
  const [showResults, setShowResults] = useState(false);

  // Sessions State
  const [sessions, setSessions] = useState<SessionRecord[]>([]);

  // Intent State
  const [selectedIntents, setSelectedIntents] = useState<string[]>([
    "HAPPY_PATH",
  ]);
  const [rightIntentOpen, setRightIntentOpen] = useState(false);

  // Logs State
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const logsCleanupRef = useRef<(() => void) | null>(null);

  // Subscription cleanup ref
  const cleanupRef = useRef<(() => void) | null>(null);

  // Track if initial job data has been loaded (to avoid resetting UI state on real-time updates)
  const initialLoadDoneRef = useRef<string | null>(null);

  // Load sessions from Supabase on mount
  useEffect(() => {
    const loadSessions = async () => {
      try {
        const supabaseSessions = await fetchSessionsFromSupabase();
        setSessions(supabaseSessions);
      } catch (e) {
        console.error("Failed to load sessions:", e);
      }
    };
    loadSessions();
  }, []);

  // Handle URL-based job ID - subscribe to real-time updates
  useEffect(() => {
    if (urlJobId && !isRunning) {
      console.log("Loading job from URL:", urlJobId);
      setCurrentJobId(urlJobId);
      setShowResults(true);
      setIsLoadingData(true);

      // Reset initial load tracking for new job
      initialLoadDoneRef.current = null;

      // Clear previous logs and start fresh
      setLogs([]);

      // Fetch initial logs
      fetchJobLogs(urlJobId).then((initialLogs) => {
        if (initialLogs.length > 0) {
          setLogs(initialLogs);
        }
      });

      // Subscribe to real-time updates
      const cleanup = subscribeToJobStatus(
        urlJobId,
        async (status) => {
          setIsLoadingData(false);
          try {
            await updatePipelineFromJobStatus(status, urlJobId);
          } catch (err) {
            console.error(
              "Failed updating pipeline from initial real-time status:",
              err,
            );
          }

          if (
            status.status.toLowerCase() === "completed" ||
            status.status.toLowerCase() === "failed"
          ) {
            setIsRunning(false);
          }
        },
        (err) => {
          console.error("Subscription error:", err);
          setError(err.message);
          setIsLoadingData(false);
          // Auto-refresh on Realtime channel error
          if (err.message === "Realtime channel error") {
            console.log("Realtime channel error detected, refreshing page...");
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
        },
      );

      cleanupRef.current = cleanup;

      // Subscribe to logs for this job
      if (logsCleanupRef.current) logsCleanupRef.current();
      logsCleanupRef.current = subscribeToLogs(urlJobId, (log) => {
        setLogs((prev) => [...prev, log]);
      });

      return () => {
        if (cleanupRef.current) {
          cleanupRef.current();
        }
      };
    }
  }, [urlJobId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (cleanupRef.current) {
        cleanupRef.current();
      }
      if (logsCleanupRef.current) {
        logsCleanupRef.current();
      }
    };
  }, []);

  const handleUploadFile: React.ChangeEventHandler<HTMLInputElement> = async (
    e,
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setApiDefinition(text);
    const ext = file.name.toLowerCase();
    if (ext.endsWith(".yaml") || ext.endsWith(".yml")) {
      setInputType("openapi");
      setOutputLanguage("pytest");
    } else if (ext.endsWith(".json")) {
      setInputType("openapi");
      setOutputLanguage("pytest");
    } else if (ext.endsWith(".ts")) {
      setInputType("typescript");
      setOutputLanguage("jest");
    }
    setShowResults(false);
    setRightIntentOpen(true);
  };

  const handleGenerate = async () => {
    if (!apiDefinition.trim()) return;

    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }

    setIsRunning(true);
    setShowResults(true);
    setError(null);
    setIsLoadingData(true);
    setRightIntentOpen(false);
    setBaseUrlOpen(false);
    setLlmConfigOpen(false);

    setPipelineData({
      ...INITIAL_PIPELINE_DATA,
      status: "pending",
      currentStep: 0,
    });

    try {
      // Map inputType to source_type (direct mapping now)
      const sourceType = inputType;
      const intents =
        selectedIntents.length > 0 ? selectedIntents : ["HAPPY_PATH"];

      const jobResponse = await createJob({
        spec_data: apiDefinition,
        source_type: sourceType,
        framework: outputLanguage,
        base_url: baseUrl,
        target_intents: intents,
        llm_config: {
          payload_enhancement: {
            provider: payloadEnhancementProvider,
            model: payloadEnhancementModel,
          },
          test_enhancement: {
            provider: llmProvider,
            model: llmModel,
          },
        },
      });

      const jobId = jobResponse.job_id;
      setCurrentJobId(jobId);
      console.log("Job created:", jobId);

      const newSession: SessionRecord = {
        jobId,
        timestamp: Date.now(),
        status: "pending",
        progress: 0,
      };
      const updatedSessions = [newSession, ...sessions];
      setSessions(updatedSessions);

      router.push(`?jobId=${jobId}`);

      // Mark initial load as done for this job (we just set the UI state)
      initialLoadDoneRef.current = jobId;

      // Clear previous logs and subscribe to new ones
      setLogs([]);
      if (logsCleanupRef.current) logsCleanupRef.current();
      logsCleanupRef.current = subscribeToLogs(jobId, (log) => {
        setLogs((prev) => [...prev, log]);
      });

      // Fetch initial logs for this job (don't await, do async)
      fetchJobLogs(jobId).then((initialLogs) => {
        if (initialLogs.length > 0) {
          setLogs(initialLogs);
        }
      });

      const cleanup = subscribeToJobStatus(
        jobId,
        async (status) => {
          console.log("Real-time update:", status.status, status.progress);
          setIsLoadingData(false);
          try {
            await updatePipelineFromJobStatus(status, jobId);
          } catch (err) {
            console.error(
              "Failed updating pipeline from real-time status:",
              err,
            );
          }

          setSessions((prev) =>
            prev.map((s) =>
              s.jobId === jobId
                ? {
                    ...s,
                    status: status.status.toLowerCase() as any,
                    progress: status.progress || 0,
                  }
                : s,
            ),
          );

          if (
            status.status.toLowerCase() === "completed" ||
            status.progress === 100 ||
            status.status.toLowerCase() === "failed"
          ) {
            setIsRunning(false);

            // Refresh artifacts data when job completes
            if (
              status.status.toLowerCase() === "completed" ||
              status.progress === 100
            ) {
              setIsLoadingData(true);
              // Wait a moment for consistency before fetching artifacts
              setTimeout(async () => {
                try {
                  const artifacts = await fetchJobArtifacts(jobId);
                  setPipelineData((prev) => ({
                    ...prev,
                    testFiles: artifacts.testFiles || {},
                    payloads: artifacts.payloads || [],
                    testCases: artifacts.intents || prev.testCases,
                    endpoints: (status.endpoints as any[]) || prev.endpoints,
                  }));
                  console.log("Artifacts refreshed on completion:", artifacts);
                } catch (err) {
                  console.error(
                    "Failed to refresh artifacts on completion:",
                    err,
                  );
                } finally {
                  setIsLoadingData(false);
                }
              }, 2000);
            }
          }
        },
        (err) => {
          console.error("Subscription error:", err);
          setError(err.message);
          setIsRunning(false);
          setIsLoadingData(false);
          setPipelineData((prev) => ({ ...prev, status: "failed" }));
          // Auto-refresh on Realtime channel error
          if (err.message === "Realtime channel error") {
            console.log("Realtime channel error detected, refreshing page...");
            setTimeout(() => {
              window.location.reload();
            }, 1000);
          }
        },
      );

      cleanupRef.current = cleanup;
    } catch (err: any) {
      console.error("Job creation error:", err);
      setError(err.message || "Failed to create job");
      setIsRunning(false);
      setIsLoadingData(false);
      setPipelineData((prev) => ({ ...prev, status: "failed" }));
    }
  };

  const updatePipelineFromJobStatus = async (
    status: JobStatus,
    jobId: string,
  ) => {
    const jobStatus = status.status.toLowerCase();
    const progress = status.progress || 0;

    // Check if this is the initial load for this job (restore full UI state)
    const isInitialLoad = initialLoadDoneRef.current !== jobId;

    if (isInitialLoad) {
      console.log("Initial job data load - restoring full UI state");
      initialLoadDoneRef.current = jobId;

      // Restore source type / input type
      if (status.source_type) {
        const sourceType = status.source_type.toLowerCase();

        let newInputType: InputType = "openapi";
        if (sourceType === "python") {
          newInputType = "python";
        } else if (sourceType === "typescript") {
          newInputType = "typescript";
        }
        setInputType(newInputType);

        // Restore framework / output language
        const requestFramework =
          status.request_payload && (status.request_payload as any).framework;

        let newOutputLanguage: OutputLanguage = "pytest";
        if (sourceType === "typescript") {
          newOutputLanguage = "jest";
        } else if (requestFramework === "jest") {
          newOutputLanguage = "jest";
        } else {
          newOutputLanguage = "pytest";
        }

        setOutputLanguage(newOutputLanguage);
      }

      // Restore spec content (decode from base64)
      if (status.spec_data) {
        try {
          const decodedSpec = base64ToString(status.spec_data);
          setApiDefinition(decodedSpec);
        } catch (e) {
          console.error("Failed to decode spec_data:", e);
          // Try using as-is if not base64 encoded
          setApiDefinition(status.spec_data);
        }
      }

      // Restore base URL
      if (status.base_url) {
        setBaseUrl(status.base_url);
      }

      // Restore intents from request_payload
      if (
        status.request_payload?.target_intents &&
        status.request_payload.target_intents.length > 0
      ) {
        setSelectedIntents(status.request_payload.target_intents);
      }

      // Restore LLM configuration
      if (status.request_payload?.llm_config?.test_enhancement) {
        const testEnhancement =
          status.request_payload.llm_config.test_enhancement;
        if (testEnhancement.provider) {
          setLlmProvider(testEnhancement.provider);
        }
        if (testEnhancement.model) {
          setLlmModel(testEnhancement.model);
        }
      }

      if (status.request_payload?.llm_config?.payload_enhancement) {
        const payloadEnhancement =
          status.request_payload.llm_config.payload_enhancement;
        if (payloadEnhancement.provider) {
          setPayloadEnhancementProvider(payloadEnhancement.provider);
        }
        if (payloadEnhancement.model) {
          setPayloadEnhancementModel(payloadEnhancement.model);
        }
      }

      console.log("Fetching artifacts");
      // Fetch artifacts (payloads, enhanced payloads, test files, intents, IR)
      try {
        setIsLoadingData(true);
        const artifacts = await fetchJobArtifacts(jobId);
        // Populate pipeline data with artifacts
        setPipelineData((prev) => ({
          ...prev,
          testFiles: artifacts.testFiles || {},
          payloads: artifacts.payloads || [],
          testCases: artifacts.intents || prev.testCases,
        }));

        // If no selected intents were provided by the request, use extracted intents
        if (
          (!status.request_payload ||
            !status.request_payload.target_intents ||
            status.request_payload.target_intents.length === 0) &&
          artifacts.intents &&
          artifacts.intents.length > 0
        ) {
          setSelectedIntents(artifacts.intents.map((i: any) => i.id || i));
        }
      } catch (err) {
        console.error("Failed to fetch artifacts for job:", err);
      } finally {
        setIsLoadingData(false);
      }
    }

    const stepDefinitions = [
      {
        id: 1,
        name: "Parse Specification",
        description: "Parsing the API definition",
      },
      {
        id: 2,
        name: "Build IR",
        description: "Creating intermediate representation",
      },
      {
        id: 3,
        name: "Generate Intents",
        description: "Identifying test scenarios",
      },
      {
        id: 4,
        name: "Generate Payloads",
        description: "Creating request payloads",
      },
      {
        id: 5,
        name: "Generate Test Cases",
        description: "Generating test case files",
      },
      {
        id: 6,
        name: "Save Artifacts",
        description: "Saving artifacts to storage",
      },
    ];

    const stepsCount = stepDefinitions.length;
    const perStep = 100 / stepsCount;

    let stepStates: Record<
      number,
      "pending" | "running" | "completed" | "error"
    > = {};
    for (let i = 1; i <= stepsCount; i++) stepStates[i] = "pending";

    const completedCount = Math.max(
      0,
      Math.min(stepsCount, Math.floor(progress / perStep)),
    );
    for (let i = 1; i <= completedCount; i++) stepStates[i] = "completed";

    let currentRunningStep = -1;
    if (jobStatus === "running") {
      const next = completedCount + 1;
      if (next <= stepsCount) {
        currentRunningStep = next;
        stepStates[currentRunningStep] = "running";
      }
    } else if (jobStatus === "completed") {
      for (let i = 1; i <= stepsCount; i++) stepStates[i] = "completed";
    } else if (jobStatus === "failed") {
      const failedStep = completedCount + 1;
      if (failedStep <= stepsCount) stepStates[failedStep] = "error";
    }

    let currentStep = 1;
    if (jobStatus === "completed") {
      // All steps done, set currentStep beyond the last step
      currentStep = stepsCount + 1;
    } else if (currentRunningStep !== -1) {
      currentStep = currentRunningStep;
    } else {
      currentStep = Math.min(stepsCount, completedCount + 1);
    }

    let endpoints: any[] = status.endpoints || [];
    let testCases: any[] = [];
    let payloads: any[] = [];

    const steps = stepDefinitions.map((d) => ({
      ...d,
      status: stepStates[d.id],
    }));

    setPipelineData((prev) => ({
      ...prev,
      status:
        jobStatus === "failed"
          ? "failed"
          : jobStatus === "completed"
            ? "completed"
            : jobStatus === "running"
              ? "running"
              : "pending",
      currentStep,
      progress: status.progress || 0,
      steps,
      endpoints,
      testCases: prev.testCases || testCases,
      payloads: prev.payloads?.length ? prev.payloads : payloads,
      testFiles: prev.testFiles || {},
    }));

    if (status.error_message) {
      setError(status.error_message);
    }
  };

  const toggleIntent = (intentId: string) => {
    if (intentId === "HAPPY_PATH") return;
    setSelectedIntents((prev) =>
      prev.includes(intentId)
        ? prev.filter((id) => id !== intentId)
        : [...prev, intentId],
    );
  };

  const getCurrentIntents = () => {
    switch (inputType) {
      case "openapi":
        return OPENAPI_INTENTS;
      case "python":
        return PYTHON_INTENTS;
      case "typescript":
        return TYPESCRIPT_INTENTS;
      default:
        return OPENAPI_INTENTS;
    }
  };

  const handleMouseDown = () => setIsDragging(true);
  const handleMouseUp = () => setIsDragging(false);
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    const container = e.currentTarget;
    const rect = container.getBoundingClientRect();
    const newWidth = ((e.clientX - rect.left) / rect.width) * 100;
    if (newWidth > 25 && newWidth < 75) {
      setLeftWidth(newWidth);
    }
  };

  const handleNewSession = () => {
    setSidebarOpen(false);
    router.push("/");
    setCurrentJobId(null);
    setShowResults(false);
    setError(null);
    setApiDefinition("");
    setIsRunning(false);
    // Reset initial load tracking
    initialLoadDoneRef.current = null;
    // Reset to defaults
    setInputType("openapi");
    setOutputLanguage("pytest");
    setSelectedIntents(["HAPPY_PATH"]);
    setBaseUrl("http://localhost:8000");
    setLlmProvider(DEFAULT_TEST_ENHANCEMENT_PROVIDER);
    setLlmModel(DEFAULT_TEST_ENHANCEMENT_MODEL);
    setPayloadEnhancementProvider(DEFAULT_PAYLOAD_ENHANCEMENT_PROVIDER);
    setPayloadEnhancementModel(DEFAULT_PAYLOAD_ENHANCEMENT_MODEL);
  };

  return (
    <div className="h-screen bg-slate-50 flex flex-col">
      <Header
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <SessionsSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        sessions={sessions}
        currentJobId={currentJobId}
        onSelectSession={setCurrentJobId}
        onNewSession={handleNewSession}
        onDeleteSession={(jobId) => {
          setSessions((prev) => prev.filter((s) => s.jobId !== jobId));
          if (currentJobId === jobId) {
            setCurrentJobId(null);
            setShowResults(false);
            setError(null);
            router.push("/");
          }
        }}
      />

      <main
        className="flex-1 flex overflow-hidden relative"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      >
        <div style={{ width: `${leftWidth}%` }}>
          <EditorPanel
            inputType={inputType}
            onInputTypeChange={setInputType}
            apiDefinition={apiDefinition}
            onApiDefinitionChange={setApiDefinition}
            outputLanguage={outputLanguage}
            onOutputLanguageChange={setOutputLanguage}
            selectedIntents={selectedIntents}
            onToggleIntent={toggleIntent}
            onGenerateClick={handleGenerate}
            isRunning={isRunning}
            intents={getCurrentIntents()}
            categories={INTENT_CATEGORIES}
            onFileUpload={handleUploadFile}
          />
        </div>

        <div
          className={`w-1 bg-slate-200 hover:bg-emerald-500 cursor-col-resize shrink-0 relative group transition-colors ${isDragging ? "bg-emerald-500" : ""}`}
          onMouseDown={handleMouseDown}
        >
          <div className="absolute inset-y-0 -left-1 -right-1 flex items-center justify-center">
            <div className="w-1 h-16 bg-slate-300 rounded-full group-hover:bg-emerald-600 transition-colors" />
          </div>
        </div>

        <div style={{ flex: 1 }} className="relative overflow-y-auto min-h-0">
          <OutputPanel
            showResults={showResults}
            isLoadingData={isLoadingData}
            error={error}
            onDismissError={() => setError(null)}
            pipelineData={pipelineData}
            selectedIntents={selectedIntents}
            rightIntentOpen={rightIntentOpen}
            onToggleRightIntent={() => setRightIntentOpen(!rightIntentOpen)}
            onToggleIntent={toggleIntent}
            intents={getCurrentIntents()}
            categories={INTENT_CATEGORIES}
            isRunning={isRunning}
            baseUrl={baseUrl}
            onBaseUrlChange={setBaseUrl}
            hideBaseUrl={inputType === "typescript" || inputType === "python"}
            baseUrlOpen={baseUrlOpen}
            onToggleBaseUrl={() => setBaseUrlOpen(!baseUrlOpen)}
            llmProvider={llmProvider}
            onLlmProviderChange={setLlmProvider}
            llmModel={llmModel}
            onLlmModelChange={setLlmModel}
            payloadEnhancementProvider={payloadEnhancementProvider}
            onPayloadEnhancementProviderChange={setPayloadEnhancementProvider}
            payloadEnhancementModel={payloadEnhancementModel}
            onPayloadEnhancementModelChange={setPayloadEnhancementModel}
            llmConfigOpen={llmConfigOpen}
            onToggleLlmConfig={() => setLlmConfigOpen(!llmConfigOpen)}
            logs={logs}
            isLive={isRunning}
            inputType={inputType}
          />
        </div>
      </main>
    </div>
  );
}

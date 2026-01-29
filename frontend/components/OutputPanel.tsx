import { Zap, AlertCircle } from "lucide-react";
import {
  LLM_PROVIDERS,
  getDefaultModelForProvider,
  getModelsForProvider,
} from "@/lib/llm_config";
import PipelineStatus from "@/components/PipelineStatus";
import IntentSelector from "@/components/IntentSelector";
import EndpointsWidget from "@/components/EndpointsWidget";
import ArtifactsTabs from "@/components/ArtifactsTabs";
import LogViewer from "@/components/LogViewer";
import {
  SkeletonPipelineStatus,
  SkeletonResults,
  SkeletonEndpoints,
} from "@/components/Skeletons";
import { PipelineData } from "@/lib/types";

interface LogEntry {
  message: string;
  log_type: "info" | "debug" | "error";
  created_at: string;
}

interface OutputPanelProps {
  showResults: boolean;
  isLoadingData: boolean;
  error: string | null;
  onDismissError: () => void;
  pipelineData: PipelineData;
  selectedIntents: string[];
  rightIntentOpen: boolean;
  onToggleRightIntent: () => void;
  onToggleIntent: (intentId: string) => void;
  intents: any[];
  categories: any;
  isRunning: boolean;
  baseUrl: string;
  onBaseUrlChange: (value: string) => void;
  hideBaseUrl: boolean;
  baseUrlOpen: boolean;
  onToggleBaseUrl: () => void;
  llmProvider: string;
  onLlmProviderChange: (provider: string) => void;
  llmModel: string;
  onLlmModelChange: (model: string) => void;
  payloadEnhancementProvider: string;
  onPayloadEnhancementProviderChange: (provider: string) => void;
  payloadEnhancementModel: string;
  onPayloadEnhancementModelChange: (model: string) => void;
  llmConfigOpen: boolean;
  onToggleLlmConfig: () => void;
  logs: LogEntry[];
  isLive?: boolean;
  inputType?: "openapi" | "python" | "typescript";
}

export default function OutputPanel({
  showResults,
  isLoadingData,
  error,
  onDismissError,
  pipelineData,
  selectedIntents,
  rightIntentOpen,
  onToggleRightIntent,
  onToggleIntent,
  intents,
  categories,
  isRunning,
  baseUrl,
  onBaseUrlChange,
  hideBaseUrl,
  baseUrlOpen,
  onToggleBaseUrl,
  llmProvider,
  onLlmProviderChange,
  llmModel,
  onLlmModelChange,
  payloadEnhancementProvider,
  onPayloadEnhancementProviderChange,
  payloadEnhancementModel,
  onPayloadEnhancementModelChange,
  llmConfigOpen,
  onToggleLlmConfig,
  logs,
  isLive = false,
  inputType = "openapi",
}: OutputPanelProps) {
  return (
    <div className="flex-1 relative flex flex-col bg-stone-100 overflow-hidden min-h-0">
      <div className="flex-1 overflow-y-auto min-h-0">
        {/* Selected Intents Accordion - Always visible */}
        <div className="p-6">
          <div className="bg-white rounded-lg border border-stone-300 mb-4 shadow-sm">
            <div
              className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-stone-50"
              onClick={onToggleRightIntent}
            >
              <div>
                <div className="text-sm font-medium text-stone-800">
                  Select Intents
                </div>
                <div className="text-xs text-stone-500">
                  {selectedIntents.length} selected
                </div>
              </div>
              <div className="text-xs text-stone-500">
                {rightIntentOpen ? (
                  <img
                    width="14"
                    height="14"
                    className="rotate-90"
                    src="https://img.icons8.com/ios-filled/50/79716b/play--v1.png"
                    alt="play--v1"
                  />
                ) : (
                  <img
                    width="14"
                    height="14"
                    src="https://img.icons8.com/ios-filled/50/79716b/play--v1.png"
                    alt="play--v1"
                  />
                )}
              </div>
            </div>
            {rightIntentOpen && (
              <div className="p-4 border-t border-stone-200">
                <IntentSelector
                  intents={intents}
                  selectedIntents={selectedIntents}
                  onToggle={onToggleIntent}
                  categories={categories}
                />
              </div>
            )}
          </div>

          {/* API Base URL and LLM Configuration in same row */}
          <div className="gap-4 flex justify-between w-full h-auto">
            {/* API Base URL Accordion */}
            {!hideBaseUrl && (
              <div className="bg-white w-full rounded-lg border border-stone-300 shadow-sm">
                <div
                  className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-stone-50"
                  onClick={onToggleBaseUrl}
                >
                  <div>
                    <div className="text-sm font-medium text-stone-800">
                      API Base URL
                    </div>
                    <div className="text-xs text-stone-500">
                      For test execution
                    </div>
                  </div>
                  <div className="text-xs text-stone-500">
                    {baseUrlOpen ? (
                      <img
                        width="14"
                        height="14"
                        className="rotate-90"
                        src="https://img.icons8.com/ios-filled/50/79716b/play--v1.png"
                        alt="play--v1"
                      />
                    ) : (
                      <img
                        width="14"
                        height="14"
                        src="https://img.icons8.com/ios-filled/50/79716b/play--v1.png"
                        alt="play--v1"
                      />
                    )}
                  </div>
                </div>
                {baseUrlOpen && (
                  <div className="p-4 border-t border-stone-200">
                    <label
                      className="block text-xs font-semibold text-stone-600 mb-2"
                      htmlFor="base-url-input"
                    >
                      Base URL
                    </label>
                    <input
                      id="base-url-input"
                      type="url"
                      className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 shadow-sm focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 outline-none"
                      placeholder="https://api.example.com"
                      value={baseUrl}
                      onChange={(e) => onBaseUrlChange(e.target.value)}
                    />
                  </div>
                )}
              </div>
            )}

            {/* LLM Configuration Accordion */}
            <div className="bg-white w-full rounded-lg border border-stone-300 shadow-sm">
              <div
                className="flex items-center justify-between px-4 py-3 cursor-pointer hover:bg-stone-50"
                onClick={onToggleLlmConfig}
              >
                <div>
                  <div className="text-sm font-medium text-stone-800">
                    LLM Configuration
                  </div>
                  <div className="text-xs text-stone-500">
                    Configure payload & test enhancement
                  </div>
                </div>
                <div className="text-xs text-stone-500">
                  {llmConfigOpen ? (
                    <img
                      width="14"
                      height="14"
                      className="rotate-90"
                      src="https://img.icons8.com/ios-filled/50/79716b/play--v1.png"
                      alt="play--v1"
                    />
                  ) : (
                    <img
                      width="14"
                      height="14"
                      src="https://img.icons8.com/ios-filled/50/79716b/play--v1.png"
                      alt="play--v1"
                    />
                  )}
                </div>
              </div>
              {llmConfigOpen && (
                <div className="p-4 border-t border-stone-200 space-y-6">
                  {/* Payload Enhancement Config */}
                  <div className="space-y-4">
                    <h4 className="text-xs font-bold text-stone-900 uppercase tracking-wider pb-2 border-b border-stone-100">
                      Payload Enhancement
                    </h4>
                    <div>
                      <label
                        className="block text-xs font-semibold text-stone-600 mb-2"
                        htmlFor="payload-provider"
                      >
                        Provider
                      </label>
                      <select
                        id="payload-provider"
                        className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 shadow-sm focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 outline-none"
                        value={payloadEnhancementProvider}
                        onChange={(e) => {
                          onPayloadEnhancementProviderChange(e.target.value);
                          onPayloadEnhancementModelChange(
                            getDefaultModelForProvider(e.target.value),
                          );
                        }}
                      >
                        {LLM_PROVIDERS.map((provider) => (
                          <option key={provider.value} value={provider.value}>
                            {provider.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label
                        className="block text-xs font-semibold text-stone-600 mb-2"
                        htmlFor="payload-model"
                      >
                        Model
                      </label>
                      <select
                        id="payload-model"
                        className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 shadow-sm focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 outline-none"
                        value={payloadEnhancementModel}
                        onChange={(e) =>
                          onPayloadEnhancementModelChange(e.target.value)
                        }
                      >
                        {getModelsForProvider(payloadEnhancementProvider).map(
                          (model) => (
                            <option key={model.value} value={model.value}>
                              {model.label}
                            </option>
                          ),
                        )}
                      </select>
                    </div>
                  </div>

                  {/* Test Enhancement Config */}
                  <div className="space-y-4">
                    <h4 className="text-xs font-bold text-stone-900 uppercase tracking-wider pb-2 border-b border-stone-100">
                      Test Enhancement
                    </h4>
                    <div>
                      <label
                        className="block text-xs font-semibold text-stone-600 mb-2"
                        htmlFor="llm-provider"
                      >
                        Provider
                      </label>
                      <select
                        id="llm-provider"
                        className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 shadow-sm focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 outline-none"
                        value={llmProvider}
                        onChange={(e) => {
                          onLlmProviderChange(e.target.value);
                          onLlmModelChange(
                            getDefaultModelForProvider(e.target.value),
                          );
                        }}
                      >
                        {LLM_PROVIDERS.map((provider) => (
                          <option key={provider.value} value={provider.value}>
                            {provider.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label
                        className="block text-xs font-semibold text-stone-600 mb-2"
                        htmlFor="llm-model"
                      >
                        Model
                      </label>
                      <select
                        id="llm-model"
                        className="w-full rounded-md border border-stone-300 bg-white px-3 py-2 text-sm text-stone-800 shadow-sm focus:border-emerald-600 focus:ring-2 focus:ring-emerald-200 outline-none"
                        value={llmModel}
                        onChange={(e) => onLlmModelChange(e.target.value)}
                      >
                        {getModelsForProvider(llmProvider).map((model) => (
                          <option key={model.value} value={model.value}>
                            {model.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {!showResults ? (
          <div className="h-full flex items-center justify-center p-8">
            <div className="text-center max-w-md">
              <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-emerald-200 to-emerald-300 rounded-2xl mb-4">
                <Zap className="w-10 h-10 text-emerald-800" />
              </div>
              <h3 className="text-xl font-bold text-stone-900 mb-2">
                Ready to Generate
              </h3>
              <p className="text-sm text-stone-600 leading-relaxed">
                Provide your API definition, select test intents, and click
                Generate to create comprehensive test suites with realistic mock
                data.
              </p>
            </div>
          </div>
        ) : (
          <div className="p-6 pb-6">
            {/* Error Display */}
            {error && (
              <div className="bg-rose-50 border border-rose-300 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-rose-700 shrink-0 mt-0.5" />
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-rose-900 mb-1">
                    Error
                  </h4>
                  <p className="text-sm text-rose-700">{error}</p>
                </div>
                <button
                  onClick={onDismissError}
                  className="text-rose-700 hover:text-rose-800 text-sm font-medium"
                >
                  Dismiss
                </button>
              </div>
            )}

            {/* Log Viewer - Above Pipeline Status */}
            {logs.length > 0 && <LogViewer logs={logs} isLive={isLive} />}

            {/* Pipeline Status */}
            {showResults && (
              <>
                {isLoadingData ? (
                  <SkeletonPipelineStatus />
                ) : (
                  <PipelineStatus data={pipelineData} />
                )}

                {/* Show endpoints widget */}
                {isLoadingData ? (
                  <SkeletonEndpoints />
                ) : (
                  pipelineData.endpoints &&
                  pipelineData.endpoints.length > 0 && (
                    <EndpointsWidget
                      endpoints={pipelineData.endpoints}
                      inputType={inputType}
                    />
                  )
                )}

                {/* {pipelineData.status === "completed" ? null : isRunning ? (
                  <SkeletonResults />
                ) : null} */}

                {/* Show artifacts whenever we have them */}
                <ArtifactsTabs
                  testFiles={pipelineData.testFiles || {}}
                  payloads={pipelineData.payloads || []}
                  isLoading={isLoadingData || isRunning}
                  inputType={inputType}
                />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

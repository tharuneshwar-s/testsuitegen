/**
 * LLM Configuration Constants
 * Centralized configuration for LLM providers and models used across the application.
 */

export interface LLMModel {
  value: string;
  label: string;
}

export interface LLMProvider {
  value: string;
  label: string;
  models: LLMModel[];
  defaultModel: string;
}

export const LLM_PROVIDERS: LLMProvider[] = [
  {
    value: "lmstudio",
    label: "LM Studio",
    models: [
      { value: "qwen2.5-coder-1.5b-instruct", label: "qwen2.5-coder-1.5b-instruct" },
      { value: "meta-llama-3.1-8b-instruct", label: "meta-llama-3.1-8b-instruct" },
      { value: "qwen2-nextgen-8b", label: "qwen2-nextgen-8b" },
      { value: "qwen2.5-3b-instruct", label: "qwen2.5-3b-instruct" },
      { value: "qwen3-0.6b", label: "qwen3-0.6b" },
    ],
    defaultModel: "qwen2.5-coder-1.5b-instruct",
  },
  {
    value: "vllm",
    label: "vLLM",
    models: [
      { value: "Qwen/Qwen2.5-Coder-1.5B-Instruct", label: "Qwen/Qwen2.5-Coder-1.5B-Instruct" },
      { value: "Qwen/Qwen2.5-Coder-3B-Instruct", label: "Qwen/Qwen2.5-Coder-3B-Instruct" },
    ],
    defaultModel: "Qwen/Qwen2.5-Coder-1.5B-Instruct",
  },
  {
    value: "groq",
    label: "Groq",
    models: [
      { value: "openai/gpt-oss-20b", label: "openai/gpt-oss-20b" },
      { value: "moonshotai/kimi-k2-instruct", label: "moonshotai/kimi-k2-instruct" },
      { value: "llama-3.3-70b-versatile", label: "llama-3.3-70b-versatile" },
    ],
    defaultModel: "openai/gpt-oss-20b",
  },
  {
    value: "gemini",
    label: "Gemini",
    models: [
      { value: "gemini-2.5-flash", label: "gemini-2.5-flash" },
      { value: "gemini-2.5-flash-lite", label: "gemini-2.5-flash-lite" },
      { value: "gemini-2.0-flash", label: "gemini-2.0-flash" },
    ],
    defaultModel: "gemini-2.5-flash",
  },
];

/**
 * Get the default model for a given provider.
 */
export function getDefaultModelForProvider(providerValue: string): string {
  const provider = LLM_PROVIDERS.find((p) => p.value === providerValue);
  return provider?.defaultModel || LLM_PROVIDERS[0].defaultModel;
}

/**
 * Get the models for a given provider.
 */
export function getModelsForProvider(providerValue: string): LLMModel[] {
  const provider = LLM_PROVIDERS.find((p) => p.value === providerValue);
  return provider?.models || [];
}

// Default configuration
export const DEFAULT_PAYLOAD_ENHANCEMENT_PROVIDER = "vllm";
export const DEFAULT_PAYLOAD_ENHANCEMENT_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct";
export const DEFAULT_TEST_ENHANCEMENT_PROVIDER = "vllm";
export const DEFAULT_TEST_ENHANCEMENT_MODEL = "Qwen/Qwen2.5-Coder-1.5B-Instruct";

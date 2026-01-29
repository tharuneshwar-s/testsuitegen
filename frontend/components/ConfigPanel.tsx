"use client";

import { useState } from "react";
import { Upload, Server, Brain, Settings2 } from "lucide-react";

export default function ConfigPanel() {
  const [config, setConfig] = useState({
    specPath: "openapi.yaml",
    outputDir: "artifacts",
    baseUrl: "http://localhost:8000",
    useLLM: true,
    llmProvider: "lmstudio",
    llmModel: "meta-llama-3.1-8b-instruct",
    maxTokens: "8000",
  });

  return (
    <div className="space-y-5">
      {/* OpenAPI Spec Section */}
      <div className="bg-white rounded-lg p-5 border border-slate-200">
        <div className="flex items-center gap-2 mb-4">
          <Upload className="w-4 h-4 text-blue-600" />
          <h3 className="text-base font-medium text-slate-900">
            OpenAPI Specification
          </h3>
        </div>
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Spec File Path
            </label>
            <input
              type="text"
              value={config.specPath}
              onChange={(e) => setConfig({ ...config, specPath: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              placeholder="path/to/openapi.yaml"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              Output Directory
            </label>
            <input
              type="text"
              value={config.outputDir}
              onChange={(e) => setConfig({ ...config, outputDir: e.target.value })}
              className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              placeholder="artifacts"
            />
          </div>
        </div>
      </div>

      {/* API Configuration */}
      <div className="bg-white rounded-lg p-5 border border-slate-200">
        <div className="flex items-center gap-2 mb-4">
          <Server className="w-4 h-4 text-green-600" />
          <h3 className="text-base font-medium text-slate-900">
            API Configuration
          </h3>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Base URL
          </label>
          <input
            type="text"
            value={config.baseUrl}
            onChange={(e) => setConfig({ ...config, baseUrl: e.target.value })}
            className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
            placeholder="http://localhost:8000"
          />
        </div>
      </div>

      {/* LLM Configuration */}
      <div className="bg-white rounded-lg p-5 border border-slate-200">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-600" />
            <h3 className="text-base font-medium text-slate-900">
              LLM Enhancement
            </h3>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={config.useLLM}
              onChange={(e) => setConfig({ ...config, useLLM: e.target.checked })}
              className="sr-only peer"
            />
            <div className="w-10 h-5 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        {config.useLLM && (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                LLM Provider
              </label>
              <select
                value={config.llmProvider}
                onChange={(e) => setConfig({ ...config, llmProvider: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
              >
                <option value="lmstudio">LM Studio (Local)</option>
                <option value="gemini">Google Gemini</option>
                <option value="groq">Groq</option>
                <option value="airllm">AirLLM</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                Model
              </label>
              <input
                type="text"
                value={config.llmModel}
                onChange={(e) => setConfig({ ...config, llmModel: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
                placeholder="meta-llama-3.1-8b-instruct"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                Max Tokens
              </label>
              <input
                type="text"
                value={config.maxTokens}
                onChange={(e) => setConfig({ ...config, maxTokens: e.target.value })}
                className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-white text-slate-900 text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow"
                placeholder="8000"
              />
            </div>
          </div>
        )}
      </div>

      {/* Advanced Settings */}
      <div className="bg-slate-50 rounded-lg p-5 border border-slate-200">
        <div className="flex items-center gap-2 mb-4">
          <Settings2 className="w-4 h-4 text-slate-600" />
          <h3 className="text-base font-medium text-slate-900">
            Advanced Settings
          </h3>
        </div>
        <div className="space-y-2.5 text-sm text-slate-600">
          <div className="flex justify-between items-center">
            <span>Circuit Breaker Threshold</span>
            <span className="font-mono text-slate-900">5 failures</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Max LLM Retries</span>
            <span className="font-mono text-slate-900">3 attempts</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Exponential Backoff Base</span>
            <span className="font-mono text-slate-900">2 seconds</span>
          </div>
        </div>
      </div>
    </div>
  );
}

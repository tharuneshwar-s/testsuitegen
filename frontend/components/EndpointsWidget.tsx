"use client";

import { useState } from "react";
import {
  Globe,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Filter,
} from "lucide-react";

interface EndpointInput {
  path?: Array<{ name: string; required?: boolean; schema?: any }>;
  query?: Array<{ name: string; required?: boolean; schema?: any }>;
  headers?: Array<{ name: string; required?: boolean; schema?: any }>;
  body?: {
    content_type?: string;
    required?: boolean;
    schema?: any;
  };
}

interface EndpointOutput {
  status: number;
  description?: string;
  content_type?: string | null;
  schema?: any;
}

interface Endpoint {
  id?: string;
  method: string;
  path: string;
  summary?: string;
  operation_id?: string;
  inputs?: EndpointInput;
  outputs?: EndpointOutput[];
}

interface EndpointsWidgetProps {
  endpoints: Endpoint[];
  inputType?: "openapi" | "python" | "typescript";
}

export default function EndpointsWidget({
  endpoints,
  inputType = "openapi",
}: EndpointsWidgetProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  /**
   * Extracts a human-readable type label from a JSON Schema property.
   * Prioritizes custom type names from x-enum-type, $ref, or description patterns.
   */
  const getSchemaTypeLabel = (prop: any): string => {
    if (!prop) return "any";

    // 1. Check for custom enum type reference (from parser)
    if (prop["x-enum-type"]) {
      return prop["x-enum-type"];
    }

    // 2. Check for custom class type reference (from LLM enhancer)
    if (prop["x-class-type"]) {
      return prop["x-class-type"];
    }

    // 3. Check for $ref (model reference)
    if (prop["$ref"]) {
      // Extract type name from "#/types/TypeName" or similar
      const refMatch = prop["$ref"].match(/\/([^/]+)$/);
      if (refMatch) return refMatch[1];
    }

    // 3. Check description for "Class: X" or "Enum: X" patterns
    if (prop.description) {
      const classMatch = prop.description.match(
        /^(?:Class|Enum|Type):\s*(\w+)/i,
      );
      if (classMatch) return classMatch[1];

      // Also check for "Complex type: X" pattern from fallback
      const complexMatch = prop.description.match(/^Complex type:\s*(\w+)/i);
      if (complexMatch) return complexMatch[1];
    }

    // 4. Format array types with items type
    if (prop.type === "array" && prop.items) {
      const itemType = getSchemaTypeLabel(prop.items);
      return `${itemType}[]`;
    }

    // 5. Format object types that have additionalProperties
    if (prop.type === "object" && prop.additionalProperties) {
      const valueType = getSchemaTypeLabel(prop.additionalProperties);
      return `Dict[${valueType}]`;
    }

    // 6. Return primitive type or fallback
    return prop.type || "any";
  };
  const [expandedEndpoints, setExpandedEndpoints] = useState<Set<number>>(
    new Set(),
  );
  const [methodFilters, setMethodFilters] = useState<Record<string, boolean>>({
    GET: true,
    POST: true,
    PUT: true,
    PATCH: true,
    DELETE: true,
    FUNC: true,
    MODEL: true,
    ENUM: true,
  });

  if (!endpoints || endpoints.length === 0) return null;

  const toggleMethodFilter = (method: string) => {
    setMethodFilters((prev) => ({ ...prev, [method]: !prev[method] }));
  };

  // Count endpoints by method
  const methodCounts = {
    GET: endpoints.filter((e) => e.method?.toUpperCase() === "GET").length,
    POST: endpoints.filter((e) => e.method?.toUpperCase() === "POST").length,
    PUT: endpoints.filter((e) => e.method?.toUpperCase() === "PUT").length,
    PATCH: endpoints.filter((e) => e.method?.toUpperCase() === "PATCH").length,
    DELETE: endpoints.filter((e) => e.method?.toUpperCase() === "DELETE")
      .length,
    FUNC: endpoints.filter((e) => e.method === "FUNC").length,
    MODEL: endpoints.filter((e) => e.method === "MODEL").length,
    ENUM: endpoints.filter((e) => e.method === "ENUM").length,
  };

  // Filter endpoints based on selected filters
  const visibleEndpoints = endpoints.filter(
    (endpoint) =>
      methodFilters[endpoint.method?.toUpperCase() || endpoint.method] ?? true,
  );

  const toggleEndpoint = (idx: number) => {
    setExpandedEndpoints((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) {
        next.delete(idx);
      } else {
        next.add(idx);
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
      // Specialized colors for Types
      MODEL: "bg-indigo-700 text-indigo-50",
      ENUM: "bg-teal-700 text-teal-50",
      FUNC: "bg-stone-600 text-stone-50",
    };

    if (inputType === "openapi" && !["MODEL", "ENUM"].includes(method)) {
      return colors[method?.toUpperCase()] || "bg-stone-600 text-stone-50";
    }

    if (colors[method]) return colors[method];

    // Deterministic random color for functions based on name/method string
    const seed = method
      .split("")
      .reduce((acc, char) => acc + char.charCodeAt(0), 0);
    const variants = [
      "bg-slate-700 text-slate-50",
      "bg-zinc-700 text-zinc-50",
      "bg-neutral-700 text-neutral-50",
      "bg-stone-700 text-stone-50",
      "bg-red-700 text-red-50",
      "bg-orange-700 text-orange-50",
      "bg-amber-700 text-amber-50",
      "bg-yellow-700 text-yellow-50",
      "bg-lime-700 text-lime-50",
      "bg-green-700 text-green-50",
      "bg-emerald-700 text-emerald-50",
      "bg-teal-700 text-teal-50",
      "bg-cyan-700 text-cyan-50",
      "bg-sky-700 text-sky-50",
      "bg-blue-700 text-blue-50",
      "bg-indigo-700 text-indigo-50",
      "bg-violet-700 text-violet-50",
      "bg-purple-700 text-purple-50",
      "bg-fuchsia-700 text-fuchsia-50",
      "bg-pink-700 text-pink-50",
      "bg-rose-700 text-rose-50",
    ];
    return variants[seed % variants.length];
  };

  const hasDetails = (endpoint: Endpoint) => {
    // Models/Enums always have details (schema)
    if (["MODEL", "ENUM"].includes(endpoint.method)) return true;

    const hasInputs =
      endpoint.inputs &&
      ((endpoint.inputs.path && endpoint.inputs.path.length > 0) ||
        (endpoint.inputs.query && endpoint.inputs.query.length > 0) ||
        (endpoint.inputs.body && endpoint.inputs.body.schema));
    const hasOutputs = endpoint.outputs && endpoint.outputs.length > 0;
    return hasInputs || hasOutputs;
  };

  return (
    <div className="bg-stone-50 rounded-lg border border-stone-300 overflow-hidden shadow-sm mb-4">
      {/* Header - collapsible */}
      <div
        className="flex items-center justify-between px-4 py-3 bg-stone-100 border-b border-stone-200 cursor-pointer hover:bg-stone-150"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-emerald-800" />
          <h3 className="text-sm font-semibold text-stone-800">
            {inputType === "openapi" ? "API Endpoints" : "Functions & Types"}
          </h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-800 text-emerald-50 font-medium">
            {visibleEndpoints.length !== endpoints.length
              ? `${visibleEndpoints.length}/${endpoints.length}`
              : endpoints.length}
          </span>
        </div>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 text-stone-500" />
        ) : (
          <ChevronDown className="w-4 h-4 text-stone-500" />
        )}
      </div>

      {/* Expandable content */}
      {isExpanded && (
        <>
          {/* Filter Bar */}
          <div className="flex items-center gap-2 px-4 py-2 bg-stone-50 border-b border-stone-200">
            <Filter className="w-3.5 h-3.5 text-stone-500" />
            <span className="text-xs text-stone-600">Filter:</span>
            <div className="flex gap-1.5 flex-wrap">
              {inputType === "openapi" ? (
                <>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMethodFilter("GET");
                    }}
                    className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                      methodFilters.GET
                        ? "bg-sky-100 text-sky-800 border-sky-300"
                        : "bg-stone-100 text-stone-500 border-stone-300"
                    }`}
                  >
                    GET ({methodCounts.GET})
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMethodFilter("POST");
                    }}
                    className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                      methodFilters.POST
                        ? "bg-emerald-100 text-emerald-800 border-emerald-300"
                        : "bg-stone-100 text-stone-500 border-stone-300"
                    }`}
                  >
                    POST ({methodCounts.POST})
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMethodFilter("PUT");
                    }}
                    className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                      methodFilters.PUT
                        ? "bg-amber-100 text-amber-800 border-amber-300"
                        : "bg-stone-100 text-stone-500 border-stone-300"
                    }`}
                  >
                    PUT ({methodCounts.PUT})
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMethodFilter("PATCH");
                    }}
                    className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                      methodFilters.PATCH
                        ? "bg-orange-100 text-orange-800 border-orange-300"
                        : "bg-stone-100 text-stone-500 border-stone-300"
                    }`}
                  >
                    PATCH ({methodCounts.PATCH})
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleMethodFilter("DELETE");
                    }}
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
                <>
                  {/* Python Filters */}
                  {methodCounts.FUNC > 0 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMethodFilter("FUNC");
                      }}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.FUNC
                          ? "bg-stone-200 text-stone-800 border-stone-400"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      Functions ({methodCounts.FUNC})
                    </button>
                  )}
                  {methodCounts.MODEL > 0 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMethodFilter("MODEL");
                      }}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.MODEL
                          ? "bg-indigo-100 text-indigo-800 border-indigo-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      Classes ({methodCounts.MODEL})
                    </button>
                  )}
                  {methodCounts.ENUM > 0 && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        toggleMethodFilter("ENUM");
                      }}
                      className={`flex items-center gap-1 px-2 py-1 text-xs font-medium rounded border transition-colors ${
                        methodFilters.ENUM
                          ? "bg-teal-100 text-teal-800 border-teal-300"
                          : "bg-stone-100 text-stone-500 border-stone-300"
                      }`}
                    >
                      Enums ({methodCounts.ENUM})
                    </button>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Endpoints List */}
          <div className="divide-y divide-stone-200">
            {visibleEndpoints.map((endpoint, idx) => (
              <div key={endpoint.id || idx} className="bg-white">
                <div
                  className={`flex items-center gap-3 px-4 py-3 transition-colors ${hasDetails(endpoint) ? "cursor-pointer hover:bg-stone-50" : ""}`}
                  onClick={() => hasDetails(endpoint) && toggleEndpoint(idx)}
                >
                  {hasDetails(endpoint) &&
                    (expandedEndpoints.has(idx) ? (
                      <ChevronDown className="w-4 h-4 text-stone-500" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-stone-500" />
                    ))}
                  {!hasDetails(endpoint) && <div className="w-4" />}

                  <span
                    className={`w-16 text-center px-2 py-0.5 text-xs font-mono font-semibold rounded ${getMethodColor(inputType === "openapi" ? endpoint.method : endpoint.path)}`}
                  >
                    {inputType === "openapi"
                      ? endpoint.method
                      : inputType === "python"
                        ? endpoint.method === "FUNC"
                          ? "def"
                          : endpoint.method === "MODEL"
                            ? "class"
                            : "enum"
                        : "fn"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="font-mono text-sm text-stone-800 truncate">
                      {endpoint.path}
                    </div>
                    {(endpoint.summary || (endpoint as any).description) && (
                      <div className="text-xs text-stone-500 mt-0.5 line-clamp-2">
                        {endpoint.summary || (endpoint as any).description}
                      </div>
                    )}
                  </div>
                </div>

                {/* Expanded Details */}
                {expandedEndpoints.has(idx) && hasDetails(endpoint) && (
                  <div className="px-4 pb-4 bg-stone-50 border-t border-stone-200">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                      {/* Request Section */}
                      <div
                        className={
                          endpoint.method === "MODEL" ||
                          endpoint.method === "ENUM"
                            ? "col-span-2"
                            : ""
                        }
                      >
                        <h4 className="text-xs font-semibold text-stone-600 uppercase tracking-wide mb-2">
                          {endpoint.method === "MODEL"
                            ? "Fields"
                            : endpoint.method === "ENUM"
                              ? "Values"
                              : "Request"}
                        </h4>
                        <div className="space-y-2">
                          {/* Path Parameters */}
                          {endpoint.inputs?.path &&
                            endpoint.inputs.path.length > 0 && (
                              <div className="bg-white rounded border border-stone-200 p-2">
                                <div className="text-xs font-medium text-stone-500 mb-1">
                                  Path Parameters
                                </div>
                                <div className="space-y-1">
                                  {endpoint.inputs.path.map((param, i) => (
                                    <div
                                      key={i}
                                      className="flex items-center gap-2 text-xs"
                                    >
                                      <span className="font-mono text-stone-800">
                                        {param.name}
                                      </span>
                                      {param.required && (
                                        <span className="text-rose-600">*</span>
                                      )}
                                      <span className="text-stone-400">
                                        {getSchemaTypeLabel(param.schema)}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                          {/* Query Parameters */}
                          {endpoint.inputs?.query &&
                            endpoint.inputs.query.length > 0 && (
                              <div className="bg-white rounded border border-stone-200 p-2">
                                <div className="text-xs font-medium text-stone-500 mb-1">
                                  Query Parameters
                                </div>
                                <div className="space-y-1">
                                  {endpoint.inputs.query.map((param, i) => (
                                    <div
                                      key={i}
                                      className="flex items-center gap-2 text-xs"
                                    >
                                      <span className="font-mono text-stone-800">
                                        {param.name}
                                      </span>
                                      {param.required && (
                                        <span className="text-rose-600">*</span>
                                      )}
                                      <span className="text-stone-400">
                                        {getSchemaTypeLabel(param.schema)}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                          {/* Request Body / Function Arguments / Model Fields */}
                          {endpoint.inputs?.body?.schema && (
                            <div className="bg-white rounded border border-stone-200 p-2">
                              {endpoint.method !== "MODEL" &&
                                endpoint.method !== "ENUM" && (
                                  <div className="text-xs font-medium text-stone-500 mb-1">
                                    {inputType === "openapi"
                                      ? "Body"
                                      : "Parameters"}{" "}
                                    {endpoint.inputs.body.content_type && (
                                      <span className="text-stone-400">
                                        ({endpoint.inputs.body.content_type})
                                      </span>
                                    )}
                                  </div>
                                )}

                              {/* RENDER MODEL FIELDS */}
                              {(inputType !== "openapi" &&
                                endpoint.inputs.body.schema.properties) ||
                              endpoint.method === "MODEL" ? (
                                <div className="space-y-1">
                                  {Object.entries(
                                    endpoint.inputs.body.schema.properties ||
                                      {},
                                  ).map(([name, prop]: [string, any], i) => (
                                    <div
                                      key={i}
                                      className="flex items-start gap-2 text-xs py-1 border-b border-stone-50 last:border-0"
                                    >
                                      <div className="min-w-[100px]">
                                        <span className="font-mono text-stone-800 font-medium">
                                          {name}
                                        </span>
                                        {endpoint.inputs?.body?.schema?.required?.includes(
                                          name,
                                        ) && (
                                          <span className="text-rose-600 ml-0.5">
                                            *
                                          </span>
                                        )}
                                      </div>
                                      <div className="flex-1">
                                        <span className="text-emerald-700 bg-emerald-50 px-1.5 rounded border border-emerald-100 font-mono text-[10px]">
                                          {getSchemaTypeLabel(prop)}
                                          {prop.format
                                            ? `(${prop.format})`
                                            : ""}
                                        </span>
                                        {prop.description && (
                                          <div className="text-stone-500 mt-0.5">
                                            {prop.description}
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  ))}
                                  {Object.keys(
                                    endpoint.inputs.body.schema.properties ||
                                      {},
                                  ).length === 0 && (
                                    <div className="text-stone-400 italic text-xs">
                                      No fields
                                    </div>
                                  )}
                                </div>
                              ) : endpoint.method === "ENUM" ? (
                                /* RENDER ENUM VALUES */
                                <div className="space-y-1">
                                  {(endpoint.inputs.body.schema as any)[
                                    "x-enum-values"
                                  ]?.map((val: any, i: number) => (
                                    <div
                                      key={i}
                                      className="flex items-center gap-4 text-xs py-1 border-b border-stone-50 last:border-0"
                                    >
                                      <span className="font-mono text-teal-800 font-bold w-32">
                                        {val.name}
                                      </span>
                                      <span className="font-mono text-stone-500">
                                        = {String(val.value)}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                /* Render Raw JSON for OpenAPI Body */
                                <pre className="bg-stone-900 text-stone-100 rounded p-2 overflow-x-auto text-xs font-mono max-h-32 overflow-y-auto">
                                  {JSON.stringify(
                                    endpoint.inputs.body.schema,
                                    null,
                                    2,
                                  )}
                                </pre>
                              )}
                            </div>
                          )}

                          {/* No request data */}
                          {!endpoint.inputs?.path?.length &&
                            !endpoint.inputs?.query?.length &&
                            !endpoint.inputs?.body?.schema && (
                              <div className="text-xs text-stone-400 italic">
                                No parameters
                              </div>
                            )}
                        </div>
                      </div>

                      {/* Response Section - Only for OpenAPI */}
                      {inputType === "openapi" && (
                        <div>
                          <h4 className="text-xs font-semibold text-stone-600 uppercase tracking-wide mb-2">
                            Responses
                          </h4>
                          <div className="space-y-2">
                            {endpoint.outputs && endpoint.outputs.length > 0 ? (
                              endpoint.outputs.map((output, i) => (
                                <div
                                  key={i}
                                  className="bg-white rounded border border-stone-200 p-2"
                                >
                                  <div className="flex items-center gap-2 mb-1">
                                    <span
                                      className={`px-1.5 py-0.5 text-xs font-mono font-semibold rounded ${
                                        output.status >= 200 &&
                                        output.status < 300
                                          ? "bg-emerald-100 text-emerald-800"
                                          : output.status >= 400
                                            ? "bg-rose-100 text-rose-800"
                                            : "bg-amber-100 text-amber-800"
                                      }`}
                                    >
                                      {output.status}
                                    </span>
                                    {output.description && (
                                      <span className="text-xs text-stone-600">
                                        {output.description}
                                      </span>
                                    )}
                                  </div>
                                  {output.schema && (
                                    <pre className="bg-stone-900 text-emerald-300 rounded p-2 overflow-x-auto text-xs font-mono max-h-32 overflow-y-auto">
                                      {JSON.stringify(output.schema, null, 2)}
                                    </pre>
                                  )}
                                </div>
                              ))
                            ) : (
                              <div className="text-xs text-stone-400 italic">
                                No response schema defined
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

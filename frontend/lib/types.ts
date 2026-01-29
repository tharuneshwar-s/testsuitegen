export type StepStatus = "pending" | "running" | "completed" | "error";

export interface Endpoint {
  id?: string;
  method: string;
  path: string;
  summary?: string;
  operation_id?: string;
}

export interface PipelineData {
  status: string;
  currentStep: number;
  progress?: number;
  steps: {
    id: number;
    name: string;
    description: string;
    status: StepStatus;
  }[];
  endpoints?: Endpoint[];
  testCases: {
    id: string;
    name: string;
    intent: string;
    description: string;
  }[];
  testFiles?: Record<string, string>;
  payloads?: Array<{
    intent?: string;
    operation?: string;
    method?: string;
    path?: string;
    payload?: any;
    request_body?: any;
    response?: any;
  }>;
}

export const INITIAL_PIPELINE_DATA: PipelineData = {
  status: "idle",
  currentStep: 0,
  steps: [
    { id: 1, name: "Parse Specification", description: "Parsing the API definition", status: "pending" },
    { id: 2, name: "Build IR", description: "Creating intermediate representation", status: "pending" },
    { id: 3, name: "Generate Intents", description: "Identifying test scenarios", status: "pending" },
    { id: 4, name: "Generate Payloads", description: "Creating request payloads", status: "pending" },
    { id: 5, name: "Generate Test Cases", description: "Generating test case files", status: "pending" },
    { id: 6, name: "Save Artifacts", description: "Saving artifacts to storage", status: "pending" },
  ],
  endpoints: [],
  testCases: [],
};

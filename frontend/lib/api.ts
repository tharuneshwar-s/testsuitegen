'use client'

import { createClient, RealtimeChannel } from "@supabase/supabase-js";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "";
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const SUPABASE_STORAGE_BUCKET = "testsuitegen-artifacts";

// Initialize Supabase client for realtime
const supabase = SUPABASE_URL && SUPABASE_ANON_KEY
  ? createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      // Realtime config keeps channels healthy under reconnects
      realtime: {
        params: {
          eventsPerSecond: 2,
        },
      },
    })
  : null;

// Retry configuration
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;

/**
 * Convert string to base64
 */
function stringToBase64(str: string): string {
  return Buffer.from(str, 'utf-8').toString('base64');
}

/**
 * Convert base64 to string
 */
export function base64ToString(str: string): string {
  try {
    return Buffer.from(str, 'base64').toString('utf-8');
  } catch (error) {
    console.error('Failed to decode base64:', error);
    return str; // Return original string if decoding fails
  }
}

/**
 * Retry helper with exponential backoff
 */
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  retries = MAX_RETRIES,
  delay = RETRY_DELAY_MS
): Promise<T> {
  try {
    return await fn();
  } catch (error: any) {
    if (retries === 0) throw error;
    
    // Don't retry on client errors (4xx)
    if (error.status >= 400 && error.status < 500) {
      throw error;
    }
    
    // Wait with exponential backoff
    await new Promise(resolve => setTimeout(resolve, delay));
    return retryWithBackoff(fn, retries - 1, delay * 2);
  }
}

export interface JobRequest {
  spec_data: string;
  source_type: "openapi" | "python" | "typescript";
  framework?: "pytest" | "jest";
  base_url?: string;
  target_intents?: string[];
  llm_config?: {
    payload_enhancement?: {
      provider: string;
      model?: string;
    };
    test_enhancement?: {
      provider: string;
      model?: string;
    };
  };
  custom_payloads?: any[];
}

export interface JobResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface JobStatus {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  created_at: string;
  updated_at: string;
  logs: Array<{
    timestamp: string;
    level: string;
    message: string;
  }>;
  artifacts: Array<{
    artifact_name: string;
    artifact_path: string;
  }>;
  // Endpoints from jobs table (jsonb column)
  endpoints?: Array<{
    method?: string;
    path?: string;
    summary?: string;
    operation_id?: string;
  }>;
  // Job configuration from jobs table and job_requests table
  source_type?: string;
  base_url?: string;
  spec_data?: string; // Base64 encoded spec content
  request_payload?: {
    target_intents?: string[];
    llm_config?: {
      payload_enhancement?: {
        provider: string;
        model?: string;
      };
      test_enhancement?: {
        provider: string;
        model?: string;
      };
    };
  };
  error_message?: string;
}

export interface IntentResponse {
  intents: string[];
  message: string;
}

/**
 * Create a new test generation job
 */
export async function createJob(request: JobRequest): Promise<JobResponse> {
  return retryWithBackoff(async () => {
    // Base64 encode the spec_data
    const encodedRequest = {
      ...request,
      spec_data: stringToBase64(request.spec_data),
    };

    const response = await fetch(`${API_BASE_URL}/api/v1/jobs`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(encodedRequest),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      const err: any = new Error(error.detail || "Failed to create job");
      err.status = response.status;
      throw err;
    }

    return response.json();
  });
}



/**
 * Extract intents from spec content
 */
export async function extractIntents(
  specData: string,
  sourceType: "openapi" | "python" | "typescript"
): Promise<IntentResponse> {
  return retryWithBackoff(async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/intents/extract`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        spec_data: specData,
        source_type: sourceType,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      const err: any = new Error(error.detail || "Failed to extract intents");
      err.status = response.status;
      throw err;
    }

    return response.json();
  });
}

/**
 * Get job status from API
 */
export async function getJobStatus(jobId: string): Promise<JobStatus> {
  return retryWithBackoff(async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      const err: any = new Error(error.detail || "Failed to get job status");
      err.status = response.status;
      throw err;
    }

    return response.json();
  });
}

/**
 * Get comprehensive job data with all related information (joins query)
 */
export async function getJobDetailedData(jobId: string): Promise<JobStatus> {
  return retryWithBackoff(async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}/details`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Fallback to regular getJobStatus if detailed endpoint doesn't exist
      console.warn("Detailed data endpoint not available, falling back to standard job status");
      return getJobStatus(jobId);
    }

    return response.json();
  });
}

/**
 * Get comprehensive job data directly from Supabase (with all related tables)
 */
export async function getJobDataFromSupabase(jobId: string): Promise<{
  job: any;
  request: any;
  artifacts: any[];
  logs: any[];
  endpoints: any[];
}> {
  if (!supabase) {
    throw new Error("Supabase not initialized");
  }

  try {
    // Fetch job details
    const { data: jobData, error: jobError } = await supabase
      .from("jobs")
      .select("*")
      .eq("id", jobId)
      .single();

    if (jobError) {
      throw new Error(`Failed to fetch job: ${jobError.message}`);
    }

    // Fetch job request (spec_data and request_payload)
    const { data: requestData, error: requestError } = await supabase
      .from("job_requests")
      .select("*")
      .eq("job_id", jobId)
      .single();

    if (requestError) {
      console.warn("Failed to fetch job request:", requestError);
    }

    // Fetch artifacts
    const { data: artifactsData, error: artifactsError } = await supabase
      .from("job_artifacts")
      .select("*")
      .eq("job_id", jobId);

    if (artifactsError) {
      console.warn("Failed to fetch artifacts:", artifactsError);
    }

    // Fetch logs
    const { data: logsData, error: logsError } = await supabase
      .from("job_logs")
      .select("*")
      .eq("job_id", jobId)
      .order("created_at", { ascending: true });

    if (logsError) {
      console.warn("Failed to fetch logs:", logsError);
    }

    // Endpoints are now stored in the jobs table as a JSONB column
    const endpoints = jobData?.endpoints || [];

    return {
      job: jobData,
      request: requestData,
      artifacts: artifactsData || [],
      logs: logsData || [],
      endpoints: endpoints,
    };
  } catch (err: any) {
    console.error("Error fetching job data from Supabase:", err);
    throw err;
  }
}

/**
 * Download all artifacts for a job as ZIP from the server
 */
export async function downloadJobZip(jobId: string): Promise<Blob> {
  const resp = await fetch(`${API_BASE_URL}/jobs/${jobId}/download`);
  if (!resp.ok) {
    throw new Error("Failed to download job ZIP");
  }
  return resp.blob();
}

/**
 * Fetch job logs from Supabase
 */
export async function fetchJobLogs(jobId: string): Promise<LogEntry[]> {
  if (!supabase) {
    console.error("Supabase not initialized");
    return [];
  }

  try {
    const { data, error } = await supabase
      .from("job_logs")
      .select("message, log_type, created_at")
      .eq("job_id", jobId)
      .order("created_at", { ascending: true });

    if (error) {
      console.warn("Failed to fetch logs:", error);
      return [];
    }

    return (data || []).map((log: any) => ({
      message: log.message,
      log_type: log.log_type || "info",
      created_at: log.created_at,
    }));
  } catch (err) {
    console.error("Error fetching job logs:", err);
    return [];
  }
}

/**
 * Subscribe to real-time job status updates via Supabase Realtime
 * Also fetches the complete initial job data including job_requests
 */
export function subscribeToJobStatus(
  jobId: string,
  onUpdate: (status: JobStatus) => void,
  onError: (error: Error) => void
): () => void {
  if (!supabase) {
    console.error("Supabase not initialized");
    onError(new Error("Supabase not initialized"));
    return () => {};
  }

  console.log(`Subscribing to real-time updates for job ${jobId}`);

  // Immediately fetch the complete initial job data
  const fetchInitialData = async () => {
    try {
      // Fetch job details
      const { data: jobData, error: jobError } = await supabase
        .from("jobs")
        .select("*")
        .eq("id", jobId)
        .single();

      if (jobError) {
        console.error("Failed to fetch job:", jobError);
        onError(new Error(`Failed to fetch job: ${jobError.message}`));
        return;
      }

      // Fetch job request (spec_data and request_payload)
      const { data: requestData, error: requestError } = await supabase
        .from("job_requests")
        .select("*")
        .eq("job_id", jobId)
        .single();

      if (requestError) {
        console.warn("Failed to fetch job request:", requestError);
      }

      // Fetch artifacts
      const { data: artifactsData, error: artifactsError } = await supabase
        .from("job_artifacts")
        .select("*")
        .eq("job_id", jobId);

      if (artifactsError) {
        console.warn("Failed to fetch artifacts:", artifactsError);
      }

      // Build the complete JobStatus with all data
      const status: JobStatus = {
        job_id: jobData.id,
        status: jobData.status,
        progress: jobData.progress || 0,
        created_at: jobData.created_at,
        updated_at: jobData.updated_at,
        logs: [],
        artifacts: (artifactsData || []).map((a: any) => ({
          artifact_name: a.artifact_path?.split("/").pop() || "",
          artifact_path: a.artifact_path,
        })),
        endpoints: jobData.endpoints || [],
        source_type: jobData.source_type,
        base_url: jobData.base_url,
        spec_data: requestData?.spec_data,
        request_payload: requestData?.request_payload,
        error_message: jobData.error_message,
      };

      console.log("Initial job data loaded:", status);
      onUpdate(status);
    } catch (err: any) {
      console.error("Error fetching initial job data:", err);
      onError(err);
    }
  };

  // Fetch initial data immediately
  fetchInitialData();

  // Subscribe to postgres changes on the jobs table
  const channel = supabase
    .channel(`job:${jobId}`)
    .on(
      "postgres_changes",
      {
        event: "UPDATE",
        schema: "public",
        table: "jobs",
        filter: `id=eq.${jobId}`,
      },
      (payload: any) => {
        console.log("Real-time job update received:", payload);

        const jobData = payload.new;
        if (jobData) {
          // For real-time updates, we only get jobs table data
          // The spec_data and request_payload won't change, so we only update status-related fields
          onUpdate({
            job_id: jobData.id,
            status: jobData.status,
            progress: jobData.progress || 0,
            created_at: jobData.created_at,
            updated_at: jobData.updated_at,
            logs: [],
            artifacts: [],
            endpoints: jobData.endpoints || [],
            source_type: jobData.source_type,
            base_url: jobData.base_url,
            error_message: jobData.error_message,
          });
        }
      }
    )
    .subscribe((status) => {
      if (status === "SUBSCRIBED") {
        console.log(`Successfully subscribed to real-time updates for job ${jobId}`);
      } else if (status === "TIMED_OUT") {
        console.warn(`Realtime timed out for job ${jobId}; will attempt automatic reconnect`);
      } else if (status === "CHANNEL_ERROR") {
        console.warn(`Channel subscription error for job ${jobId} - check Supabase credentials and RLS policies`);
        onError(new Error("Realtime channel error"));
      } else if (status === "CLOSED") {
        console.warn(`Realtime channel closed for job ${jobId}`);
      }
    });

  // Return cleanup function
  return () => {
    console.log(`Unsubscribing from job ${jobId}`);
    supabase?.removeChannel(channel);
  };
}

/**
 * Delete a job from Supabase
 */
/**
 * Delete a job from Supabase (DB + Storage)
 */
export async function deleteJob(jobId: string): Promise<void> {
  if (supabase) {
    try {
      console.log(`Deleting job ${jobId} from Supabase...`);

      // 1. Delete Artifacts from Storage
      // We need to handle this manually as there is no recursive delete
      const pathsToDelete: string[] = [];

      // List root properties
      const { data: rootFiles } = await supabase.storage
        .from(SUPABASE_STORAGE_BUCKET)
        .list(jobId);

      if (rootFiles) {
        rootFiles.forEach((file) => {
          pathsToDelete.push(`${jobId}/${file.name}`);
        });
      }

      // List tests folder
      const { data: testFiles } = await supabase.storage
        .from(SUPABASE_STORAGE_BUCKET)
        .list(`${jobId}/tests`);

      if (testFiles) {
        testFiles.forEach((file) => {
          pathsToDelete.push(`${jobId}/tests/${file.name}`);
        });
      }

      if (pathsToDelete.length > 0) {
        const { error: storageError } = await supabase.storage
          .from(SUPABASE_STORAGE_BUCKET)
          .remove(pathsToDelete);
        
        if (storageError) {
          console.warn("Failed to delete artifacts from storage:", storageError);
        }
      }

      // 2. Delete from DB (jobs table)
      // This should cascade to job_logs, job_requests, job_artifacts
      const { error: dbError } = await supabase
        .from("jobs")
        .delete()
        .eq("id", jobId);

      if (dbError) {
        console.error("Failed to delete job from DB:", dbError);
        throw new Error(dbError.message);
      }
      
      console.log(`Successfully deleted job ${jobId}`);
      return;
    } catch (err) {
        console.error("Error during Supabase deletion, trying API fallback:", err);
        // Fallthrough to API call as backup
    }
  }

  // Fallback: Call API if Supabase client not present or failed
  return retryWithBackoff(async () => {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      const err: any = new Error(error.detail || "Failed to delete job");
      err.status = response.status;
      throw err;
    }
  });
}

/**
 * Log entry type
 */
export interface LogEntry {
  message: string;
  log_type: "info" | "debug" | "error";
  created_at: string;
}

/**
 * Subscribe to real-time log updates for a job
 */
export function subscribeToLogs(
  jobId: string,
  onLog: (log: LogEntry) => void
): () => void {
  if (!supabase) {
    console.error("Supabase not initialized for log subscription");
    return () => {};
  }

  console.log(`Subscribing to log updates for job ${jobId}`);

  const channel = supabase
    .channel(`job_logs:${jobId}`)
    .on(
      "postgres_changes",
      {
        event: "INSERT",
        schema: "public",
        table: "job_logs",
        filter: `job_id=eq.${jobId}`,
      },
      (payload: any) => {
        const logData = payload.new;
        if (logData) {
          onLog({
            message: logData.message,
            log_type: logData.log_type || "info",
            created_at: logData.created_at,
          });
        }
      }
    )
    .subscribe((status) => {
      if (status === "SUBSCRIBED") {
        console.log(`Subscribed to logs for job ${jobId}`);
      }
    });

  return () => {
    console.log(`Unsubscribing from logs for job ${jobId}`);
    supabase?.removeChannel(channel);
  };
}

/**
 * Fetch all sessions from Supabase directly
 */
export async function fetchSessionsFromSupabase(): Promise<Array<{
  jobId: string;
  timestamp: number;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
}>> {
  if (!supabase) {
    console.error("Supabase not initialized");
    return [];
  }

  try {
    const { data, error: dbError } = await supabase
      .from("jobs")
      .select("*")
      .order("created_at", { ascending: false });

    if (dbError) {
      console.error("Failed to fetch sessions from Supabase:", dbError);
      return [];
    }

    if (!data) {
      return [];
    }

    return data.map((job: any) => ({
      jobId: job.id,
      timestamp: new Date(job.created_at).getTime(),
      status: job.status as "pending" | "running" | "completed" | "failed",
      progress: job.progress || 0,
    }));
  } catch (err) {
    console.error("Error fetching sessions from Supabase:", err);
    return [];
  }
}



/**
 * Fetch artifact content from Supabase storage
 */
export async function fetchArtifactFromStorage(artifactPath: string): Promise<string | null> {
  if (!supabase) {
    console.error("Supabase not initialized");
    return null;
  }

  try {
    const { data, error } = await supabase.storage
      .from(SUPABASE_STORAGE_BUCKET)
      .download(artifactPath);

    if (error) {
      console.error(`Failed to download artifact ${artifactPath}:`, error);
      return null;
    }

    const text = await data.text();
    return text;
  } catch (err) {
    console.error(`Error fetching artifact ${artifactPath}:`, err);
    return null;
  }
}

/**
 * Fetch all artifacts for a job from Supabase storage
 */
export async function fetchJobArtifacts(jobId: string): Promise<{
  payloads: any[];
  enhancedPayloads: any[];
  testFiles: Record<string, string>;
  intents: any[];
  ir: any;
}> {
  if (!supabase) {
    console.error("Supabase not initialized");
    return { payloads: [], enhancedPayloads: [], testFiles: {}, intents: [], ir: {} };
  }

  try {
    // Fetch payloads
    const payloadsContent = await fetchArtifactFromStorage(`${jobId}/3_payloads_final.json`);
    const payloads = payloadsContent ? JSON.parse(payloadsContent) : [];

    // Fetch enhanced payloads
    const enhancedContent = await fetchArtifactFromStorage(`${jobId}/3_payloads_enhanced.json`);
    const enhancedPayloads = enhancedContent ? JSON.parse(enhancedContent) : [];

    // Fetch intents
    const intentsContent = await fetchArtifactFromStorage(`${jobId}/2_intents.json`);
    const intents = intentsContent ? JSON.parse(intentsContent) : [];

    // Fetch IR
    const irContent = await fetchArtifactFromStorage(`${jobId}/1_ir.json`);
    const ir = irContent ? JSON.parse(irContent) : {};

    // List test files from storage
    const { data: testFilesList, error: listError } = await supabase.storage
      .from(SUPABASE_STORAGE_BUCKET)
      .list(`${jobId}/tests`);

    console.log("Test files list response:", { testFilesList, listError });

    const testFiles: Record<string, string> = {};
    
    if (!listError && testFilesList) {
      for (const file of testFilesList) {
        // Skip folders (id is null for folders) and files without names
        if (file.name && file.id) {
          console.log("Fetching test file:", file.name);
          const content = await fetchArtifactFromStorage(`${jobId}/tests/${file.name}`);
          if (content) {
            testFiles[file.name] = content;
          }
        }
      }
    } else if (listError) {
      console.error("Failed to list test files:", listError);
    }

    console.log("Fetched test files:", Object.keys(testFiles));
    return { payloads, enhancedPayloads, testFiles, intents, ir };
  } catch (err) {
    console.error("Error fetching job artifacts:", err);
    return { payloads: [], enhancedPayloads: [], testFiles: {}, intents: [], ir: {} };
  }
}


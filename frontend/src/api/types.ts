export type TaskType = "summarize" | "translate" | "generate";

export interface AIRequest {
  task: TaskType;
  input_text: string;
  target_language?: string;
  options?: {
    temperature?: number;
    max_tokens?: number;
    genre?: string;
    [key: string]: unknown;
  };
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number;
}

export interface AIResponse {
  id: string;
  task: TaskType;
  model: string;
  input_text: string;
  output_text: string;
  usage: TokenUsage;
  created_at: string;
}

export interface UsageHistoryItem {
  id: string;
  task: TaskType;
  model: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  created_at: string;
}

export interface ErrorInfo {
  type: string;
  message: string;
  detail?: string;
  retryable?: boolean;
}

export interface ErrorResponse {
  error: ErrorInfo;
}

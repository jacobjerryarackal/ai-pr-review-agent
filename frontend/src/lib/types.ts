// frontend/src/lib/types.ts

export type ReviewStatus =
  | "queued"
  | "in_progress"
  | "agents_running"
  | "aggregating"
  | "posting"
  | "completed"
  | "escalated"
  | "failed";

export type Verdict = "approve" | "request_changes" | "dismiss" | "comment";

export type DecisionAction = "approve" | "request_changes" | "dismiss";

export interface Finding {
  id: string;
  review_id: string;
  agent_type: string;
  severity: string; // "critical" | "high" | "medium" | "low" | "info"
  category: string;
  summary: string;
  file_path?: string | null;
  line_start?: number | null;
  line_end?: number | null;
  suggestion?: string | null;
  confidence: number;
  created_at: string;
}

export interface ReviewSummary {
  id: string;
  repo_full_name: string;
  pr_number: number;
  pr_title: string;
  head_commit_sha: string;
  verdict?: Verdict | string | null;
  status: ReviewStatus | string;
  overall_confidence?: number | null;
  needs_human_review: boolean;
  finding_count: number;
  created_at: string;
  updated_at: string;
}

export interface ReviewDetail {
  id: string;
  repo_full_name: string;
  pr_number: number;
  pr_title: string;
  head_commit_sha: string;
  verdict?: Verdict | string | null;
  status: ReviewStatus | string;
  overall_confidence?: number | null;
  needs_human_review: boolean;
  human_review_reason?: string | null;
  github_review_id?: number | null;
  findings: Finding[];
  created_at: string;
  updated_at: string;
}

export interface QueueItem {
  id: string;
  repo_full_name: string;
  pr_number: number;
  pr_title: string;
  status: ReviewStatus | string;
  needs_human_review: boolean;
  human_review_reason?: string | null;
  overall_confidence?: number | null;
  created_at: string;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface EconomicsSummary {
  today_usd: number;
  last_7d_usd: number;
  last_30d_usd: number;
  by_model_30d: Record<string, number>;
  by_agent_30d: Record<string, number>;
  call_count_30d: number;
  total_input_tokens_30d: number;
  total_output_tokens_30d: number;
}

export interface BudgetStatus {
  daily_cap_usd: number;
  daily_spent_usd: number;
  daily_headroom_usd: number;
  daily_utilization: number;
  per_review_cap_usd: number;
  exceeded: boolean;
}

export interface DailyPoint {
  date: string;
  cost_usd: number;
  call_count: number;
}

export interface HITLItem {
  id: string;
  review_id: string;
  repo_full_name: string;
  pr_number: number;
  agent_verdict: string;
  human_verdict: string | null;
  status: string;
  escalation_reason: string;
  overall_confidence: number;
  posted_to_github: boolean;
  created_at: string;
  resolved_at: string | null;
}

export interface HITLDetail extends HITLItem {
  findings: Finding[];
  human_reason?: string | null;
  reviewer_id?: string | null;
}

export interface HITLDecisionResponse {
  hitl_review_id: string;
  previous_status: string;
  new_status: string;
  human_verdict: string;
  posted_to_github: boolean;
  feedback_id: string;
}


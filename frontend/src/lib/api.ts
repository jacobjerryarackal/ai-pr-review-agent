// frontend/src/lib/api.ts

import type { ReviewDetail, DecisionAction, HITLDecisionResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }
  return headers;
}

export const api = {
  async getReview(id: string): Promise<ReviewDetail> {
    // If the ID contains slashes, we pass it exactly as part of the path.
    // e.g. "owner/repo:pr:sha" -> "/api/v1/reviews/owner/repo:pr:sha"
    // NextJS page routes can sometimes struggle with unescaped slashes, but the backend
    // router uses /{review_id:path} which handles it when passed directly.
    const url = `${API_BASE_URL}/api/v1/reviews/${id}`;
    const response = await fetch(url, {
      headers: getHeaders(),
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch review detail: ${response.statusText}`);
    }
    return response.json();
  },

  async hitlDecide(
    hitlId: string,
    payload: {
      human_verdict: DecisionAction;
      reason: string;
      reviewer_id: string;
    }
  ): Promise<HITLDecisionResponse> {
    const url = `${API_BASE_URL}/api/v1/hitl/${hitlId}/decision`;
    const response = await fetch(url, {
      method: "POST",
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Failed to submit HITL decision: ${response.statusText}`);
    }
    return response.json();
  },
};

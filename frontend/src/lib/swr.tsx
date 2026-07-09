// frontend/src/lib/swr.tsx

"use client";

import React from "react";
import { SWRConfig } from "swr";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface SWRError extends Error {
  status?: number;
  info?: unknown;
}

const defaultFetcher = async (url: string) => {
  const headers: Record<string, string> = {};
  const apiKey = process.env.NEXT_PUBLIC_API_KEY;
  if (apiKey) {
    headers["X-API-Key"] = apiKey;
  }

  // Prepend base URL if the input is a relative path
  const fullUrl = url.startsWith("http://") || url.startsWith("https://")
    ? url
    : `${API_BASE_URL}${url}`;

  const res = await fetch(fullUrl, { headers });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    const error = new Error(errorData.detail || "An error occurred while fetching the data.") as SWRError;
    // Attach extra info to the error object.
    error.status = res.status;
    error.info = errorData;
    throw error;
  }
  return res.json();
};

export function SWRProvider({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        fetcher: defaultFetcher,
        refreshInterval: 5000, // refresh data every 5 seconds by default
      }}
    >
      {children}
    </SWRConfig>
  );
}

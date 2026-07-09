// frontend/src/app/hitl/page.tsx

"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { Empty } from "@/components/Empty";
import { HITLDecisionForm } from "@/components/HITLDecisionForm";
import { FindingsByAgent } from "@/components/AgentFindingCard";
import { VerdictChip } from "@/components/VerdictChip";
import type { HITLItem, HITLDetail, Paginated } from "@/lib/types";

export default function HITLQueuePage() {
  const { data, error, isLoading } = useSWR<Paginated<HITLItem>>("/api/v1/hitl/queue?limit=100");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [rebuilding, setRebuilding] = useState(false);
  const [rebuildMsg, setRebuildMsg] = useState<string | null>(null);

  // Fetch detail for selected item
  const { data: detailData, error: detailError, isLoading: detailLoading } = useSWR<HITLDetail>(
    selectedId ? `/api/v1/hitl/${selectedId}` : null
  );

  const items = data?.items ?? [];

  async function handleRebuildQueue() {
    setRebuilding(true);
    setRebuildMsg(null);
    try {
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
      const headers: Record<string, string> = { "Content-Type": "application/json" };
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      if (apiKey) {
        headers["X-API-Key"] = apiKey;
      }
      
      const res = await fetch(`${API_BASE_URL}/api/v1/hitl/queue/rebuild`, {
        method: "POST",
        headers,
      });
      const data = await res.json();
      setRebuildMsg(data.message || "Queue rebuilt successfully.");
      mutate("/api/v1/hitl/queue?limit=100");
    } catch (err) {
      setRebuildMsg(err instanceof Error ? err.message : "Failed to rebuild queue");
    } finally {
      setRebuilding(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">HITL Decision Queue</h1>
          <p className="text-muted text-sm mt-1">
            Review reviews that require human approval before being posted back to GitHub.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {rebuildMsg && (
            <span className="text-xs font-mono text-accent bg-accent/10 border border-accent/20 px-2 py-1 rounded">
              {rebuildMsg}
            </span>
          )}
          <button
            onClick={handleRebuildQueue}
            disabled={rebuilding}
            className="px-3 py-1.5 rounded bg-panel border border-border hover:bg-bg text-sm text-white transition disabled:opacity-50"
          >
            {rebuilding ? "Rebuilding…" : "Rebuild Queue"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left/Middle column: Queue list */}
        <div className="lg:col-span-2 space-y-4">
          {error ? (
            <Empty>Failed to load queue: {error.message}</Empty>
          ) : isLoading ? (
            <Empty>Loading queue…</Empty>
          ) : items.length === 0 ? (
            <Empty>No items in the HITL queue.</Empty>
          ) : (
            <div className="border border-border rounded-lg bg-panel overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-bg text-muted text-xs uppercase tracking-wide">
                  <tr>
                    <th className="text-left px-4 py-2">PR / Repo</th>
                    <th className="text-left px-4 py-2">Agent Verdict</th>
                    <th className="text-left px-4 py-2">Status</th>
                    <th className="text-left px-4 py-2">Confidence</th>
                    <th className="text-left px-4 py-2">Escalated</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {items.map((item) => {
                    const isSelected = selectedId === item.id;
                    return (
                      <tr
                        key={item.id}
                        onClick={() => setSelectedId(item.id)}
                        className={`cursor-pointer transition ${
                          isSelected ? "bg-accent/10 border-l-2 border-accent" : "hover:bg-bg/40"
                        }`}
                      >
                        <td className="px-4 py-3 font-mono">
                          <span className="text-accent font-semibold">
                            {item.repo_full_name} #{item.pr_number}
                          </span>
                          <div className="text-[11px] text-muted truncate max-w-xs mt-0.5">
                            {item.id.split(":").pop()?.slice(0, 8)}…
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <VerdictChip verdict={item.agent_verdict} />
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex px-2 py-0.5 rounded text-xs font-mono font-medium ${
                            item.status === "pending"
                              ? "bg-warn/25 text-warn"
                              : "bg-ok/25 text-ok"
                          }`}>
                            {item.status}
                          </span>
                        </td>
                        <td className="px-4 py-3 font-mono">
                          {(item.overall_confidence * 100).toFixed(0)}%
                        </td>
                        <td className="px-4 py-3 text-xs text-muted">
                          {new Date(item.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right column: Details and Decision form */}
        <div className="lg:col-span-1">
          {!selectedId ? (
            <div className="border border-dashed border-border rounded-lg p-8 text-center text-muted text-sm bg-panel/30 h-full flex flex-col justify-center items-center">
              <span>Select an item from the queue to view details and submit a decision.</span>
            </div>
          ) : detailLoading ? (
            <div className="border border-border rounded-lg bg-panel p-6 text-center text-muted text-sm animate-pulse">
              Loading details…
            </div>
          ) : detailError || !detailData ? (
            <div className="border border-border rounded-lg bg-panel p-6 text-center text-err text-sm">
              Error loading details: {detailError?.message || "Data not found"}
            </div>
          ) : (
            <div className="space-y-6">
              {/* Item Info Card */}
              <div className="border border-border rounded-lg bg-panel p-4 space-y-3">
                <div>
                  <div className="text-[10px] text-muted font-mono">{detailData.id}</div>
                  <h3 className="font-semibold text-lg text-white mt-1">
                    {detailData.repo_full_name} #{detailData.pr_number}
                  </h3>
                  <a
                    href={`https://github.com/${detailData.repo_full_name}/pull/${detailData.pr_number}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-xs text-accent underline inline-block mt-1"
                  >
                    Open on GitHub →
                  </a>
                </div>

                <div className="border-t border-border pt-3 space-y-2">
                  <div className="text-xs">
                    <span className="text-muted uppercase tracking-wider block font-mono text-[10px]">Escalation Reason</span>
                    <span className="text-white font-medium block mt-0.5">{detailData.escalation_reason}</span>
                  </div>
                  <div className="text-xs">
                    <span className="text-muted uppercase tracking-wider block font-mono text-[10px]">Agent Verdict</span>
                    <VerdictChip verdict={detailData.agent_verdict} className="mt-1" />
                  </div>
                  <div className="text-xs">
                    <span className="text-muted uppercase tracking-wider block font-mono text-[10px]">Status</span>
                    <span className="text-white block mt-1 font-mono uppercase text-xs">{detailData.status}</span>
                  </div>
                </div>
              </div>

              {/* Decision form if pending */}
              {detailData.status === "pending" ? (
                <div className="space-y-2">
                  <h4 className="text-sm font-semibold text-white px-1">Take Action</h4>
                  <HITLDecisionForm hitlId={detailData.id} />
                </div>
              ) : (
                <div className="border border-border rounded-lg bg-panel/50 p-4 text-sm text-muted">
                  This item has already been resolved with human verdict:
                  <VerdictChip verdict={detailData.human_verdict} className="ml-2 inline-block align-middle" />
                  {detailData.human_reason && (
                    <div className="mt-2 text-xs border-l-2 border-border pl-2 italic">
                      &ldquo;{detailData.human_reason}&rdquo;
                    </div>
                  )}
                  {detailData.reviewer_id && (
                    <div className="mt-1 text-[10px] text-muted text-right font-mono">
                      Reviewed by {detailData.reviewer_id}
                    </div>
                  )}
                </div>
              )}

              {/* Findings Snapshot */}
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-white px-1">Findings Snapshot</h4>
                <div className="max-h-96 overflow-y-auto pr-1">
                  <FindingsByAgent findings={detailData.findings || []} />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

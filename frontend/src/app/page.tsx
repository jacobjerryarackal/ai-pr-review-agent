// frontend/src/app/page.tsx

"use client";

import useSWR from "swr";
import Link from "next/link";
import { ReviewStatusBadge } from "@/components/ReviewStatusBadge";
import { VerdictChip } from "@/components/VerdictChip";
import { Empty } from "@/components/Empty";
import type { Paginated, ReviewSummary, EconomicsSummary, BudgetStatus, HITLItem } from "@/lib/types";

export default function DashboardPage() {
  const { data: reviewsData, error: reviewsErr } = useSWR<Paginated<ReviewSummary>>("/api/v1/reviews?limit=5");
  const { data: ecoSummary, error: ecoErr } = useSWR<EconomicsSummary>("/api/v1/economics/summary");
  const { data: budget, error: budgetErr } = useSWR<BudgetStatus>("/api/v1/economics/budget");
  
  // Fetch pending hitl queue items
  // Note: the route in hitl_router is /api/v1/hitl/queue
  const { data: hitlData, error: hitlErr } = useSWR<{ items: HITLItem[]; total: number }>("/api/v1/hitl/queue?limit=5");

  const recentReviews = reviewsData?.items ?? [];
  const totalReviews = reviewsData?.total ?? 0;
  const pendingHitlCount = hitlData?.total ?? 0;
  const pendingHitlItems = hitlData?.items ?? [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-white">Dashboard</h1>
        <p className="text-muted text-sm mt-1">
          Overview of the AI Pull Request Review Agent status, spending, and pending human-in-the-loop decisions.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Total Reviews Card */}
        <div className="border border-border rounded-lg bg-panel p-6 shadow-sm">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted">Total Reviews</div>
          <div className="text-3xl font-mono font-bold mt-2 text-white">
            {reviewsErr ? "—" : reviewsData ? totalReviews : "…"}
          </div>
          <div className="text-xs text-muted mt-2">
            All reviews handled by the system
          </div>
        </div>

        {/* Pending HITL Card */}
        <Link href="/hitl" className="border border-border rounded-lg bg-panel p-6 shadow-sm hover:border-accent/40 transition block">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted">Pending HITL</div>
          <div className="text-3xl font-mono font-bold mt-2 text-white">
            {hitlErr ? "—" : hitlData ? pendingHitlCount : "…"}
          </div>
          <div className={`text-xs mt-2 ${pendingHitlCount > 0 ? "text-warn font-semibold" : "text-muted"}`}>
            {pendingHitlCount > 0 ? "Requires operator action" : "Queue is clear"}
          </div>
        </Link>

        {/* Today's Cost Card */}
        <Link href="/economics" className="border border-border rounded-lg bg-panel p-6 shadow-sm hover:border-accent/40 transition block">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted">Today&apos;s spend</div>
          <div className="text-3xl font-mono font-bold mt-2 text-white">
            {ecoErr ? "—" : ecoSummary ? usd(ecoSummary.today_usd) : "…"}
          </div>
          <div className="text-xs text-muted mt-2">
            LLM costs accrued today
          </div>
        </Link>

        {/* Budget Utilization Card */}
        <Link href="/economics" className="border border-border rounded-lg bg-panel p-6 shadow-sm hover:border-accent/40 transition block">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted">Daily Budget</div>
          <div className="text-3xl font-mono font-bold mt-2 text-white">
            {budgetErr ? "—" : budget ? pct(budget.daily_utilization) : "…"}
          </div>
          <div className={`text-xs mt-2 ${budget?.exceeded ? "text-err font-semibold" : "text-muted"}`}>
            {budget?.exceeded ? "Limit exceeded!" : `${usd(budget?.daily_spent_usd ?? 0)} of ${usd(budget?.daily_cap_usd ?? 0)}`}
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* HITL Queue Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-white">HITL Action Required</h2>
            <Link href="/hitl" className="text-xs text-accent hover:underline">
              View all queue →
            </Link>
          </div>
          
          {hitlErr ? (
            <Empty>Failed to load HITL queue: {hitlErr.message}</Empty>
          ) : !hitlData ? (
            <Empty>Loading HITL queue…</Empty>
          ) : pendingHitlItems.length === 0 ? (
            <div className="border border-dashed border-border rounded-lg p-6 text-center text-muted text-sm bg-panel/30">
              No pending reviews require human intervention.
            </div>
          ) : (
            <div className="border border-border rounded-lg bg-panel divide-y divide-border overflow-hidden">
              {pendingHitlItems.slice(0, 5).map((item) => (
                <div key={item.id} className="p-4 hover:bg-bg/40 transition flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <Link href={`/reviews/${encodeURIComponent(item.review_id)}`} className="text-sm font-medium text-accent hover:underline block truncate">
                      {item.repo_full_name} #{item.pr_number}
                    </Link>
                    <div className="text-xs text-muted truncate mt-1">
                      {item.escalation_reason}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="text-xs text-muted font-mono bg-bg px-2 py-0.5 rounded border border-border">
                      {item.status}
                    </span>
                    <Link href={`/hitl`} className="px-3 py-1 text-xs rounded bg-accent text-bg font-semibold hover:bg-accent/90 transition">
                      Decide
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Recent Activity Section */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-medium text-white">Recent Reviews</h2>
            <Link href="/reviews" className="text-xs text-accent hover:underline">
              View all history →
            </Link>
          </div>

          {reviewsErr ? (
            <Empty>Failed to load recent reviews: {reviewsErr.message}</Empty>
          ) : !reviewsData ? (
            <Empty>Loading recent reviews…</Empty>
          ) : recentReviews.length === 0 ? (
            <div className="border border-dashed border-border rounded-lg p-6 text-center text-muted text-sm bg-panel/30">
              No reviews recorded yet. Connect a repository or send a test webhook.
            </div>
          ) : (
            <div className="border border-border rounded-lg bg-panel divide-y divide-border overflow-hidden">
              {recentReviews.slice(0, 5).map((r) => (
                <div key={r.id} className="p-4 hover:bg-bg/40 transition flex items-center justify-between gap-4">
                  <div className="min-w-0">
                    <Link href={`/reviews/${encodeURIComponent(r.id)}`} className="text-sm font-medium text-accent hover:underline block truncate">
                      {r.repo_full_name} #{r.pr_number}
                    </Link>
                    <div className="text-xs text-muted truncate mt-1">
                      {r.pr_title}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <VerdictChip verdict={r.verdict} />
                    <ReviewStatusBadge status={r.status} />
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function usd(n: number): string {
  if (n === 0) return "$0.00";
  if (n < 0.01) return `$${n.toFixed(4)}`;
  if (n < 1) return `$${n.toFixed(3)}`;
  return `$${n.toFixed(2)}`;
}

function pct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}
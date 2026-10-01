"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  DollarSign,
  Users,
  ShoppingCart,
  AlertTriangle,
  TrendingUp,
  PieChart,
  Brain,
  ArrowRight,
  ShieldAlert,
} from "lucide-react";
import Link from "next/link";

interface OverviewData {
  total_revenue: number;
  customers: number;
  orders: number;
  churn_rate: number;
  average_order_value: number;
}

interface MonthlyRevenue {
  month: string;
  revenue: number;
}

interface RevenueData {
  total_revenue: number;
  average_order_value: number;
  monthly_revenue: MonthlyRevenue[];
}

interface SegmentItem {
  segment: string;
  customer_count: number;
  avg_recency_days?: number | null;
  avg_frequency?: number | null;
  avg_monetary?: number | null;
}

interface SegmentAnalytics {
  total_segments: number;
  segments: SegmentItem[];
}

interface ChurnAnalytics {
  total_eligible_customers: number;
  churned_customers: number;
  retained_customers: number;
  churn_rate: number;
  observation_date?: string | null;
}

const segmentBadgeColor: Record<string, string> = {
  Champions: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  "Loyal Customers": "bg-blue-500/10 text-blue-400 border-blue-500/30",
  "At Risk": "bg-amber-500/10 text-amber-400 border-amber-500/30",
  "Lost Customers": "bg-rose-500/10 text-rose-400 border-rose-500/30",
};

export default function DashboardPage() {
  const { data: overview, isLoading: overviewLoading } = useQuery<OverviewData>({
    queryKey: ["analytics-overview"],
    queryFn: () => api.get<OverviewData>("/analytics/overview"),
  });

  const { data: revenueData, isLoading: revLoading } = useQuery<RevenueData>({
    queryKey: ["analytics-revenue"],
    queryFn: () => api.get<RevenueData>("/analytics/revenue"),
  });

  const { data: segmentData, isLoading: segLoading } = useQuery<SegmentAnalytics>({
    queryKey: ["analytics-segments"],
    queryFn: () => api.get<SegmentAnalytics>("/analytics/segments"),
  });

  const { data: churnData, isLoading: churnLoading } = useQuery<ChurnAnalytics>({
    queryKey: ["analytics-churn"],
    queryFn: () => api.get<ChurnAnalytics>("/analytics/churn"),
  });

  const maxRevenue = Math.max(
    ...(revenueData?.monthly_revenue?.map((m) => m.revenue) || [1])
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-tight">RetainIQ Executive Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time business intelligence, revenue trends, customer segments & ML churn risk
          </p>
        </div>
        <Link
          href="/churn"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-indigo-600/20"
        >
          <Brain className="w-4 h-4" />
          Predict Churn
        </Link>
      </div>

      {/* Top Row: 4 Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Revenue */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Revenue</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-emerald-400">
            ${overviewLoading ? "..." : overview?.total_revenue?.toLocaleString()}
          </div>
          <p className="text-xs text-slate-400 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            AOV: ${overview?.average_order_value || 0}
          </p>
        </div>

        {/* Customers */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Customers</span>
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white">
            {overviewLoading ? "..." : overview?.customers}
          </div>
          <p className="text-xs text-slate-400 mt-2">Active database accounts</p>
        </div>

        {/* Orders */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Orders</span>
            <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
              <ShoppingCart className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-white">
            {overviewLoading ? "..." : overview?.orders}
          </div>
          <p className="text-xs text-slate-400 mt-2">Completed transactions</p>
        </div>

        {/* Churn Rate */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-bold uppercase tracking-wider">Churn Rate</span>
            <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-extrabold text-rose-400">
            {overviewLoading ? "..." : `${((overview?.churn_rate || 0) * 100).toFixed(1)}%`}
          </div>
          <p className="text-xs text-slate-400 mt-2">90-day inactivity model risk</p>
        </div>
      </div>

      {/* Middle Section: Revenue Trend */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Revenue Trend</h2>
            <p className="text-xs text-slate-400 mt-0.5">Monthly revenue distribution & performance</p>
          </div>
          <Link
            href="/analytics"
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
          >
            Full Analytics <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {revLoading ? (
          <div className="py-12 text-center text-slate-500">Loading revenue trend...</div>
        ) : (
          <div className="space-y-3">
            {revenueData?.monthly_revenue?.map((item) => {
              const percentage = Math.round((item.revenue / maxRevenue) * 100);
              return (
                <div key={item.month} className="space-y-1">
                  <div className="flex justify-between text-xs font-mono">
                    <span className="text-slate-400">{item.month}</span>
                    <span className="text-emerald-400 font-bold">
                      ${item.revenue.toLocaleString()}
                    </span>
                  </div>
                  <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800">
                    <div
                      className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Bottom Section: Customer Segments | Churn Risk */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column: Customer Segments */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-white">Customer Segments</h2>
                <p className="text-xs text-slate-400 mt-0.5">RFM & K-Means cluster distribution</p>
              </div>
              <PieChart className="w-5 h-5 text-indigo-400" />
            </div>

            {segLoading ? (
              <div className="py-8 text-center text-slate-500">Loading segments...</div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                {segmentData?.segments.map((seg, idx) => {
                  const badgeClass =
                    segmentBadgeColor[seg.segment] ||
                    "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
                  return (
                    <div
                      key={idx}
                      className="bg-slate-950 border border-slate-800 rounded-lg p-4 space-y-2"
                    >
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-bold border inline-block ${badgeClass}`}
                      >
                        {seg.segment}
                      </span>
                      <div className="text-xl font-extrabold text-white">
                        {seg.customer_count}{" "}
                        <span className="text-xs font-normal text-slate-400">customers</span>
                      </div>
                      <p className="text-xs text-slate-500">
                        Avg spend: ${seg.avg_monetary ?? "-"}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <Link
            href="/segments"
            className="mt-6 w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-medium text-xs rounded-lg text-center transition-colors block border border-slate-700"
          >
            Explore Customer Segments &rarr;
          </Link>
        </div>

        {/* Right Column: Churn Risk */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-bold text-white">Churn Risk</h2>
                <p className="text-xs text-slate-400 mt-0.5">ML 90-day churn prediction overview</p>
              </div>
              <ShieldAlert className="w-5 h-5 text-rose-400" />
            </div>

            {churnLoading ? (
              <div className="py-8 text-center text-slate-500">Loading churn risk...</div>
            ) : (
              <div className="space-y-4">
                <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <span className="text-xs text-slate-400 block">High Risk Customers</span>
                    <span className="text-2xl font-extrabold text-rose-400">
                      {churnData?.churned_customers}
                    </span>
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 block">Retained Customers</span>
                    <span className="text-2xl font-extrabold text-emerald-400">
                      {churnData?.retained_customers}
                    </span>
                  </div>
                </div>

                <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
                  <span className="text-xs text-slate-400 block mb-1">Model Observation Date</span>
                  <span className="text-sm font-mono text-indigo-400 font-bold">
                    {churnData?.observation_date || "2025-01-01"}
                  </span>
                  <p className="text-xs text-slate-500 mt-2 leading-relaxed">
                    Evaluates customer inactivity threshold over a 90-day forward-looking window.
                  </p>
                </div>
              </div>
            )}
          </div>

          <Link
            href="/churn"
            className="mt-6 w-full py-2.5 bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 font-medium text-xs rounded-lg text-center transition-colors block border border-rose-500/30"
          >
            Run Churn Risk Intelligence &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}

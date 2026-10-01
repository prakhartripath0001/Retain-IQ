"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import {
  DollarSign,
  Users,
  ShoppingCart,
  AlertTriangle,
  TrendingUp,
  ArrowRight,
  Brain,
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

interface Customer {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export default function DashboardPage() {
  const { data: overview, isLoading: overviewLoading } = useQuery<OverviewData>({
    queryKey: ["analytics-overview"],
    queryFn: () => api.get<OverviewData>("/analytics/overview"),
  });

  const { data: customers } = useQuery<Customer[]>({
    queryKey: ["recent-customers"],
    queryFn: () => api.get<Customer[]>("/customers?limit=5"),
  });

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Platform Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time overview of customer analytics & churn metrics
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

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Revenue</span>
            <div className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">
            ${overviewLoading ? "..." : overview?.total_revenue?.toLocaleString()}
          </div>
          <p className="text-xs text-slate-400 mt-2 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
            AOV: ${overview?.average_order_value || 0}
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Customers</span>
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">
            {overviewLoading ? "..." : overview?.customers}
          </div>
          <p className="text-xs text-slate-400 mt-2">Active database accounts</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Orders</span>
            <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
              <ShoppingCart className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white">
            {overviewLoading ? "..." : overview?.orders}
          </div>
          <p className="text-xs text-slate-400 mt-2">Processed transactions</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
          <div className="flex items-center justify-between text-slate-400 mb-3">
            <span className="text-xs font-semibold uppercase tracking-wider">Churn Rate</span>
            <div className="p-2 bg-rose-500/10 text-rose-400 rounded-lg">
              <AlertTriangle className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-bold text-rose-400">
            {overviewLoading ? "..." : `${((overview?.churn_rate || 0) * 100).toFixed(1)}%`}
          </div>
          <p className="text-xs text-slate-400 mt-2">90-day inactivity model risk</p>
        </div>
      </div>

      {/* Quick Access & Recent Data */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-white">Recent Customers</h2>
              <p className="text-xs text-slate-400 mt-0.5">Latest customer signups</p>
            </div>
            <Link
              href="/customers"
              className="text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center gap-1"
            >
              View all <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="divide-y divide-slate-800">
            {customers?.map((customer) => (
              <div key={customer.id} className="py-3 flex items-center justify-between">
                <div>
                  <Link
                    href={`/customers/${customer.id}`}
                    className="font-medium text-sm text-white hover:text-indigo-400 transition-colors"
                  >
                    {customer.name}
                  </Link>
                  <p className="text-xs text-slate-400">{customer.email}</p>
                </div>
                <span className="text-xs text-slate-500 font-mono">ID: #{customer.id}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between">
          <div>
            <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl w-fit text-rose-400 mb-4">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <h2 className="text-lg font-bold text-white mb-2">Churn Intelligence</h2>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              Run ML prediction algorithms to identify high-risk customers before they stop purchasing.
            </p>
          </div>

          <Link
            href="/churn"
            className="w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-white font-medium text-sm rounded-lg text-center transition-colors block border border-slate-700"
          >
            Explore Churn Risk &rarr;
          </Link>
        </div>
      </div>
    </div>
  );
}

"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { BarChart3, TrendingUp, DollarSign, Users, ShoppingCart, Calendar } from "lucide-react";

interface MonthlyRevenue {
  month: string;
  revenue: number;
}

interface RevenueData {
  total_revenue: number;
  average_order_value: number;
  monthly_revenue: MonthlyRevenue[];
}

interface CustomerData {
  total_customers: number;
  buying_customers: number;
  avg_orders_per_customer: number;
  avg_customer_spend: number;
}

export default function AnalyticsPage() {
  const { data: revenueData, isLoading: revLoading } = useQuery<RevenueData>({
    queryKey: ["analytics-revenue"],
    queryFn: () => api.get<RevenueData>("/analytics/revenue"),
  });

  const { data: customerData, isLoading: custLoading } = useQuery<CustomerData>({
    queryKey: ["analytics-customers"],
    queryFn: () => api.get<CustomerData>("/analytics/customers"),
  });

  const maxRevenue = Math.max(
    ...(revenueData?.monthly_revenue?.map((m) => m.revenue) || [1])
  );

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Business & Revenue Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">
          Deep-dive business intelligence, revenue breakdown, and growth metrics
        </p>
      </div>

      {/* Top Analytics KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Total Revenue
          </span>
          <div className="text-2xl font-bold text-emerald-400">
            ${revLoading ? "..." : revenueData?.total_revenue?.toLocaleString()}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Lifetime business gross</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Average Order Value
          </span>
          <div className="text-2xl font-bold text-white">
            ${revLoading ? "..." : revenueData?.average_order_value}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Per checkout transaction</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Avg Customer Spend
          </span>
          <div className="text-2xl font-bold text-blue-400">
            ${custLoading ? "..." : customerData?.avg_customer_spend}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Per purchasing customer</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Purchase Frequency
          </span>
          <div className="text-2xl font-bold text-purple-400">
            {custLoading ? "..." : `${customerData?.avg_orders_per_customer} orders`}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Avg orders per buying account</span>
        </div>
      </div>

      {/* Monthly Revenue Bar Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Monthly Revenue Trend</h2>
            <p className="text-xs text-slate-400">Monthly breakdown of gross revenue</p>
          </div>
          <TrendingUp className="w-5 h-5 text-emerald-400" />
        </div>

        {revLoading ? (
          <div className="py-12 text-center text-slate-500">Loading chart data...</div>
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
    </div>
  );
}

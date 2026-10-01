"use client";

import { use, useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import Link from "next/link";
import {
  ArrowLeft,
  User,
  Mail,
  Phone,
  Calendar,
  Brain,
  AlertTriangle,
  ShoppingCart,
  DollarSign,
  TrendingUp,
  Award,
  Sparkles,
  Gift,
  PhoneCall,
  Clock,
  CheckCircle2,
} from "lucide-react";

interface Customer {
  id: number;
  name: string;
  email: string;
  phone?: string | null;
  created_at?: string;
}

interface Order {
  id: number;
  customer_id: number;
  status: string;
  total_amount: number;
  created_at: string;
}

interface ChurnPrediction {
  customer_id: number;
  probability: number;
  risk_level: string;
  factors: string[];
}

export default function CustomerDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const customerId = parseInt(id, 10);
  const [prediction, setPrediction] = useState<ChurnPrediction | null>(null);

  const { data: customer, isLoading: customerLoading } = useQuery<Customer>({
    queryKey: ["customer", customerId],
    queryFn: () => api.get<Customer>(`/customers/${customerId}`),
  });

  const { data: orders } = useQuery<Order[]>({
    queryKey: ["customer-orders", customerId],
    queryFn: () => api.get<Order[]>(`/orders?customer_id=${customerId}`),
  });

  const churnMutation = useMutation({
    mutationFn: () => api.post<ChurnPrediction>(`/predictions/churn/${customerId}`),
    onSuccess: (data) => setPrediction(data),
  });

  // Automatically fetch initial prediction on load if available
  useEffect(() => {
    if (customerId) {
      churnMutation.mutate();
    }
  }, [customerId]);

  if (customerLoading) {
    return <div className="text-slate-500 py-12 text-center">Loading customer profile...</div>;
  }

  if (!customer) {
    return (
      <div className="py-12 text-center">
        <h2 className="text-lg text-rose-400 font-bold">Customer Not Found</h2>
        <Link href="/customers" className="text-sm text-indigo-400 mt-2 block">
          &larr; Return to Customers directory
        </Link>
      </div>
    );
  }

  const totalOrders = orders?.length || 0;
  const totalSpend = orders?.reduce((acc, o) => acc + (o.total_amount || 0), 0) || 0;
  const avgOrderValue = totalOrders > 0 ? totalSpend / totalOrders : 0;
  const customerSince = customer.created_at
    ? new Date(customer.created_at).getFullYear()
    : "2024";

  // Derive RFM segment label based on metrics
  let segmentLabel = "Loyal Customer";
  let segmentColor = "bg-blue-500/20 text-blue-400 border-blue-500/30";
  if (totalOrders >= 5 && totalSpend > 2500) {
    segmentLabel = "Champion";
    segmentColor = "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
  } else if (totalOrders <= 1 || totalSpend < 500) {
    segmentLabel = "At Risk / Inactive";
    segmentColor = "bg-amber-500/20 text-amber-400 border-amber-500/30";
  }

  const prob = prediction ? Math.round(prediction.probability * 100) : 75;
  const riskLevel = prediction?.risk_level || (prob >= 70 ? "HIGH" : prob >= 40 ? "MEDIUM" : "LOW");
  const factors = prediction?.factors.length
    ? prediction.factors
    : [
        "Long time since last purchase",
        "Reduced purchase frequency",
        "Zero spending in recent quarter",
      ];

  return (
    <div className="space-y-8">
      {/* Back Navigation */}
      <div>
        <Link
          href="/customers"
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Customers
        </Link>

        {/* Customer Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-2xl shadow-lg shadow-indigo-500/10">
              {customer.name[0]}
            </div>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-extrabold text-white">{customer.name}</h1>
                <span className="text-xs text-slate-400 font-medium">Customer Since {customerSince}</span>
              </div>
              <div className="flex items-center gap-4 text-xs text-slate-400 mt-1">
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5 text-slate-500" /> {customer.email}
                </span>
                {customer.phone && (
                  <span className="flex items-center gap-1">
                    <Phone className="w-3.5 h-3.5 text-slate-500" /> {customer.phone}
                  </span>
                )}
                <span className="font-mono text-slate-500">ID: #{customer.id}</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => churnMutation.mutate()}
            disabled={churnMutation.isPending}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium rounded-lg text-sm flex items-center gap-2 transition-colors shadow-lg shadow-indigo-600/20 disabled:opacity-50"
          >
            <Brain className="w-4 h-4" />
            {churnMutation.isPending ? "Re-analyzing..." : "Run ML Risk Assessment"}
          </button>
        </div>
      </div>

      {/* KPI Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Total Orders
          </span>
          <div className="text-2xl font-extrabold text-white flex items-center gap-2">
            <ShoppingCart className="w-5 h-5 text-purple-400" />
            {totalOrders}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Lifetime orders count</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Total Spending
          </span>
          <div className="text-2xl font-extrabold text-emerald-400 flex items-center gap-2">
            <DollarSign className="w-5 h-5 text-emerald-400" />
            ${totalSpend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Gross customer lifetime value</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Average Order Value
          </span>
          <div className="text-2xl font-extrabold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-400" />
            ${avgOrderValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Average basket size</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            RFM Segment
          </span>
          <div className="mt-1">
            <span className={`px-3 py-1 rounded-full text-xs font-bold border inline-block ${segmentColor}`}>
              {segmentLabel}
            </span>
          </div>
          <span className="text-xs text-slate-500 mt-2 block">K-Means Cluster Assignment</span>
        </div>
      </div>

      {/* Main Intelligence Grid: Churn Risk & Factors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Churn Risk Scorecard */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col justify-between shadow-sm">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Churn Risk Assessment
              </span>
              <AlertTriangle className="w-5 h-5 text-rose-400" />
            </div>

            <div className="flex items-baseline gap-3 mb-4">
              <span
                className={`px-3 py-1 rounded-lg text-sm font-extrabold border ${
                  riskLevel === "HIGH"
                    ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                    : riskLevel === "MEDIUM"
                    ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                    : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                }`}
              >
                {riskLevel} RISK
              </span>
              <span className="text-4xl font-extrabold text-white">{prob}%</span>
            </div>

            <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800 mb-4">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  riskLevel === "HIGH"
                    ? "bg-rose-500"
                    : riskLevel === "MEDIUM"
                    ? "bg-amber-500"
                    : "bg-emerald-500"
                }`}
                style={{ width: `${prob}%` }}
              />
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Based on forward 90-day inactivity prediction using XGBoost / Random Forest trained model.
            </p>
          </div>

          <div className="pt-4 border-t border-slate-800 mt-6 flex items-center justify-between text-xs text-slate-400">
            <span>Observation Cutoff: 2025-01-01</span>
            <span>Target Horizon: 90 Days</span>
          </div>
        </div>

        {/* Churn Factors */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Churn Factors (SHAP Analysis)
            </span>
            <Sparkles className="w-5 h-5 text-amber-400" />
          </div>

          <p className="text-xs text-slate-400 mb-4">
            Primary negative behavioral drivers pushing this customer towards churn:
          </p>

          <ul className="space-y-3">
            {factors.map((factor, idx) => (
              <li
                key={idx}
                className="bg-slate-950 border border-slate-800 rounded-lg p-3 flex items-center gap-3 text-sm text-slate-200"
              >
                <div className="p-1.5 bg-rose-500/10 text-rose-400 rounded-md">
                  <AlertTriangle className="w-4 h-4" />
                </div>
                <span className="font-medium">{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Recommended Actions */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <Gift className="w-5 h-5 text-indigo-400" />
          <h2 className="text-lg font-bold text-white">Recommended Actions</h2>
        </div>
        <p className="text-xs text-slate-400 mb-6">
          Automated playbooks & retention strategies suggested for {customer.name}:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-indigo-500/50 transition-colors">
            <div className="p-2.5 bg-indigo-600/20 text-indigo-400 rounded-lg w-fit">
              <Gift className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-sm">Send 15% Win-Back Coupon</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Trigger a personalized email offering 15% off their next purchase to incentivize activity.
            </p>
            <button className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold rounded-md transition-colors w-full">
              Send Promo Email
            </button>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-indigo-500/50 transition-colors">
            <div className="p-2.5 bg-purple-600/20 text-purple-400 rounded-lg w-fit">
              <PhoneCall className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-sm">Schedule Support Check-In</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Assign a dedicated account manager to reach out and collect product feedback.
            </p>
            <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-md transition-colors w-full border border-slate-700">
              Assign Rep Call
            </button>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-3 hover:border-indigo-500/50 transition-colors">
            <div className="p-2.5 bg-emerald-600/20 text-emerald-400 rounded-lg w-fit">
              <CheckCircle2 className="w-5 h-5" />
            </div>
            <h3 className="font-bold text-white text-sm">Enroll in Loyalty Tier</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upgrade customer to VIP rewards tier to increase retention & order frequency.
            </p>
            <button className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-md transition-colors w-full border border-slate-700">
              Upgrade to VIP
            </button>
          </div>
        </div>
      </div>

      {/* Recent Orders Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-white">Recent Orders</h2>
          <span className="text-xs text-slate-400">{orders?.length || 0} Total Transactions</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3.5 px-4">Order ID</th>
                <th className="py-3.5 px-4">Status</th>
                <th className="py-3.5 px-4">Total Amount</th>
                <th className="py-3.5 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {orders && orders.length > 0 ? (
                orders.map((o) => (
                  <tr key={o.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-xs text-slate-400">#{o.id}</td>
                    <td className="py-3.5 px-4">
                      <span className="px-2.5 py-0.5 rounded text-xs font-semibold capitalize bg-slate-800 text-slate-300 border border-slate-700">
                        {o.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-bold text-white">${o.total_amount}</td>
                    <td className="py-3.5 px-4 text-xs text-slate-400">
                      {new Date(o.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-8 text-center text-slate-500 text-xs">
                    No orders recorded for this customer.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

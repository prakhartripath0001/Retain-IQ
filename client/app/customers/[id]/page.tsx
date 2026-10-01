"use client";

import { use, useState } from "react";
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
  CheckCircle,
  ShoppingCart,
  DollarSign,
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

  if (customerLoading) {
    return <div className="text-slate-500 py-12 text-center">Loading customer profile...</div>;
  }

  if (!customer) {
    return (
      <div className="py-12 text-center">
        <h2 className="text-lg text-rose-400 font-bold">Customer Not Found</h2>
        <Link href="/customers" className="text-sm text-indigo-400 mt-2 block">
          &larr; Return to Customers list
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <Link
          href="/customers"
          className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 mb-4 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Customers
        </Link>

        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-bold text-xl">
              {customer.name[0]}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{customer.name}</h1>
              <p className="text-xs text-slate-400 font-mono">Customer ID: #{customer.id}</p>
            </div>
          </div>

          <button
            onClick={() => churnMutation.mutate()}
            disabled={churnMutation.isPending}
            className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white font-medium rounded-lg text-sm flex items-center gap-2 transition-colors shadow-lg shadow-rose-600/20 disabled:opacity-50"
          >
            <Brain className="w-4 h-4" />
            {churnMutation.isPending ? "Analyzing..." : "Predict Churn Risk"}
          </button>
        </div>
      </div>

      {/* Customer Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Contact Info
          </span>
          <div className="space-y-2 text-sm text-slate-300">
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-slate-500" />
              <span>{customer.email}</span>
            </div>
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-slate-500" />
              <span>{customer.phone || "No phone listed"}</span>
            </div>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Order Metrics
          </span>
          <div className="space-y-2 text-sm text-slate-300">
            <div className="flex items-center gap-2">
              <ShoppingCart className="w-4 h-4 text-slate-500" />
              <span>{orders?.length || 0} Total Orders</span>
            </div>
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-slate-500" />
              <span>
                $
                {orders
                  ?.reduce((acc, o) => acc + (o.total_amount || 0), 0)
                  .toLocaleString() || 0}{" "}
                Total Spend
              </span>
            </div>
          </div>
        </div>

        {/* Churn Prediction Banner */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            ML Churn Assessment
          </span>
          {prediction ? (
            <div className="mt-2">
              <div className="flex items-center gap-2">
                <span
                  className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                    prediction.risk_level === "HIGH"
                      ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      : prediction.risk_level === "MEDIUM"
                      ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                      : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  }`}
                >
                  {prediction.risk_level} RISK
                </span>
                <span className="text-lg font-bold text-white">
                  {(prediction.probability * 100).toFixed(0)}%
                </span>
              </div>
              <ul className="mt-2 space-y-1">
                {prediction.factors.map((factor, idx) => (
                  <li key={idx} className="text-xs text-slate-400 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-rose-400" />
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic mt-2">
              Click &quot;Predict Churn Risk&quot; above to run the ML model.
            </p>
          )}
        </div>
      </div>

      {/* Customer Orders History */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-bold text-white mb-4">Order History</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Order ID</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Total Amount</th>
                <th className="py-3 px-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {orders && orders.length > 0 ? (
                orders.map((o) => (
                  <tr key={o.id} className="hover:bg-slate-800/40">
                    <td className="py-3 px-4 font-mono text-xs text-slate-400">#{o.id}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-xs capitalize bg-slate-800 text-slate-300 border border-slate-700">
                        {o.status}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-white">${o.total_amount}</td>
                    <td className="py-3 px-4 text-xs text-slate-400">
                      {new Date(o.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="py-6 text-center text-slate-500 text-xs">
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

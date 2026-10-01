"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { AlertTriangle, Brain, Search, CheckCircle, ShieldAlert, Sparkles } from "lucide-react";
import Link from "next/link";

interface ChurnAnalytics {
  total_eligible_customers: number;
  churned_customers: number;
  retained_customers: number;
  churn_rate: number;
  observation_date?: string | null;
}

interface ChurnPrediction {
  customer_id: number;
  probability: number;
  risk_level: string;
  factors: string[];
}

export default function ChurnPage() {
  const [testCustomerId, setTestCustomerId] = useState("1");
  const [predictionResult, setPredictionResult] = useState<ChurnPrediction | null>(null);

  const { data: churnData, isLoading } = useQuery<ChurnAnalytics>({
    queryKey: ["analytics-churn"],
    queryFn: () => api.get<ChurnAnalytics>("/analytics/churn"),
  });

  const predictMutation = useMutation({
    mutationFn: (id: number) => api.post<ChurnPrediction>(`/predictions/churn/${id}`),
    onSuccess: (data) => setPredictionResult(data),
  });

  const handlePredict = (e: React.FormEvent) => {
    e.preventDefault();
    const idNum = parseInt(testCustomerId, 10);
    if (!isNaN(idNum)) {
      predictMutation.mutate(idNum);
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Churn Risk & Prediction</h1>
        <p className="text-sm text-slate-400 mt-1">
          Machine learning churn prediction pipeline & risk scoring
        </p>
      </div>

      {/* Churn Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Churn Rate
          </span>
          <div className="text-3xl font-extrabold text-rose-400">
            {isLoading ? "..." : `${((churnData?.churn_rate || 0) * 100).toFixed(1)}%`}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">90-day inactivity model</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Eligible Customers
          </span>
          <div className="text-3xl font-extrabold text-white">
            {isLoading ? "..." : churnData?.total_eligible_customers}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">With purchase history</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Churned (High Risk)
          </span>
          <div className="text-3xl font-extrabold text-amber-400">
            {isLoading ? "..." : churnData?.churned_customers}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Did not return in 90 days</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Retained
          </span>
          <div className="text-3xl font-extrabold text-emerald-400">
            {isLoading ? "..." : churnData?.retained_customers}
          </div>
          <span className="text-xs text-slate-500 mt-1 block">Active repeat purchasers</span>
        </div>
      </div>

      {/* Live Churn Prediction Form */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 bg-indigo-600/20 text-indigo-400 rounded-lg">
            <Brain className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white">Run Live ML Prediction</h2>
            <p className="text-xs text-slate-400">
              Predict churn probability & extract key risk factors for any customer ID
            </p>
          </div>
        </div>

        <form onSubmit={handlePredict} className="flex gap-3 max-w-md mb-6">
          <input
            type="number"
            required
            value={testCustomerId}
            onChange={(e) => setTestCustomerId(e.target.value)}
            placeholder="Enter Customer ID (e.g. 1)"
            className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
          />
          <button
            type="submit"
            disabled={predictMutation.isPending}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm rounded-lg transition-colors flex items-center gap-2"
          >
            {predictMutation.isPending ? "Predicting..." : "Predict"}
          </button>
        </form>

        {predictMutation.isError && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/20 rounded-lg text-rose-400 text-sm mb-4">
            {(predictMutation.error as Error).message}
          </div>
        )}

        {predictionResult && (
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-4 max-w-xl">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs text-slate-400">Customer #{predictionResult.customer_id}</span>
                <div className="flex items-center gap-3 mt-1">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-extrabold border ${
                      predictionResult.risk_level === "HIGH"
                        ? "bg-rose-500/20 text-rose-400 border-rose-500/30"
                        : predictionResult.risk_level === "MEDIUM"
                        ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
                        : "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
                    }`}
                  >
                    {predictionResult.risk_level} RISK
                  </span>
                  <span className="text-2xl font-bold text-white">
                    {(predictionResult.probability * 100).toFixed(0)}% Probability
                  </span>
                </div>
              </div>

              <Link
                href={`/customers/${predictionResult.customer_id}`}
                className="text-xs text-indigo-400 hover:underline"
              >
                View Full Profile &rarr;
              </Link>
            </div>

            <div className="pt-3 border-t border-slate-800">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
                Key Risk Factors
              </span>
              <ul className="space-y-1.5">
                {predictionResult.factors.map((factor, i) => (
                  <li key={i} className="text-sm text-slate-300 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
                    {factor}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

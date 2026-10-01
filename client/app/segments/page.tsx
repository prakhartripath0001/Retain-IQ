"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { PieChart, Users, Award, AlertTriangle, ShieldX, Sparkles } from "lucide-react";

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

const segmentBadgeColor: Record<string, string> = {
  Champions: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  "Loyal Customers": "bg-blue-500/10 text-blue-400 border-blue-500/30",
  "At Risk": "bg-amber-500/10 text-amber-400 border-amber-500/30",
  "Lost Customers": "bg-rose-500/10 text-rose-400 border-rose-500/30",
};

export default function SegmentsPage() {
  const { data: segmentData, isLoading } = useQuery<SegmentAnalytics>({
    queryKey: ["analytics-segments"],
    queryFn: () => api.get<SegmentAnalytics>("/analytics/segments"),
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Customer Segmentation</h1>
        <p className="text-sm text-slate-400 mt-1">
          K-Means clustering & RFM (Recency, Frequency, Monetary) breakdown
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {isLoading ? (
          <div className="col-span-full py-12 text-center text-slate-500">
            Loading segments...
          </div>
        ) : segmentData?.segments.length === 0 ? (
          <div className="col-span-full py-12 text-center text-slate-500">
            No segment data available yet.
          </div>
        ) : (
          segmentData?.segments.map((item, idx) => {
            const badgeClass =
              segmentBadgeColor[item.segment] ||
              "bg-indigo-500/10 text-indigo-400 border-indigo-500/30";
            return (
              <div
                key={idx}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-bold border ${badgeClass}`}
                    >
                      {item.segment}
                    </span>
                    <Users className="w-4 h-4 text-slate-500" />
                  </div>
                  <div className="text-3xl font-extrabold text-white mt-1">
                    {item.customer_count}
                  </div>
                  <span className="text-xs text-slate-400">Total Customers</span>
                </div>

                <div className="mt-6 pt-4 border-t border-slate-800 space-y-2 text-xs text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Avg Recency:</span>
                    <span className="font-semibold">{item.avg_recency_days ?? "-"} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Avg Frequency:</span>
                    <span className="font-semibold">{item.avg_frequency ?? "-"} orders</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Avg Monetary:</span>
                    <span className="font-semibold text-emerald-400">
                      ${item.avg_monetary ?? "-"}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <h2 className="text-lg font-bold text-white mb-4">RFM Cluster Profiles Table</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-950/60 text-xs uppercase text-slate-400 font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Segment</th>
                <th className="py-3 px-4">Customer Count</th>
                <th className="py-3 px-4">Avg Recency (Days)</th>
                <th className="py-3 px-4">Avg Frequency (Orders)</th>
                <th className="py-3 px-4">Avg Monetary ($)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {segmentData?.segments.map((seg, i) => (
                <tr key={i} className="hover:bg-slate-800/40">
                  <td className="py-3 px-4 font-semibold text-white">{seg.segment}</td>
                  <td className="py-3 px-4 text-slate-300">{seg.customer_count}</td>
                  <td className="py-3 px-4 text-slate-400">{seg.avg_recency_days ?? "-"}</td>
                  <td className="py-3 px-4 text-slate-400">{seg.avg_frequency ?? "-"}</td>
                  <td className="py-3 px-4 font-semibold text-emerald-400">
                    ${seg.avg_monetary ?? "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

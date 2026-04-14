"use client";

import { useEffect, useState } from "react";
import { fetchProjectStats, type ProjectStats } from "@/lib/api";

function formatCost(cost: number): string {
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

const toolColors: Record<string, string> = {
  claude: "bg-orange-100 text-orange-700",
  gemini: "bg-blue-100 text-blue-700",
  gpt: "bg-green-100 text-green-700",
};

export default function ProjectsPage() {
  const [data, setData] = useState<ProjectStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const result = await fetchProjectStats();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) {
    return <div className="text-gray-400 text-sm py-8 text-center">Loading...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">Projects</h2>

      {data.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400 text-sm">
          No project data available
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Project</th>
                <th className="text-left px-4 py-3 font-medium text-gray-500">Tool</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Requests</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Tokens</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Cost</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Avg Latency</th>
                <th className="text-right px-4 py-3 font-medium text-gray-500">Last Used</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {data.map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium text-gray-800">
                    {item.project_id || "(no project)"}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                        toolColors[item.tool_name] || "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {item.tool_name}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {item.request_count.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {item.total_tokens.toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-right tabular-nums">
                    {formatCost(item.total_cost)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-500 tabular-nums">
                    {item.avg_latency_ms ? `${Math.round(item.avg_latency_ms)}ms` : "-"}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-400 whitespace-nowrap">
                    {item.last_used_at
                      ? new Date(item.last_used_at).toLocaleDateString("ko-KR")
                      : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

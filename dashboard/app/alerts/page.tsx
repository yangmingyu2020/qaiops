"use client";

import { useEffect, useState } from "react";
import { fetchAlerts, type AlertItem } from "@/lib/api";

const toolColors: Record<string, string> = {
  claude: "bg-orange-100 text-orange-700",
  gemini: "bg-blue-100 text-blue-700",
  gpt: "bg-green-100 text-green-700",
};

function formatCost(cost: number): string {
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [threshold, setThreshold] = useState(10000);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      try {
        const data = await fetchAlerts(threshold);
        setAlerts(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load alerts");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [threshold]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">고비용 알림</h2>
        <div className="flex items-center gap-2 text-sm">
          <label className="text-gray-500">기준값:</label>
          <select
            value={threshold}
            onChange={(e) => setThreshold(Number(e.target.value))}
            className="border border-gray-300 rounded px-2 py-1 text-sm bg-white"
          >
            <option value={1000}>1,000+ 토큰</option>
            <option value={5000}>5,000+ 토큰</option>
            <option value={10000}>10,000+ 토큰</option>
            <option value={50000}>50,000+ 토큰</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-gray-400 text-sm py-8 text-center">로딩 중...</div>
      ) : alerts.length === 0 ? (
        <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400 text-sm">
          {threshold.toLocaleString()} 토큰 기준을 초과하는 요청이 없습니다
        </div>
      ) : (
        <div className="space-y-3">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className="bg-white rounded-lg border border-gray-200 p-4 flex items-start gap-4"
            >
              <div className="flex-shrink-0 mt-0.5">
                <span className="inline-block w-2 h-2 rounded-full bg-red-500" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${
                      toolColors[alert.tool_name] || "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {alert.tool_name}
                  </span>
                  {alert.model_name && (
                    <span className="text-xs text-gray-400">{alert.model_name}</span>
                  )}
                  {alert.project_id && (
                    <span className="text-xs text-gray-400">/ {alert.project_id}</span>
                  )}
                  <span className="text-xs text-gray-400 ml-auto">
                    {new Date(alert.created_at).toLocaleString("ko-KR")}
                  </span>
                </div>
                <p className="text-sm text-gray-700 truncate">{alert.prompt_text}</p>
              </div>
              <div className="text-right flex-shrink-0">
                <p className="text-sm font-semibold text-red-600">
                  {alert.total_tokens.toLocaleString()} 토큰
                </p>
                <p className="text-xs text-gray-500">{formatCost(alert.total_cost)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

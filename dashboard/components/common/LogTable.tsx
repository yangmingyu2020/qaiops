"use client";

import type { LogItem } from "@/lib/api";

interface LogTableProps {
  logs: LogItem[];
  onRowClick?: (log: LogItem) => void;
}

function formatDate(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatCost(cost: number): string {
  if (cost < 0.001) return `$${cost.toFixed(6)}`;
  return `$${cost.toFixed(4)}`;
}

const toolColors: Record<string, string> = {
  claude: "bg-orange-100 text-orange-700",
  gemini: "bg-blue-100 text-blue-700",
  gpt: "bg-green-100 text-green-700",
  codex: "bg-green-100 text-green-700",
};

export default function LogTable({ logs, onRowClick }: LogTableProps) {
  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-8 text-center text-gray-400 text-sm">
        No logs found
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 border-b border-gray-200">
          <tr>
            <th className="text-left px-4 py-3 font-medium text-gray-500">Tool</th>
            <th className="text-left px-4 py-3 font-medium text-gray-500">Prompt</th>
            <th className="text-left px-4 py-3 font-medium text-gray-500">Project</th>
            <th className="text-right px-4 py-3 font-medium text-gray-500">Tokens</th>
            <th className="text-right px-4 py-3 font-medium text-gray-500">Cost</th>
            <th className="text-right px-4 py-3 font-medium text-gray-500">Time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {logs.map((log) => (
            <tr
              key={log.id}
              className="hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => onRowClick?.(log)}
            >
              <td className="px-4 py-3">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    toolColors[log.tool_name] || "bg-gray-100 text-gray-700"
                  }`}
                >
                  {log.tool_name}
                </span>
              </td>
              <td className="px-4 py-3 text-gray-700 max-w-xs truncate">
                {log.prompt_text}
              </td>
              <td className="px-4 py-3 text-gray-500">
                {log.project_id || "-"}
              </td>
              <td className="px-4 py-3 text-right text-gray-600 tabular-nums">
                {(log.input_tokens + log.output_tokens).toLocaleString()}
              </td>
              <td className="px-4 py-3 text-right text-gray-600 tabular-nums">
                {formatCost(log.total_cost)}
              </td>
              <td className="px-4 py-3 text-right text-gray-400 whitespace-nowrap">
                {formatDate(log.created_at)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

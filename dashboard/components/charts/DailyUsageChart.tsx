"use client";

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { DailyStats } from "@/lib/api";

interface DailyUsageChartProps {
  data: DailyStats[];
}

interface AggregatedDay {
  date: string;
  tokens: number;
  cost: number;
  requests: number;
}

export default function DailyUsageChart({ data }: DailyUsageChartProps) {
  // Aggregate by date (across tools)
  const byDate = new Map<string, AggregatedDay>();
  for (const item of data) {
    const existing = byDate.get(item.date);
    if (existing) {
      existing.tokens += item.total_tokens;
      existing.cost += item.total_cost;
      existing.requests += item.total_requests;
    } else {
      byDate.set(item.date, {
        date: item.date,
        tokens: item.total_tokens,
        cost: item.total_cost,
        requests: item.total_requests,
      });
    }
  }

  const chartData = Array.from(byDate.values()).sort((a, b) =>
    a.date.localeCompare(b.date)
  );

  if (chartData.length === 0) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-sm font-medium text-gray-700 mb-4">일일 사용량</h3>
        <div className="h-64 flex items-center justify-center text-gray-400 text-sm">
          데이터 없음
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-sm font-medium text-gray-700 mb-4">일일 토큰 사용량</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#9ca3af" }}
            tickFormatter={(v) => v.slice(5)}
          />
          <YAxis tick={{ fontSize: 11, fill: "#9ca3af" }} />
          <Tooltip
            contentStyle={{ fontSize: 12 }}
            formatter={(value: number) => [value.toLocaleString(), "토큰"]}
            labelFormatter={(label) => `날짜: ${label}`}
          />
          <Area
            type="monotone"
            dataKey="tokens"
            stroke="#3b82f6"
            fill="#dbeafe"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

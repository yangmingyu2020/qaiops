"use client";

import { useEffect, useState } from "react";
import StatsCard from "@/components/common/StatsCard";
import DailyUsageChart from "@/components/charts/DailyUsageChart";
import ToolDistribution from "@/components/charts/ToolDistribution";
import CostRanking from "@/components/charts/CostRanking";
import {
  fetchDailyStats,
  fetchTopCosts,
  type DailyStats,
  type TopCostItem,
} from "@/lib/api";

function formatCost(cost: number): string {
  if (cost < 0.01) return `$${cost.toFixed(4)}`;
  return `$${cost.toFixed(2)}`;
}

export default function DashboardPage() {
  const [dailyStats, setDailyStats] = useState<DailyStats[]>([]);
  const [topCosts, setTopCosts] = useState<TopCostItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [daily, costs] = await Promise.all([
          fetchDailyStats(30),
          fetchTopCosts(5),
        ]);
        setDailyStats(daily);
        setTopCosts(costs);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load data");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalRequests = dailyStats.reduce((sum, d) => sum + d.total_requests, 0);
  const totalTokens = dailyStats.reduce((sum, d) => sum + d.total_tokens, 0);
  const totalCost = dailyStats.reduce((sum, d) => sum + d.total_cost, 0);
  const toolCount = new Set(dailyStats.map((d) => d.tool_name)).size;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400 text-sm">
        Loading dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
        {error}
        <p className="mt-1 text-red-500">
          Make sure the FastAPI server is running on port 8765.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Total Requests"
          value={totalRequests.toLocaleString()}
          subtitle="Last 30 days"
        />
        <StatsCard
          title="Total Tokens"
          value={totalTokens.toLocaleString()}
          subtitle="Last 30 days"
        />
        <StatsCard
          title="Total Cost"
          value={formatCost(totalCost)}
          subtitle="Last 30 days"
        />
        <StatsCard
          title="Active Tools"
          value={String(toolCount)}
          subtitle="Distinct tools used"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <DailyUsageChart data={dailyStats} />
        </div>
        <ToolDistribution data={dailyStats} />
      </div>

      <CostRanking data={topCosts} />
    </div>
  );
}

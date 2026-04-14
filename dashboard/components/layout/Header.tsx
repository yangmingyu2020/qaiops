"use client";

import { useEffect, useState } from "react";
import { fetchHealth } from "@/lib/api";

export default function Header() {
  const [serverStatus, setServerStatus] = useState<"connected" | "disconnected" | "checking">("checking");

  useEffect(() => {
    async function checkServer() {
      try {
        await fetchHealth();
        setServerStatus("connected");
      } catch {
        setServerStatus("disconnected");
      }
    }
    checkServer();
    const interval = setInterval(checkServer, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
      <h2 className="text-sm font-medium text-gray-700">Monitoring Dashboard</h2>
      <div className="flex items-center gap-2 text-xs">
        <span
          className={`w-2 h-2 rounded-full ${
            serverStatus === "connected"
              ? "bg-green-500"
              : serverStatus === "disconnected"
              ? "bg-red-500"
              : "bg-yellow-500"
          }`}
        />
        <span className="text-gray-500">
          {serverStatus === "connected"
            ? "Server Connected"
            : serverStatus === "disconnected"
            ? "Server Disconnected"
            : "Checking..."}
        </span>
      </div>
    </header>
  );
}

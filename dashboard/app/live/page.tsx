"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import type { LogItem } from "@/lib/api";

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8765/ws/live";

type ConnectionStatus = "connected" | "disconnected" | "connecting";

const toolColors: Record<string, string> = {
  claude: "bg-orange-100 text-orange-700",
  gemini: "bg-blue-100 text-blue-700",
  gpt: "bg-green-100 text-green-700",
};

function formatTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("ko-KR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function LivePage() {
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [status, setStatus] = useState<ConnectionStatus>("disconnected");
  const [paused, setPaused] = useState(false);
  const feedRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pausedRef = useRef(false);

  pausedRef.current = paused;

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    setStatus("connecting");
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => setStatus("connected");
    ws.onclose = () => {
      setStatus("disconnected");
      setTimeout(connect, 3000);
    };
    ws.onerror = () => ws.close();
    ws.onmessage = (event) => {
      try {
        const log = JSON.parse(event.data) as LogItem;
        setLogs((prev) => [log, ...prev].slice(0, 200));
        if (!pausedRef.current && feedRef.current) {
          feedRef.current.scrollTop = 0;
        }
      } catch {
        // ignore malformed messages
      }
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const statusColor =
    status === "connected"
      ? "bg-green-500"
      : status === "connecting"
      ? "bg-yellow-500"
      : "bg-red-500";

  return (
    <div className="space-y-4 h-full flex flex-col">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-800">실시간 피드</h2>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setPaused((p) => !p)}
            className={`px-3 py-1 rounded text-sm border transition-colors ${
              paused
                ? "bg-blue-50 border-blue-300 text-blue-700"
                : "border-gray-300 text-gray-600 hover:bg-gray-50"
            }`}
          >
            {paused ? "재개" : "일시정지"}
          </button>
          <button
            onClick={() => setLogs([])}
            className="px-3 py-1 rounded text-sm border border-gray-300 text-gray-600 hover:bg-gray-50"
          >
            초기화
          </button>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span className={`w-2 h-2 rounded-full ${statusColor}`} />
            {status === "connected"
              ? "연결됨"
              : status === "connecting"
              ? "연결 중..."
              : "연결 끊김"}
          </div>
        </div>
      </div>

      <div
        ref={feedRef}
        className="flex-1 bg-white rounded-lg border border-gray-200 overflow-auto min-h-[400px]"
      >
        {logs.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-400 text-sm">
            새 로그를 기다리는 중...
            <br />
            CLI 래퍼를 사용하여 로그를 생성하세요.
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {logs.map((log, idx) => (
              <div key={`${log.id}-${idx}`} className="px-4 py-3 hover:bg-gray-50">
                <div className="flex items-center gap-3 text-sm">
                  <span className="text-xs text-gray-400 font-mono w-16">
                    {formatTime(log.created_at)}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-medium ${
                      toolColors[log.tool_name] || "bg-gray-100 text-gray-700"
                    }`}
                  >
                    {log.tool_name}
                  </span>
                  <span className="text-gray-700 flex-1 truncate">{log.prompt_text}</span>
                  <span className="text-xs text-gray-500 tabular-nums">
                    {(log.input_tokens + log.output_tokens).toLocaleString()} tok
                  </span>
                  <span className="text-xs text-gray-500 tabular-nums w-16 text-right">
                    ${log.total_cost.toFixed(4)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="text-xs text-gray-400">
        버퍼에 {logs.length}개 로그 (최대 200개)
      </div>
    </div>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import LogTable from "@/components/common/LogTable";
import { fetchLogs, type LogItem, type LogListResponse } from "@/lib/api";

export default function HistoryPage() {
  const [data, setData] = useState<LogListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [toolFilter, setToolFilter] = useState("");
  const [projectFilter, setProjectFilter] = useState("");
  const [search, setSearch] = useState("");
  const [selectedLog, setSelectedLog] = useState<LogItem | null>(null);

  const loadLogs = useCallback(async () => {
    setLoading(true);
    try {
      const result = await fetchLogs({
        page,
        size: 20,
        tool_name: toolFilter || undefined,
        project_id: projectFilter || undefined,
        search: search || undefined,
      });
      setData(result);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load logs");
    } finally {
      setLoading(false);
    }
  }, [page, toolFilter, projectFilter, search]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setPage(1);
    loadLogs();
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-800">히스토리</h2>

      {/* Filters */}
      <form onSubmit={handleSearch} className="flex gap-3 flex-wrap">
        <select
          value={toolFilter}
          onChange={(e) => { setToolFilter(e.target.value); setPage(1); }}
          className="border border-gray-300 rounded px-3 py-1.5 text-sm bg-white"
        >
          <option value="">전체 도구</option>
          <option value="claude">Claude</option>
          <option value="gemini">Gemini</option>
          <option value="gpt">GPT</option>
        </select>
        <input
          type="text"
          placeholder="프로젝트 ID"
          value={projectFilter}
          onChange={(e) => { setProjectFilter(e.target.value); setPage(1); }}
          className="border border-gray-300 rounded px-3 py-1.5 text-sm w-40"
        />
        <input
          type="text"
          placeholder="프롬프트 검색..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded px-3 py-1.5 text-sm flex-1 min-w-48"
        />
        <button
          type="submit"
          className="bg-gray-900 text-white px-4 py-1.5 rounded text-sm hover:bg-gray-800 transition-colors"
        >
          검색
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-gray-400 text-sm py-8 text-center">로딩 중...</div>
      ) : data ? (
        <>
          <LogTable logs={data.items} onRowClick={setSelectedLog} />

          {/* Pagination */}
          {data.pages > 1 && (
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">
                {data.page} / {data.pages} 페이지 (총 {data.total}건)
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-40"
                >
                  이전
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                  disabled={page >= data.pages}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-40"
                >
                  다음
                </button>
              </div>
            </div>
          )}
        </>
      ) : null}

      {/* Log Detail Modal */}
      {selectedLog && (
        <div
          className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedLog(null)}
        >
          <div
            className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-auto p-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-800">로그 상세</h3>
              <button
                onClick={() => setSelectedLog(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                닫기
              </button>
            </div>
            <div className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-gray-500">도구</label>
                  <p className="font-medium">{selectedLog.tool_name}</p>
                </div>
                <div>
                  <label className="text-gray-500">모델</label>
                  <p className="font-medium">{selectedLog.model_name || "-"}</p>
                </div>
                <div>
                  <label className="text-gray-500">프로젝트</label>
                  <p className="font-medium">{selectedLog.project_id || "-"}</p>
                </div>
                <div>
                  <label className="text-gray-500">비용</label>
                  <p className="font-medium">${selectedLog.total_cost.toFixed(6)}</p>
                </div>
                <div>
                  <label className="text-gray-500">입력 토큰</label>
                  <p className="font-medium">{selectedLog.input_tokens.toLocaleString()}</p>
                </div>
                <div>
                  <label className="text-gray-500">출력 토큰</label>
                  <p className="font-medium">{selectedLog.output_tokens.toLocaleString()}</p>
                </div>
              </div>
              <div>
                <label className="text-gray-500">프롬프트</label>
                <pre className="mt-1 bg-gray-50 p-3 rounded text-xs whitespace-pre-wrap break-words">
                  {selectedLog.prompt_text}
                </pre>
              </div>
              {selectedLog.response_text && (
                <div>
                  <label className="text-gray-500">응답</label>
                  <pre className="mt-1 bg-gray-50 p-3 rounded text-xs whitespace-pre-wrap break-words max-h-60 overflow-auto">
                    {selectedLog.response_text}
                  </pre>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

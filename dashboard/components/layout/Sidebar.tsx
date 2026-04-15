"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "대시보드" },
  { href: "/live", label: "실시간 피드" },
  { href: "/history", label: "히스토리" },
  { href: "/projects", label: "프로젝트" },
  { href: "/alerts", label: "알림" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 min-h-screen bg-gray-900 text-gray-300 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-bold text-white tracking-wide">QaiOps</h1>
        <p className="text-xs text-gray-500 mt-1">AI CLI 관제 시스템</p>
      </div>
      <nav className="flex-1 py-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-4 py-2.5 text-sm transition-colors ${
                isActive
                  ? "bg-gray-800 text-white border-l-2 border-blue-500"
                  : "hover:bg-gray-800 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-700 text-xs text-gray-500">
        v0.1.0
      </div>
    </aside>
  );
}

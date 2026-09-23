"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, BookOpen, Users, MessageSquare } from "lucide-react";

const links = [
  { href: "/", label: "Resumen", icon: LayoutDashboard },
  { href: "/gaps", label: "Brechas", icon: BookOpen },
  { href: "/students", label: "Estudiantes", icon: Users },
  { href: "/ai", label: "Consulta IA", icon: MessageSquare },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-lg font-bold text-indigo-700">TUNI Supervisor</h1>
        <p className="text-xs text-gray-500">Panel de monitoreo</p>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors ${
                active
                  ? "bg-indigo-50 text-indigo-700 font-medium"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-200 text-xs text-gray-400">
        Universidad Metropolitana
      </div>
    </aside>
  );
}

import type { ReactNode } from "react";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
}

export function StatsCard({ title, value, subtitle, icon }: StatsCardProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">{title}</p>
        {icon && <span className="text-gray-400">{icon}</span>}
      </div>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      {subtitle && <p className="mt-1 text-xs text-gray-400">{subtitle}</p>}
    </div>
  );
}

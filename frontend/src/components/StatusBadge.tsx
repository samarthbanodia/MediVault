import { Badge } from "./ui/badge";

interface StatusBadgeProps {
  status: "normal" | "moderate" | "high" | "critical";
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const statusConfig = {
    normal: {
      label: "Normal",
      className: "bg-[#10b981] hover:bg-[#10b981]/80 text-white",
    },
    moderate: {
      label: "Moderate",
      className: "bg-[#f59e0b] hover:bg-[#f59e0b]/80 text-white",
    },
    high: {
      label: "High",
      className: "bg-[#dc2626] hover:bg-[#dc2626]/80 text-white",
    },
    critical: {
      label: "Critical",
      className: "bg-[#7f1d1d] hover:bg-[#7f1d1d]/80 text-white",
    },
  };

  const config = statusConfig[status];

  return <Badge className={config.className}>{config.label}</Badge>;
}

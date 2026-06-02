import React from "react";

const DOMAIN_COLORS = {
  "Jewellery Retail": "#7c3aed",
  "General Retail": "#3b82f6",
  "Hospitality": "#14b8a6",
  "Healthcare": "#ef4444",
  "Education": "#06b6d4",
  "IT Services": "#8b5cf6",
  "Financial Services": "#f59e0b",
  "Manufacturing": "#6366f1",
  "Construction": "#f97316",
  "Other / Mixed": "#6b7280",
};

export default function DomainBadge({ domain, subDomain, confidence, size = "medium" }) {
  if (!domain) return null;

  const domainColor = DOMAIN_COLORS[domain] || DOMAIN_COLORS["Unknown / Mixed"];
  
  const sizeStyles = {
    small: { padding: "4px 8px", fontSize: 12 },
    medium: { padding: "8px 16px", fontSize: 14 },
    large: { padding: "12px 24px", fontSize: 16 },
  };

  const style = sizeStyles[size] || sizeStyles.medium;

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
      <div
        style={{
          ...style,
          borderRadius: 8,
          backgroundColor: domainColor,
          color: "white",
          fontWeight: 600,
        }}
      >
        {domain}
      </div>
      {subDomain && (
        <div
          style={{
            padding: "6px 12px",
            borderRadius: 6,
            backgroundColor: "#f3f4f6",
            color: "#374151",
            fontWeight: 500,
            fontSize: size === "small" ? 11 : size === "large" ? 14 : 13,
          }}
        >
          {subDomain}
        </div>
      )}
      {confidence !== null && confidence !== undefined && (
        <div
          style={{
            padding: "6px 12px",
            borderRadius: 6,
            backgroundColor: "#e0e7ff",
            color: "#4338ca",
            fontWeight: 500,
            fontSize: size === "small" ? 10 : size === "large" ? 13 : 12,
          }}
        >
          {Math.round(confidence * 100)}% confidence
        </div>
      )}
    </div>
  );
}


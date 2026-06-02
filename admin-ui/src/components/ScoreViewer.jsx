import React from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import GenericScreeningViewer from "./GenericScreeningViewer.jsx";

const COLORS = {
  age_preference: "#8884d8",
  education: "#82ca9d",
  languages: "#ffc658",
  skills: "#ff7300",
  certifications: "#ff6b9d",
  jewellery_experience: "#00C49F",
};

const CATEGORY_COLORS = {
  "Prospective Candidate": "#10b981", // green
  "Good Candidate": "#3b82f6", // blue
  "Eligible Candidate": "#f59e0b", // amber
  // "Not Eligible" removed - don't show this category
};

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

// Purple brand theme
const PURPLE_THEME = {
  primary: "#7c3aed",
  primaryLight: "#a78bfa",
  primaryDark: "#6d28d9",
};

export default function ScoreViewer({ report, profile }) {
  if (!report) return null;

  // Route to appropriate viewer based on report status
  if (report.status === "screened") {
    return <GenericScreeningViewer report={report} profile={profile} />;
  }

  // Jewellery scoring report (status === "scored")

  const {
    first_name,
    total_score,
    candidate_category,
    breakdown,
    segment_details,
    strengths,
    visa_info,
    primary_domain,
    sub_domain,
  } = report;

  // Extract additional info from profile
  const nationality = profile?.nationality || "Not specified";
  const phone = profile?.phone || "Not specified";
  const sex = profile?.sex || profile?.gender || "Not specified";

  // Prepare data for pie chart
  const pieData = Object.entries(breakdown || {})
    .filter(([_, value]) => value > 0)
    .map(([key, value]) => ({
      name: key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
      value: value,
      color: COLORS[key] || "#8884d8",
    }));

  const categoryColor = CATEGORY_COLORS[candidate_category] || "#6b7280";

  return (
    <div style={{ marginTop: 20, border: `2px solid ${PURPLE_THEME.primaryLight}`, padding: 24, borderRadius: 12, background: "#fff", boxShadow: "0 4px 6px rgba(124, 58, 237, 0.1)" }}>
      {/* Header Section */}
      <div style={{ marginBottom: 24, borderBottom: `2px solid ${PURPLE_THEME.primaryLight}`, paddingBottom: 16 }}>
        <div style={{ marginBottom: 8 }}>
          <span style={{ fontSize: 14, fontWeight: 600, color: PURPLE_THEME.primary, textTransform: "uppercase", letterSpacing: "0.5px" }}>
            Name
          </span>
        </div>
        <h2 style={{ margin: 0, fontSize: 32, fontWeight: 700, color: PURPLE_THEME.primary }}>
          {first_name || "Candidate"}
        </h2>

        {/* Domain & Sub-Domain Badge */}
        {(primary_domain || sub_domain) && (
          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", marginBottom: 8, textTransform: "uppercase" }}>
              Sector & Role
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
              {primary_domain && (
                <div
                  style={{
                    padding: "8px 16px",
                    borderRadius: 8,
                    backgroundColor: DOMAIN_COLORS[primary_domain] || DOMAIN_COLORS["Jewellery Retail"],
                    color: "white",
                    fontWeight: 600,
                    fontSize: 14,
                  }}
                >
                  {primary_domain}
                </div>
              )}
              {sub_domain && (
                <div
                  style={{
                    padding: "6px 12px",
                    borderRadius: 6,
                    backgroundColor: "#f3f4f6",
                    color: "#374151",
                    fontWeight: 500,
                    fontSize: 13,
                    border: "1px solid #e5e7eb",
                  }}
                >
                  {sub_domain}
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Additional Info */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginTop: 16 }}>
          <div>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", textTransform: "uppercase" }}>Nationality</span>
            <div style={{ fontSize: 16, fontWeight: 500, color: "#111827", marginTop: 4 }}>{nationality}</div>
          </div>
          <div>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", textTransform: "uppercase" }}>Sex</span>
            <div style={{ fontSize: 16, fontWeight: 500, color: "#111827", marginTop: 4 }}>{sex}</div>
          </div>
          <div>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", textTransform: "uppercase" }}>Mobile Number</span>
            <div style={{ fontSize: 16, fontWeight: 500, color: "#111827", marginTop: 4 }}>{phone}</div>
          </div>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 16 }}>
          <div style={{ fontSize: 40, fontWeight: 700, color: PURPLE_THEME.primary }}>
            Total Score: {total_score}
          </div>
          {candidate_category && candidate_category !== "Not Eligible" && (
            <div
              style={{
                padding: "10px 20px",
                borderRadius: 8,
                backgroundColor: categoryColor,
                color: "white",
                fontWeight: 600,
                fontSize: 16,
              }}
            >
              {candidate_category}
            </div>
          )}
        </div>
      </div>

      {/* Detailed Segments Section */}
      {segment_details && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 16, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
            Detailed Segments
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
            {Object.entries(segment_details).map(([key, segment]) => (
              <div
                key={key}
                style={{
                  border: "1px solid #e5e7eb",
                  borderRadius: 8,
                  padding: 16,
                  background: "#f9fafb",
                }}
              >
                <div style={{ fontSize: 14, fontWeight: 600, color: "#6b7280", marginBottom: 8 }}>
                  {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </div>
                <div style={{ fontSize: 24, fontWeight: 700, color: "#111827", marginBottom: 4 }}>
                  {segment.score} pts
                </div>
                <div style={{ fontSize: 14, color: "#4b5563", marginTop: 8 }}>
                  {segment.details}
                </div>
                {segment.flags && segment.flags.length > 0 && (
                  <div style={{ marginTop: 8 }}>
                    {segment.flags.map((flag, idx) => (
                      <span
                        key={idx}
                        style={{
                          display: "inline-block",
                          padding: "2px 8px",
                          marginRight: 4,
                          marginTop: 4,
                          borderRadius: 4,
                          backgroundColor: "#fee2e2",
                          color: "#991b1b",
                          fontSize: 12,
                        }}
                      >
                        {flag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score Breakdown with Pie Chart */}
      <div style={{ marginBottom: 24 }}>
        <h3 style={{ marginBottom: 16, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
          Score Breakdown
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, alignItems: "center" }}>
          {/* Pie Chart */}
          <div style={{ minHeight: 300 }}>
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ textAlign: "center", color: "#6b7280", padding: 40 }}>
                No score breakdown available
              </div>
            )}
          </div>

          {/* Breakdown List */}
          <div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {Object.entries(breakdown || {}).map(([key, value]) => (
                <div
                  key={key}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    padding: 12,
                    borderRadius: 8,
                    background: value > 0 ? "#f3f4f6" : "#fef2f2",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div
                      style={{
                        width: 16,
                        height: 16,
                        borderRadius: 4,
                        backgroundColor: COLORS[key] || "#8884d8",
                      }}
                    />
                    <span style={{ fontWeight: 500, color: "#374151" }}>
                      {key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                    </span>
                  </div>
                  <span style={{ fontWeight: 700, fontSize: 18, color: "#111827" }}>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Strengths Section */}
      {strengths && strengths.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
            Strengths
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {strengths.map((strength, idx) => (
              <span
                key={idx}
                style={{
                  padding: "8px 16px",
                  borderRadius: 8,
                  backgroundColor: PURPLE_THEME.primaryLight,
                  color: "white",
                  fontWeight: 500,
                  fontSize: 14,
                }}
              >
                {strength}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Visa Info Section */}
      {visa_info && (
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
            Visa Information (Not Scored)
          </h3>
          <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
            <div>
              <span style={{ fontWeight: 500, color: "#6b7280" }}>Type: </span>
              <span style={{ color: "#111827" }}>{visa_info.visa_type || "Unknown"}</span>
            </div>
            {visa_info.visa_expiry_date && (
              <div>
                <span style={{ fontWeight: 500, color: "#6b7280" }}>Expiry: </span>
                <span style={{ color: "#111827" }}>{visa_info.visa_expiry_date}</span>
              </div>
            )}
            {typeof visa_info.days_remaining === "number" && (
              <div>
                <span style={{ fontWeight: 500, color: "#6b7280" }}>Days Remaining: </span>
                <span style={{ color: "#111827" }}>{visa_info.days_remaining}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

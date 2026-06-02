import React from "react";

// Purple brand theme
const PURPLE_THEME = {
  primary: "#7c3aed",
  primaryLight: "#a78bfa",
  primaryDark: "#6d28d9",
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

export default function GenericScreeningViewer({ report, profile }) {
  if (!report) return null;

  const {
    first_name,
    primary_domain,
    sub_domain,
    domain_confidence,
    eligibility_flags,
    recommendation,
    age,
    languages_count,
    has_degree,
    segment_details,
    visa_info,
  } = report;

  // Extract additional info from profile
  const nationality = profile?.nationality || "Not specified";
  const phone = profile?.phone || "Not specified";
  const sex = profile?.sex || profile?.gender || "Not specified";
  const email = profile?.email || "Not specified";

  const domainColor = DOMAIN_COLORS[primary_domain] || DOMAIN_COLORS["Unknown / Mixed"];

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
        <div style={{ marginTop: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", marginBottom: 8, textTransform: "uppercase" }}>
            Sector & Role
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
            <div
              style={{
                padding: "8px 16px",
                borderRadius: 8,
                backgroundColor: domainColor,
                color: "white",
                fontWeight: 600,
                fontSize: 14,
              }}
            >
              {primary_domain}
            </div>
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
            {domain_confidence !== null && domain_confidence !== undefined && (
              <div
                style={{
                  padding: "6px 12px",
                  borderRadius: 6,
                  backgroundColor: "#e0e7ff",
                  color: "#4338ca",
                  fontWeight: 500,
                  fontSize: 12,
                }}
              >
                {Math.round(domain_confidence * 100)}% confidence
              </div>
            )}
          </div>
        </div>

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
          <div>
            <span style={{ fontSize: 12, fontWeight: 600, color: "#6b7280", textTransform: "uppercase" }}>Email</span>
            <div style={{ fontSize: 16, fontWeight: 500, color: "#111827", marginTop: 4 }}>{email}</div>
          </div>
        </div>
      </div>

      {/* Status Banner */}
      <div
        style={{
          marginBottom: 24,
          padding: 16,
          borderRadius: 8,
          backgroundColor: "#fef3c7",
          border: "1px solid #fbbf24",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ fontSize: 24 }}>ℹ️</div>
          <div>
            <div style={{ fontWeight: 600, color: "#92400e", marginBottom: 4 }}>
              Not a Jewellery Retail Profile
            </div>
            <div style={{ fontSize: 14, color: "#78350f" }}>
              This candidate has been classified as <strong>{primary_domain}</strong> and has been routed for generic screening.
            </div>
          </div>
        </div>
      </div>

      {/* Recommendation Section */}
      {recommendation && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
            Recommendation
          </h3>
          <div
            style={{
              padding: 16,
              borderRadius: 8,
              backgroundColor: "#dbeafe",
              border: `2px solid ${domainColor}`,
            }}
          >
            <div style={{ fontSize: 18, fontWeight: 600, color: "#1e40af", marginBottom: 4 }}>
              {recommendation}
            </div>
            <div style={{ fontSize: 14, color: "#1e3a8a", marginTop: 8 }}>
              This candidate should be reviewed by the {primary_domain} hiring team for appropriate role matching.
            </div>
          </div>
        </div>
      )}

      {/* Detailed Segments Section (Similar to ScoreViewer but without scores) */}
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
                          backgroundColor: flag.includes("acceptable") ? "#d1fae5" : "#fee2e2",
                          color: flag.includes("acceptable") ? "#065f46" : "#991b1b",
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

      {/* Eligibility Flags */}
      {eligibility_flags && eligibility_flags.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
            Eligibility Indicators
          </h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {eligibility_flags.map((flag, idx) => (
              <div
                key={idx}
                style={{
                  padding: "8px 16px",
                  borderRadius: 8,
                  backgroundColor: "#d1fae5",
                  color: "#065f46",
                  fontWeight: 500,
                  fontSize: 14,
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                }}
              >
                <span>✓</span>
                <span>{flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Visa Info Section */}
      {visa_info && (
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ marginBottom: 12, fontSize: 20, fontWeight: 600, color: PURPLE_THEME.primary }}>
            Visa Information
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
                <span style={{ color: visa_info.days_remaining < 30 ? "#ef4444" : "#111827" }}>
                  {visa_info.days_remaining}
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Note */}
      <div
        style={{
          marginTop: 24,
          padding: 12,
          borderRadius: 6,
          backgroundColor: "#f3f4f6",
          fontSize: 13,
          color: "#6b7280",
          fontStyle: "italic",
        }}
      >
        {report.note || "Generic screening completed. Jewellery-specific scoring not applicable."}
      </div>
    </div>
  );
}


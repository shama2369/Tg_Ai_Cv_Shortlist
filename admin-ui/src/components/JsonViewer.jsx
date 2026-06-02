import React from "react";
import DomainBadge from "./DomainBadge.jsx";

export default function JsonViewer({ title, data, showDomainBadge = false }) {
  if (!data) return null;

  // Extract domain info if available
  const domainInfo = data?.profile?.primary_domain || data?.primary_domain 
    ? {
        domain: data?.profile?.primary_domain || data?.primary_domain,
        subDomain: data?.profile?.sub_domain || data?.sub_domain,
        confidence: data?.profile?.domain_confidence || data?.domain_confidence,
      }
    : null;

  return (
    <div style={{ marginTop: title ? 12 : 0, border: "1px solid #e5e7eb", padding: 16, borderRadius: 8, background: "#f9fafb" }}>
      {title && (
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <b style={{ color: "#374151", fontSize: 16 }}>{title}</b>
          {showDomainBadge && domainInfo && (
            <DomainBadge 
              domain={domainInfo.domain} 
              subDomain={domainInfo.subDomain}
              confidence={domainInfo.confidence}
              size="small"
            />
          )}
        </div>
      )}
      {showDomainBadge && domainInfo && !title && (
        <div style={{ marginBottom: 12, padding: 8, backgroundColor: "#ffffff", borderRadius: 6 }}>
          <DomainBadge 
            domain={domainInfo.domain} 
            subDomain={domainInfo.subDomain}
            confidence={domainInfo.confidence}
            size="medium"
          />
        </div>
      )}
      <pre style={{ whiteSpace: "pre-wrap", margin: 0, fontSize: 13, color: "#111827", overflow: "auto", maxHeight: "500px" }}>
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}


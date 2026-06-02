import React, { useMemo, useState } from "react";
import FileUploader from "../components/FileUploader.jsx";
import JsonViewer from "../components/JsonViewer.jsx";
import ScoreViewer from "../components/ScoreViewer.jsx";
import DomainBadge from "../components/DomainBadge.jsx";
import { uploadAndExtract, parseCvText, scoreProfile } from "../api/cvApi.js";

// Helper function to clean profile data for JSON serialization
function cleanProfileForSerialization(obj) {
  if (obj === null || obj === undefined) {
    return null;
  }
  
  if (typeof obj !== 'object') {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(cleanProfileForSerialization);
  }
  
  const cleaned = {};
  for (const [key, value] of Object.entries(obj)) {
    // Skip functions, undefined, and symbols
    if (typeof value === 'function' || value === undefined) {
      continue;
    }
    
    // Recursively clean nested objects
    if (typeof value === 'object' && value !== null) {
      cleaned[key] = cleanProfileForSerialization(value);
    } else {
      cleaned[key] = value;
    }
  }
  
  return cleaned;
}

export default function UploadFlow({ goHome }) {
  const [files, setFiles] = useState([]);
  const [extractRes, setExtractRes] = useState(null);
  const [fullText, setFullText] = useState(""); // normalized CV text for parse
  const [parseRes, setParseRes] = useState(null);
  const [scoreRes, setScoreRes] = useState(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [showExtraDetail, setShowExtraDetail] = useState(false);

  const canCheckProfile = files.length > 0 && !busy;

  async function onCheckProfile() {
    setErr("");
    setBusy(true);
    setExtractRes(null);
    setParseRes(null);
    setScoreRes(null);
    setFullText("");

    try {
      // Step 1: Extract text
      const extractData = await uploadAndExtract(files);
      setExtractRes(extractData);

      const text =
        extractData.text ||
        extractData.clean_text ||
        extractData.extracted_text ||
        extractData.text_preview ||
        "";

      setFullText(text);

      if (!text || text.trim().length < 50) {
        throw new Error("Extracted text is too short. Please try a different CV file.");
      }

      // Step 2: Parse with AI
      const parseData = await parseCvText(text);
      setParseRes(parseData);

      if (!parseData?.profile) {
        throw new Error("Failed to parse profile data.");
      }

      // Step 3: Score the profile
      let profileData;
      try {
        const cleaned = cleanProfileForSerialization(parseData.profile);
        profileData = JSON.parse(JSON.stringify(cleaned));
      } catch (jsonErr) {
        console.error("Failed to serialize profile:", jsonErr);
        throw new Error("Invalid profile data structure.");
      }

      if (typeof profileData !== 'object' || profileData === null) {
        throw new Error("Profile data is not a valid object");
      }

      const scoreData = await scoreProfile(profileData);
      console.log("Score response received:", scoreData);
      setScoreRes(scoreData);
    } catch (e) {
      const errorMsg = e?.response?.data?.detail || e.message || "Check profile failed";
      setErr(errorMsg);
      console.error("Check profile error:", e);
      if (e?.response?.data) {
        console.error("Response data:", e.response.data);
      }
    } finally {
      setBusy(false);
    }
  }

  const extractedMeta = useMemo(() => {
    if (!extractRes) return null;
    // Show only meta-ish keys
    const { status, meta, text_stats, note } = extractRes;
    return { status, meta, text_stats, note };
  }, [extractRes]);

  // Purple brand theme colors
  const purpleTheme = {
    primary: "#7c3aed", // Purple-600
    primaryLight: "#a78bfa", // Purple-400
    primaryDark: "#6d28d9", // Purple-700
    background: "#faf5ff", // Purple-50
  };

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: 24, background: "#ffffff" }}>
      <div style={{ display: "flex", justifyContent: "center", marginBottom: 32 }}>
        <h1 style={{ 
          margin: 0, 
          fontSize: 32, 
          fontWeight: 700, 
          color: purpleTheme.primary,
          textTransform: "uppercase",
          letterSpacing: "0.5px",
          textAlign: "center"
        }}>
          TrichyGold CV Shortlisting
        </h1>
      </div>

      {err && (
        <div style={{ background: "#ffe9e9", border: "1px solid #ffb3b3", padding: 10, borderRadius: 10, marginBottom: 12 }}>
          <b>Error:</b> {err}
        </div>
      )}

      <FileUploader files={files} setFiles={setFiles} onBack={goHome} />

      <div style={{ marginTop: 24, display: "flex", justifyContent: "center" }}>
        <button 
          disabled={!canCheckProfile || busy} 
          onClick={onCheckProfile}
          style={{
            padding: "16px 48px",
            backgroundColor: canCheckProfile && !busy ? purpleTheme.primary : purpleTheme.primaryLight,
            color: "white",
            border: "none",
            borderRadius: 8,
            cursor: canCheckProfile && !busy ? "pointer" : "not-allowed",
            fontWeight: 700,
            fontSize: 18,
            textTransform: "uppercase",
            letterSpacing: "0.5px",
            transition: "background-color 0.2s",
            opacity: canCheckProfile && !busy ? 1 : 0.6,
          }}
          onMouseOver={(e) => {
            if (canCheckProfile && !busy) {
              e.target.style.backgroundColor = purpleTheme.primaryDark;
            }
          }}
          onMouseOut={(e) => {
            if (canCheckProfile && !busy) {
              e.target.style.backgroundColor = purpleTheme.primary;
            }
          }}
        >
          {busy ? "Processing..." : "Check Profile"}
        </button>
      </div>

      {/* Domain Classification Preview */}
      {parseRes?.profile?.primary_domain && (
        <div style={{ marginTop: 20, marginBottom: 16, padding: 16, borderRadius: 8, backgroundColor: "#f9fafb", border: "1px solid #e5e7eb" }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: "#6b7280", marginBottom: 8, textTransform: "uppercase" }}>
            Domain Classification
          </div>
          <DomainBadge 
            domain={parseRes.profile.primary_domain}
            subDomain={parseRes.profile.sub_domain}
            confidence={parseRes.profile.domain_confidence}
            size="medium"
          />
        </div>
      )}

      {/* Score Report - Always visible when available */}
      {scoreRes && (
        <ScoreViewer report={scoreRes} profile={parseRes?.profile} />
      )}

      {/* Extra Detail Section - Collapsible */}
      {(extractRes || parseRes || scoreRes) && (
        <div style={{ marginTop: 24 }}>
          <button
            onClick={() => setShowExtraDetail(!showExtraDetail)}
            style={{
              padding: "10px 20px",
              backgroundColor: showExtraDetail ? purpleTheme.primaryDark : "#f3f4f6",
              color: showExtraDetail ? "white" : "#374151",
              border: `1px solid ${purpleTheme.primary}`,
              borderRadius: 6,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 15,
            }}
          >
            {showExtraDetail ? "▼" : "▶"} Extra Detail
          </button>

          {showExtraDetail && (
            <div style={{ marginTop: 16, border: `1px solid ${purpleTheme.primaryLight}`, borderRadius: 8, padding: 20, background: purpleTheme.background }}>
              {/* Normalized Text */}
              {fullText && (
                <div style={{ marginBottom: 24 }}>
                  <h3 style={{ marginTop: 0, marginBottom: 12, color: purpleTheme.primary, fontSize: 18, fontWeight: 600 }}>
                    Normalized Text
                  </h3>
                  <textarea
                    style={{ width: "100%", minHeight: 200, padding: 12, borderRadius: 6, border: `1px solid ${purpleTheme.primaryLight}`, fontFamily: "monospace", fontSize: 13 }}
                    value={fullText}
                    onChange={(e) => setFullText(e.target.value)}
                    placeholder="Normalized CV text will appear here after extraction..."
                  />
                </div>
              )}

              {/* Parse Data */}
              {parseRes && (
                <div style={{ marginBottom: 24 }}>
                  <h3 style={{ marginTop: 0, marginBottom: 12, color: purpleTheme.primary, fontSize: 18, fontWeight: 600 }}>
                    Parse Data (Profile JSON)
                  </h3>
                  <JsonViewer title="" data={parseRes} showDomainBadge={true} />
                </div>
              )}

              {/* Score Data */}
              {scoreRes && (
                <div>
                  <h3 style={{ marginTop: 0, marginBottom: 12, color: purpleTheme.primary, fontSize: 18, fontWeight: 600 }}>
                    Score Data (JSON)
                  </h3>
                  <JsonViewer title="" data={scoreRes} />
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


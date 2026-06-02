import React, { useRef } from "react";

// Purple brand theme
const PURPLE_THEME = {
  primary: "#7c3aed",
  primaryLight: "#a78bfa",
  primaryDark: "#6d28d9",
  background: "#faf5ff",
};

export default function FileUploader({ files, setFiles, onBack }) {
  const inputRef = useRef(null);

  function onPick(e) {
    const selected = Array.from(e.target.files || []);
    setFiles(selected);
  }

  function clear() {
    setFiles([]);
    if (inputRef.current) inputRef.current.value = "";
  }

  return (
    <div style={{ 
      border: `2px solid ${PURPLE_THEME.primaryLight}`, 
      padding: 24, 
      borderRadius: 12,
      background: PURPLE_THEME.background,
      boxShadow: "0 2px 4px rgba(124, 58, 237, 0.1)",
      position: "relative"
    }}>
      {onBack && (
        <button 
          onClick={onBack}
          style={{
            position: "absolute",
            top: 16,
            right: 16,
            padding: "8px 16px",
            backgroundColor: PURPLE_THEME.primary,
            color: "white",
            border: "none",
            borderRadius: 6,
            cursor: "pointer",
            fontWeight: 600,
            fontSize: 14,
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = PURPLE_THEME.primaryDark}
          onMouseOut={(e) => e.target.style.backgroundColor = PURPLE_THEME.primary}
        >
          Back
        </button>
      )}
      <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
        <label style={{
          padding: "12px 24px",
          backgroundColor: PURPLE_THEME.primary,
          color: "white",
          borderRadius: 8,
          cursor: "pointer",
          fontWeight: 600,
          fontSize: 15,
          display: "inline-block",
        }}>
          Choose Files
          <input
            ref={inputRef}
            type="file"
            multiple
            accept=".pdf,image/*"
            onChange={onPick}
            style={{ display: "none" }}
          />
        </label>
        {files.length > 0 && (
          <button 
            onClick={clear}
            style={{
              padding: "12px 24px",
              backgroundColor: "#ef4444",
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 15,
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = "#dc2626"}
            onMouseOut={(e) => e.target.style.backgroundColor = "#ef4444"}
          >
            Clear
          </button>
        )}
      </div>

      <div style={{ marginTop: 16 }}>
        <div style={{ 
          fontSize: 14, 
          fontWeight: 600, 
          color: PURPLE_THEME.primary,
          marginBottom: 8
        }}>
          Selected files:
        </div>
        {files.length === 0 ? (
          <div style={{ 
            color: "#6b7280", 
            fontStyle: "italic",
            padding: "12px",
            background: "white",
            borderRadius: 6,
            border: `1px dashed ${PURPLE_THEME.primaryLight}`
          }}>
            No files selected
          </div>
        ) : (
          <div style={{
            padding: "12px",
            background: "white",
            borderRadius: 6,
            border: `1px solid ${PURPLE_THEME.primaryLight}`
          }}>
            <ul style={{ margin: 0, paddingLeft: 20 }}>
              {files.map((f) => (
                <li key={`${f.name}-${f.size}`} style={{ marginBottom: 8, color: "#374151" }}>
                  <strong>{f.name}</strong> ({Math.round(f.size / 1024)} KB) — {f.type || "unknown"}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

import React from "react";

// Purple brand theme
const PURPLE_THEME = {
  primary: "#7c3aed",
  primaryLight: "#a78bfa",
  primaryDark: "#6d28d9",
  background: "#faf5ff",
};

export default function Dashboard({ goUpload }) {
  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: 40, background: "#ffffff" }}>
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "400px" }}>
        <div style={{ 
          border: `2px solid ${PURPLE_THEME.primaryLight}`, 
          padding: 40, 
          borderRadius: 16, 
          minWidth: 300,
          textAlign: "center",
          background: PURPLE_THEME.background,
          boxShadow: "0 4px 6px rgba(124, 58, 237, 0.1)"
        }}>
          <h2 style={{ 
            marginTop: 0, 
            marginBottom: 24,
            fontSize: 28, 
            fontWeight: 700, 
            color: PURPLE_THEME.primary,
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            TrichyGold CV Shortlisting
          </h2>
          <button 
            onClick={goUpload}
            style={{
              padding: "14px 32px",
              backgroundColor: PURPLE_THEME.primary,
              color: "white",
              border: "none",
              borderRadius: 8,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 16,
              textTransform: "uppercase",
              letterSpacing: "0.5px",
              transition: "background-color 0.2s",
            }}
            onMouseOver={(e) => e.target.style.backgroundColor = PURPLE_THEME.primaryDark}
            onMouseOut={(e) => e.target.style.backgroundColor = PURPLE_THEME.primary}
          >
            New CV Upload
          </button>
        </div>
      </div>
    </div>
  );
}

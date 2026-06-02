import React, { useState } from "react";
import Dashboard from "./pages/Dashboard.jsx";
import UploadFlow from "./pages/UploadFlow.jsx";

export default function App() {
  const [page, setPage] = useState("dashboard");

  if (page === "upload") {
    return <UploadFlow goHome={() => setPage("dashboard")} />;
  }

  return <Dashboard goUpload={() => setPage("upload")} />;
}


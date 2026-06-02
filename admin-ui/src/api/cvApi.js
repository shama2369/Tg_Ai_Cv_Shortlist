import axios from "axios";

// If your FastAPI runs on 127.0.0.1:8000
export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
});

// 1) Upload + extract text (PDF or images)
export async function uploadAndExtract(files) {
  const form = new FormData();
  // backend can accept single file or multiple — we send multiple
  for (const f of files) form.append("files", f);

  const res = await api.post("/api/cv/extract", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

// 2) Parse with AI (text -> profile)
export async function parseCvText(text) {
  const res = await api.post("/api/cv/parse", { text });
  return res.data;
}

// 3) Score (profile -> score report)
export async function scoreProfile(profile) {
  // Ensure profile is a plain object
  // Axios will automatically serialize to JSON, but we ensure it's a plain object first
  const requestBody = { profile };
  
  // Validate that we can serialize it
  try {
    JSON.stringify(requestBody);
  } catch (e) {
    throw new Error(`Cannot serialize profile data: ${e.message}`);
  }
  
  const res = await api.post("/api/cv/score", requestBody);
  return res.data;
}


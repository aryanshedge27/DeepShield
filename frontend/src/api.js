const BASE = import.meta.env.VITE_API_URL || "http://localhost:5000";

export async function analyseMedia(file, onProgress) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE}/analyse`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error((await res.json()).error || "Server error");
  return res.json();
}

export async function verifyHash(sha256) {
  const res = await fetch(`${BASE}/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sha256 }),
  });
  if (!res.ok) throw new Error("Verification failed");
  return res.json();
}

export async function fetchHistory(page = 1) {
  const res = await fetch(`${BASE}/history?page=${page}`);
  return res.json();
}
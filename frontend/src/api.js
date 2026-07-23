const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8010";

async function handle(response) {
  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // ignore body parse failure
    }
    throw new Error(message);
  }
  return response.json();
}

export async function uploadExcel(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
  return handle(res);
}

export async function confirmSession(sessionId) {
  const res = await fetch(`${API_BASE}/api/${sessionId}/confirm`, {
    method: "POST",
  });
  return handle(res);
}

export async function createGroups(sessionId) {
  const res = await fetch(`${API_BASE}/api/${sessionId}/groups`, {
    method: "POST",
  });
  return handle(res);
}

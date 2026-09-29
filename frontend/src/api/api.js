// Central place for every request the frontend makes to the FastAPI
// backend. Components should never call fetch() directly -- they should
// import functions from here instead.

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkErr) {
    // The API is unreachable (server not running, CORS misconfigured, no
    // internet, etc). Never surface the raw error to the UI.
    throw new ApiError(
      "We couldn't reach the estimator service. Make sure the backend is running and try again.",
      0
    );
  }

  let body = null;
  try {
    body = await response.json();
  } catch {
    // Non-JSON or empty body -- fine for some responses, ignore.
  }

  if (!response.ok) {
    const detail =
      (body && (body.detail || body.message)) ||
      "We couldn't calculate your estimate right now. Please try again.";
    throw new ApiError(typeof detail === "string" ? detail : JSON.stringify(detail), response.status);
  }

  return body;
}

export function getHealth() {
  return request("/api/health");
}

export function getBrands() {
  return request("/api/brands");
}

export function getDevices({ brand, search } = {}) {
  const params = new URLSearchParams();
  if (brand) params.set("brand", brand);
  if (search) params.set("search", search);
  const qs = params.toString();
  return request(`/api/devices${qs ? `?${qs}` : ""}`);
}

export function getDevice(deviceId) {
  return request(`/api/devices/${encodeURIComponent(deviceId)}`);
}

export function getRepairs() {
  return request("/api/repairs");
}

export function getRepair(repairId) {
  return request(`/api/repairs/${encodeURIComponent(repairId)}`);
}

export function calculateEstimate(payload) {
  return request("/api/estimate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export { ApiError };

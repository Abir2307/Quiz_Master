import API_BASE_URL from "@/config";

export async function apiFetch(url, options = {}) {
  return fetch(`${API_BASE_URL}${url}`, {
    credentials: "include",
    ...options,
  });
}

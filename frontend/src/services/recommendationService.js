import { getToken } from './authService';

const API_URL = 'http://localhost:8000';

export async function getCourseRecommendations({ k = 10, enforce_prereqs = true } = {}) {
  const token = getToken();
  const params = new URLSearchParams();
  params.append('k', k);
  params.append('enforce_prereqs', enforce_prereqs ? 'true' : 'false');

  const res = await fetch(`${API_URL}/recommendations/courses?${params.toString()}`, {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to fetch recommendations (${res.status})`);
  }

  return res.json();
}

/**
 * Standardized API client for TenderForge frontend communicating with FastAPI backend.
 */

const API_BASE = '/api/v1';

export function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('tf_token');
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  headers['X-User-Role'] = localStorage.getItem('tf_user_role') || 'Admin';
  headers['X-User-Id'] = localStorage.getItem('tf_user_id') || 'usr-system-admin';
  return headers;
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<{ success: boolean; data?: T; message?: string; errors?: any[] }> {
  const defaultHeaders = getAuthHeaders();
  const headers = options.headers
    ? { ...defaultHeaders, ...options.headers }
    : defaultHeaders;

  if (options.body instanceof FormData) {
    delete (headers as any)['Content-Type'];
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      localStorage.removeItem('tf_token');
      window.dispatchEvent(new Event('auth-expired'));
    }

    const json = await response.json();
    return json;
  } catch (error: any) {
    console.error(`API Error on ${endpoint}:`, error);
    return {
      success: false,
      message: error.message || 'Network request failed',
    };
  }
}

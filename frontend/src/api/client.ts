const DEFAULT_BASE = '';

export const apiBase = String(import.meta.env.VITE_API_BASE_URL || DEFAULT_BASE).replace(/\/$/, '');

const DEMO_USER_KEY = 'edumind.demoUserId';
const TOKEN_KEY = 'edumind.accessToken';

function currentDemoUserId() {
  return localStorage.getItem(DEMO_USER_KEY) || 'demo-basic';
}

function shouldAppendUserId(pathname: string) {
  return [
    '/api/v1/student/learning-tasks',
    '/api/v1/learning-paths/recommend',
    '/api/v1/resources/recommendations',
    '/api/v1/tutor/history',
    '/api/v1/quiz/chapter'
  ].some((prefix) => pathname.startsWith(prefix));
}

function withDemoUser(path: string, init?: RequestInit) {
  const userId = currentDemoUserId();
  const method = String(init?.method || 'GET').toUpperCase();
  const url = new URL(path, window.location.origin);
  if (method === 'GET' && shouldAppendUserId(url.pathname) && !url.searchParams.has('user_id')) {
    url.searchParams.set('user_id', userId);
  }
  const headers = new Headers(init?.headers);
  if (shouldAppendUserId(url.pathname)) {
    headers.set('X-Demo-User-Id', userId);
  }
  const token = localStorage.getItem(TOKEN_KEY);
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  return {
    path: `${url.pathname}${url.search}${url.hash}`,
    init: { ...init, headers }
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const requestInfo = withDemoUser(path, init);
  const response = await fetch(`${apiBase}${requestInfo.path}`, requestInfo.init);
  const text = await response.text();
  let payload: any = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    if (!response.ok) throw new Error(text || `请求失败：${response.status}`);
    throw new Error(`响应解析失败：${text.slice(0, 100)}`);
  }
  if (!response.ok) {
    const detail = payload?.detail
      ? (typeof payload.detail === 'string' ? payload.detail : JSON.stringify(payload.detail))
      : `请求失败：${response.status}`;
    throw new Error(detail);
  }
  return payload as T;
}

async function download(path: string, init?: RequestInit): Promise<{ blob: Blob; filename: string }> {
  const requestInfo = withDemoUser(path, init);
  const response = await fetch(`${apiBase}${requestInfo.path}`, requestInfo.init);
  if (!response.ok) {
    const text = await response.text();
    let detail = text || `请求失败：${response.status}`;
    try {
      const payload = text ? JSON.parse(text) : null;
      detail = typeof payload?.detail === 'string' ? payload.detail : detail;
    } catch {
      // 非 JSON 错误响应沿用脱敏后的文本摘要。
    }
    throw new Error(detail.slice(0, 300));
  }
  const disposition = response.headers.get('Content-Disposition') || '';
  const filenameMatch = disposition.match(/filename\*?=(?:UTF-8''|\")?([^\";]+)/i);
  return {
    blob: await response.blob(),
    filename: decodeURIComponent(filenameMatch?.[1] || 'download.bin')
  };
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined
    }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, formData: FormData) => request<T>(path, { method: 'POST', body: formData }),
  download: (path: string, init?: RequestInit) => download(path, init)
};

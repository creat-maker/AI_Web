import type { ApiResponse } from '../types';

const DEFAULT_API_BASE_URL = 'http://localhost:8000';

const resolveApiBaseUrl = () => {
  const configuredBaseUrl = String(import.meta.env.VITE_API_BASE_URL || '').trim();
  if (/^https?:\/\//i.test(configuredBaseUrl)) {
    return configuredBaseUrl.replace(/\/$/, '');
  }
  return DEFAULT_API_BASE_URL;
};

class ApiError extends Error {
  status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export const API_BASE_URL = resolveApiBaseUrl();

const buildUrl = (path: string) => `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;

const extractFilename = (contentDisposition: string | null) => {
  if (!contentDisposition) return null;

  const utf8Match = contentDisposition.match(/filename\*=UTF-8''([^;]+)/i);
  if (utf8Match?.[1]) {
    try {
      return decodeURIComponent(utf8Match[1]);
    } catch {
      return utf8Match[1];
    }
  }

  const asciiMatch = contentDisposition.match(/filename="([^"]+)"|filename=([^;]+)/i);
  const filename = asciiMatch?.[1] || asciiMatch?.[2];
  return filename ? filename.trim() : null;
};

const parseErrorMessage = (payload: unknown, status: number) => {
  if (status === 401) {
    return '请前往设置配置 API Key';
  }

  if (status >= 500) {
    return '后端服务开小差了，请查看服务端日志';
  }

  if (payload && typeof payload === 'object') {
    const detail = (payload as { detail?: unknown }).detail;
    const message = (payload as { message?: unknown }).message;
    if (typeof detail === 'string') return detail;
    if (typeof message === 'string') return message;
  }
  return `请求失败 (${status})`;
};

const normalizeRequestError = (error: unknown) => {
  if (error instanceof ApiError) {
    return error;
  }

  const rawMessage = error instanceof Error ? error.message : '';
  if (/failed to fetch|networkerror|load failed/i.test(rawMessage)) {
    return new ApiError('网络连接失败，请检查后端 API 服务 (端口8000) 是否已启动！');
  }

  return new ApiError(rawMessage || '请求发送失败，请稍后重试');
};

const parseErrorPayload = (text: string) => {
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
};

async function request<T>(path: string, init?: RequestInit): Promise<ApiResponse<T>> {
  let response: Response;
  try {
    response = await fetch(buildUrl(path), init);
  } catch (error) {
    throw normalizeRequestError(error);
  }

  const text = await response.text();
  const payload = parseErrorPayload(text);

  if (!response.ok) {
    throw new ApiError(parseErrorMessage(payload, response.status), response.status);
  }

  return payload as ApiResponse<T>;
}

export const apiClient = {
  get<T>(path: string) {
    return request<T>(path, {
      method: 'GET',
    });
  },

  post<T>(path: string, body?: unknown) {
    return request<T>(path, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  put<T>(path: string, body?: unknown) {
    return request<T>(path, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  },

  delete<T>(path: string) {
    return request<T>(path, {
      method: 'DELETE',
    });
  },

  postForm<T>(path: string, formData: FormData) {
    return request<T>(path, {
      method: 'POST',
      body: formData,
    });
  },

  async download(path: string) {
    let response: Response;
    try {
      response = await fetch(buildUrl(path), {
        method: 'GET',
      });
    } catch (error) {
      throw normalizeRequestError(error);
    }

    if (!response.ok) {
      const text = await response.text();
      throw new ApiError(parseErrorMessage(parseErrorPayload(text), response.status), response.status);
    }

    return {
      blob: await response.blob(),
      filename: extractFilename(response.headers.get('Content-Disposition')),
    };
  },
};

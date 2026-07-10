// Environment-agnostic request logic shared by lib/api.ts (client) and
// lib/api-server.ts (server). Neither of those two ever imports the other —
// see lib/api.ts for why that split exists.

const API_URL = process.env.NEXT_PUBLIC_API_URL;

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, message: string, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

export type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
};

export function createApiClient(getAccessToken: () => Promise<string | undefined>) {
  async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const token = await getAccessToken();

    const headers = new Headers(options.headers);
    headers.set("Content-Type", "application/json");
    if (token) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
    });

    if (!res.ok) {
      let body: unknown;
      try {
        body = await res.json();
      } catch {
        body = undefined;
      }
      throw new ApiError(res.status, `Request to ${path} failed with ${res.status}`, body);
    }

    if (res.status === 204) {
      return undefined as T;
    }

    return (await res.json()) as T;
  }

  return {
    get: <T>(path: string, options?: RequestOptions) => request<T>(path, { ...options, method: "GET" }),
    post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
      request<T>(path, { ...options, method: "POST", body }),
    put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
      request<T>(path, { ...options, method: "PUT", body }),
    patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
      request<T>(path, { ...options, method: "PATCH", body }),
    delete: <T>(path: string, options?: RequestOptions) => request<T>(path, { ...options, method: "DELETE" }),
  };
}

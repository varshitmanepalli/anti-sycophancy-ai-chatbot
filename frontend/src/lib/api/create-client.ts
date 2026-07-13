import "./axios-augment";

import axios, { type AxiosInstance, type AxiosResponse } from "axios";

import { API_TIMEOUT_MS, env } from "@/config";

import { setupApiInterceptors } from "./interceptors";
import type { ApiRequestConfig, ApiResult } from "./types";

export interface CreateApiClientOptions {
  baseURL?: string;
  timeout?: number;
  withAuth?: boolean;
}

function toApiResult<T>(response: AxiosResponse<T>): ApiResult<T> {
  const headers: Record<string, string> = {};
  Object.entries(response.headers).forEach(([key, value]) => {
    if (typeof value === "string") headers[key] = value;
  });

  return {
    data: response.data,
    status: response.status,
    headers,
  };
}

/** Create a configured Axios instance with interceptors. */
export function createApiClient(options: CreateApiClientOptions = {}): AxiosInstance {
  const client = axios.create({
    baseURL: options.baseURL ?? env.clientApiUrl,
    headers: { "Content-Type": "application/json" },
    timeout: options.timeout ?? API_TIMEOUT_MS,
  });

  if (options.withAuth !== false) {
    setupApiInterceptors(client);
  }

  return client;
}

/** Typed HTTP helpers built on top of an Axios instance. */
export function createApiMethods(client: AxiosInstance) {
  return {
    get<T>(url: string, config?: ApiRequestConfig): Promise<T> {
      return client.get<T>(url, config).then((res) => res.data);
    },

    post<T, B = unknown>(url: string, body?: B, config?: ApiRequestConfig): Promise<T> {
      return client.post<T>(url, body, config).then((res) => res.data);
    },

    put<T, B = unknown>(url: string, body?: B, config?: ApiRequestConfig): Promise<T> {
      return client.put<T>(url, body, config).then((res) => res.data);
    },

    patch<T, B = unknown>(url: string, body?: B, config?: ApiRequestConfig): Promise<T> {
      return client.patch<T>(url, body, config).then((res) => res.data);
    },

    delete<T>(url: string, config?: ApiRequestConfig): Promise<T> {
      return client.delete<T>(url, config).then((res) => res.data);
    },

    /** Return full response metadata alongside typed data. */
    request<T>(url: string, config?: ApiRequestConfig): Promise<ApiResult<T>> {
      return client.request<T>({ url, ...config }).then(toApiResult);
    },
  };
}

export type ApiMethods = ReturnType<typeof createApiMethods>;

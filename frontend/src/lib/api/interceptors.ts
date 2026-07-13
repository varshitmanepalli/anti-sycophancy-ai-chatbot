import type {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from "axios";

import { authTokenStore } from "./auth-token-store";
import { ApiRequestError, parseApiErrorMessage, toApiRequestError } from "./errors";
import { refreshAccessToken } from "./refresh-token";
import { retryRequest } from "./retry";
import type { ApiInternalConfig } from "./types";

function setAuthHeader(config: InternalAxiosRequestConfig, token: string): void {
  if (typeof config.headers.set === "function") {
    config.headers.set("Authorization", `Bearer ${token}`);
  } else {
    (config.headers as Record<string, string>).Authorization = `Bearer ${token}`;
  }
}

/** Attach Authorization header when an access token is available. */
function authRequestInterceptor(config: InternalAxiosRequestConfig): InternalAxiosRequestConfig {
  const apiConfig = config as ApiInternalConfig;
  if (apiConfig.skipAuth) return config;

  const token = authTokenStore.getAccessToken();
  if (token) {
    setAuthHeader(config, token);
  }

  return config;
}

/** Attempt token refresh and replay the original request on 401. */
async function authResponseInterceptor(
  client: AxiosInstance,
  error: AxiosError,
): Promise<AxiosResponse> {
  const config = error.config as ApiInternalConfig | undefined;
  const status = error.response?.status;

  if (!config || status !== 401 || config.skipAuth || config.skipRefresh || config._retryAfterRefresh) {
    throw toApiRequestError(error);
  }

  config._retryAfterRefresh = true;

  const newToken = await refreshAccessToken();
  if (!newToken) {
    throw new ApiRequestError("Session expired. Please sign in again.", {
      status: 401,
      code: "UNAUTHORIZED",
    });
  }

  setAuthHeader(config, newToken);
  return client.request(config);
}

/** Normalize Axios errors into ApiRequestError, with optional retry. */
async function errorResponseInterceptor(
  client: AxiosInstance,
  error: AxiosError,
): Promise<AxiosResponse> {
  if (error.response?.status === 401) {
    return authResponseInterceptor(client, error);
  }

  try {
    return (await retryRequest(client, error)) as AxiosResponse;
  } catch (retryError) {
    if (retryError && typeof retryError === "object" && "isAxiosError" in retryError) {
      const axiosRetryError = retryError as AxiosError;
      throw new ApiRequestError(parseApiErrorMessage(axiosRetryError as AxiosError<import("@/types").ApiErrorBody>), {
        status: axiosRetryError.response?.status,
        details: axiosRetryError.response?.data,
      });
    }
    throw toApiRequestError(retryError);
  }
}

/** Register request/response interceptors on an Axios instance. */
export function setupApiInterceptors(client: AxiosInstance): void {
  client.interceptors.request.use(authRequestInterceptor);

  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError) => errorResponseInterceptor(client, error),
  );
}

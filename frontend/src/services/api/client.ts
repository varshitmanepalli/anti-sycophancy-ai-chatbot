/**
 * Re-exports the shared API client from the reusable API layer.
 * @see {@link @/lib/api}
 */
export {
  api,
  apiBaseUrl,
  apiClient,
  ApiRequestError,
  authTokenStore,
  createApiClient,
  createApiMethods,
  openSseStream,
  parseApiErrorMessage,
  refreshAccessToken,
  setRefreshHandler,
  StreamError,
  toApiRequestError,
} from "@/lib/api";

export type {
  ApiErrorCode,
  ApiMethods,
  ApiRequestConfig,
  ApiResult,
  AuthTokens,
  RefreshTokenResponse,
  RetryOptions,
} from "@/lib/api";

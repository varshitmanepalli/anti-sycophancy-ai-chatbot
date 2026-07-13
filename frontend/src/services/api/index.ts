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
} from "./client";

export type {
  ApiErrorCode,
  ApiMethods,
  ApiRequestConfig,
  ApiResult,
  AuthTokens,
  RefreshTokenResponse,
  RetryOptions,
} from "./client";

export { login, logout, isAuthenticated, type LoginRequest, type LoginResponse } from "./auth.service";
export { sendChatMessage, sendPipelineMessage, streamChatMessage, streamChatWithRetry, StreamChatError } from "./chat.service";
export { submitMessageFeedback } from "./feedback.service";
export { checkHealth, checkReady } from "./health.service";

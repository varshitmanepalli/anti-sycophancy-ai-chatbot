import "./axios-augment";

import { createApiClient, createApiMethods } from "./create-client";

/** Shared Axios instance for all backend API calls. */
export const apiClient = createApiClient();

/** Typed convenience methods (`get`, `post`, `put`, `patch`, `delete`, `request`). */
export const api = createApiMethods(apiClient);

/** Base URL used by the shared client — useful for SSE fetch calls. */
export const apiBaseUrl = apiClient.defaults.baseURL ?? "/api";

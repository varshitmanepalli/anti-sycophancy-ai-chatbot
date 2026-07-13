import "axios";

declare module "axios" {
  export interface AxiosRequestConfig {
    skipAuth?: boolean;
    skipRefresh?: boolean;
    retry?: import("./types").RetryOptions | false;
    _retryAfterRefresh?: boolean;
    _retryCount?: number;
  }

  export interface InternalAxiosRequestConfig {
    skipAuth?: boolean;
    skipRefresh?: boolean;
    retry?: import("./types").RetryOptions | false;
    _retryAfterRefresh?: boolean;
    _retryCount?: number;
  }
}

export {};

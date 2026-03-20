import type {
  ApiError,
  NetworkError,
  TimeoutError,
  ValidationError,
  BusinessError,
  AppError
} from '~/types/errors';

/**
 * 检查是否为ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  if (error instanceof Error) {
    return 'response' in error &&
           typeof (error as ApiError).response?.status === 'number';
  }
  return false;
}

/**
 * 检查是否为NetworkError
 */
export function isNetworkError(error: unknown): error is NetworkError {
  if (error instanceof Error) {
    const code = (error as NetworkError).code;
    return code === 'NETWORK_ERROR' ||
           code === 'ECONNABORTED' ||
           code === 'ETIMEDOUT' ||
           error.message.includes('Network Error') ||
           error.message.includes('timeout');
  }
  return false;
}

/**
 * 检查是否为TimeoutError
 */
export function isTimeoutError(error: unknown): error is TimeoutError {
  if (error instanceof Error) {
    const code = (error as TimeoutError).code;
    return code === 'ECONNABORTED' ||
           error.message.includes('timeout') ||
           error.message.includes('ECONNABORTED');
  }
  return false;
}

/**
 * 检查是否为ValidationError
 */
export function isValidationError(error: unknown): error is ValidationError {
  if (error instanceof Error) {
    return 'fields' in error &&
           typeof (error as ValidationError).fields === 'object';
  }
  return false;
}

/**
 * 检查是否为BusinessError
 */
export function isBusinessError(error: unknown): error is BusinessError {
  if (error instanceof Error) {
    return 'businessCode' in error || 'businessMessage' in error;
  }
  return false;
}

/**
 * 检查是否为AppError
 */
export function isAppError(error: unknown): error is AppError {
  return isApiError(error) ||
         isNetworkError(error) ||
         isTimeoutError(error) ||
         isValidationError(error) ||
         isBusinessError(error);
}

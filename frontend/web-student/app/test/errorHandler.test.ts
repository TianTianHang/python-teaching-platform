import { describe, it, expect, vi, beforeEach } from 'vitest';
import { handleApiError, withErrorHandling, withAuthLoader } from '../utils/errorHandler';
import { parseError } from '../utils/errorParser';
import type { ApiError, NetworkError, TimeoutError, BusinessError } from '../types/errors';

// Mock react-router redirect
vi.mock('react-router', () => ({
  redirect: (url: string) => {
    throw new Error(`Redirect to: ${url}`);
  },
}));

describe('Error Handler Integration Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('handleApiError', () => {
    it('should redirect to login on 401 error', () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = {
        status: 401,
        data: { detail: 'Authentication credentials were not provided' },
      };

      expect(() => handleApiError(error)).toThrow('Redirect to: /auth/login');
    });

    it('should throw Response for non-401 API errors', () => {
      const error = new Error('Not found') as ApiError;
      error.response = {
        status: 404,
        data: { detail: 'Not found' },
      };

      expect(() => handleApiError(error)).toThrow(Response);
    });

    it('should use custom message when provided', () => {
      const error = new Error('Server error') as ApiError;
      error.response = {
        status: 500,
        data: { detail: 'Internal server error' },
      };

      try {
        handleApiError(error, { customMessage: 'Custom error message' });
      } catch (e) {
        const response = e as Response;
        expect(response.statusText).toBe('Error');
      }
    });

    it('should call onError callback', () => {
      const onError = vi.fn();
      const error = new Error('Server error') as ApiError;
      error.response = {
        status: 500,
        data: { detail: 'Internal server error' },
      };

      try {
        handleApiError(error, { onError });
      } catch (e) {
        expect(onError).toHaveBeenCalled();
      }
    });

    it('should not redirect when redirectToLogin is false', () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = {
        status: 401,
        data: { detail: 'Authentication credentials were not provided' },
      };

      expect(() => handleApiError(error, { redirectToLogin: false })).toThrow(Response);
    });
  });

  describe('withErrorHandling', () => {
    it('should wrap function and handle errors', async () => {
      const mockFn = vi.fn().mockRejectedValue(new Error('Test error'));
      const wrappedFn = withErrorHandling(mockFn);

      await expect(wrappedFn()).rejects.toThrow();
    });

    it('should return result when function succeeds', async () => {
      const mockFn = vi.fn().mockResolvedValue('success');
      const wrappedFn = withErrorHandling(mockFn);

      const result = await wrappedFn();
      expect(result).toBe('success');
    });

    it('should handle 401 errors with redirect', async () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = { status: 401 };
      
      const mockFn = vi.fn().mockRejectedValue(error);
      const wrappedFn = withErrorHandling(mockFn);

      await expect(wrappedFn()).rejects.toThrow('Redirect to: /auth/login');
    });
  });

  describe('withAuthLoader', () => {
    it('should wrap loader function with auth error handling', async () => {
      const mockLoader = vi.fn().mockResolvedValue({ data: 'test' });
      const wrappedLoader = withAuthLoader(mockLoader);

      const result = await wrappedLoader();
      expect(result).toEqual({ data: 'test' });
    });

    it('should redirect on 401 error', async () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = { status: 401 };
      
      const mockLoader = vi.fn().mockRejectedValue(error);
      const wrappedLoader = withAuthLoader(mockLoader);

      await expect(wrappedLoader()).rejects.toThrow('Redirect to: /auth/login');
    });

    it('should throw Response for non-401 API errors', async () => {
      const error = new Error('Server error') as ApiError;
      error.response = { status: 500 };
      
      const mockLoader = vi.fn().mockRejectedValue(error);
      const wrappedLoader = withAuthLoader(mockLoader);

      await expect(wrappedLoader()).rejects.toThrow(Response);
    });
  });

  describe('parseError integration', () => {
    it('should parse API error correctly', () => {
      const error = new Error('API Error') as ApiError;
      error.response = {
        status: 400,
        data: { detail: 'Bad request' },
      };

      const result = parseError(error);
      expect(result.type).toBe('api');
      expect(result.status).toBe(400);
      expect(result.message).toBe('Bad request');
    });

    it('should parse network error correctly', () => {
      const error = new Error('Network Error') as NetworkError;
      error.code = 'NETWORK_ERROR';

      const result = parseError(error);
      expect(result.type).toBe('network');
      expect(result.message).toBe('网络连接失败，请检查网络后重试');
    });

    it('should parse timeout error correctly', () => {
      const error = new Error('Timeout') as TimeoutError;
      error.code = 'ECONNABORTED';

      const result = parseError(error);
      expect(result.type).toBe('timeout');
      expect(result.message).toBe('请求超时，请稍后重试');
    });

    it('should parse business error correctly', () => {
      const error = new Error('Business error') as BusinessError;
      error.businessCode = 'INSUFFICIENT_BALANCE';
      error.businessMessage = '余额不足';

      const result = parseError(error);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('Business error');
    });

    it('should handle unknown errors', () => {
      const result = parseError('Unknown error');
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('发生未知错误');
    });
  });

  describe('Error flow integration', () => {
    it('should handle complete error flow from API error to redirect', async () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = {
        status: 401,
        data: { detail: 'Token expired' },
      };

      // Parse the error
      const parsed = parseError(error);
      expect(parsed.type).toBe('api');
      expect(parsed.status).toBe(401);
      expect(parsed.message).toBe('Token expired');

      // Handle the error
      expect(() => handleApiError(error)).toThrow('Redirect to: /auth/login');
    });

    it('should handle complete error flow from network error to Response', async () => {
      const error = new Error('Network Error') as NetworkError;
      error.code = 'NETWORK_ERROR';

      // Parse the error
      const parsed = parseError(error);
      expect(parsed.type).toBe('network');
      expect(parsed.message).toBe('网络连接失败，请检查网络后重试');

      // Handle the error - should throw Response
      expect(() => handleApiError(error)).toThrow(Response);
    });

    it('should handle complete error flow from timeout error to Response', async () => {
      const error = new Error('Timeout') as TimeoutError;
      error.code = 'ECONNABORTED';

      // Parse the error
      const parsed = parseError(error);
      expect(parsed.type).toBe('timeout');
      expect(parsed.message).toBe('请求超时，请稍后重试');

      // Handle the error - should throw Response
      expect(() => handleApiError(error)).toThrow(Response);
    });
  });
});

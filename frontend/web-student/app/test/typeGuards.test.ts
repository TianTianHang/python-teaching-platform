import { describe, it, expect } from 'vitest';
import {
  isApiError,
  isNetworkError,
  isTimeoutError,
  isValidationError,
  isBusinessError,
  isAppError,
} from '../utils/typeGuards';
import type {
  ApiError,
  NetworkError,
  TimeoutError,
  ValidationError,
  BusinessError,
} from '../types/errors';

describe('Type Guards', () => {
  describe('isApiError', () => {
    it('should return true for valid ApiError', () => {
      const error = new Error('API Error') as ApiError;
      error.response = {
        status: 400,
        statusText: 'Bad Request',
        data: { detail: 'Invalid request' },
      };

      expect(isApiError(error)).toBe(true);
    });

    it('should return true for 401 ApiError', () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = { status: 401 };

      expect(isApiError(error)).toBe(true);
    });

    it('should return true for 500 ApiError', () => {
      const error = new Error('Server Error') as ApiError;
      error.response = { status: 500 };

      expect(isApiError(error)).toBe(true);
    });

    it('should return false for plain Error', () => {
      const error = new Error('Plain error');
      expect(isApiError(error)).toBe(false);
    });

    it('should return false for null', () => {
      expect(isApiError(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isApiError(undefined)).toBe(false);
    });

    it('should return false for string', () => {
      expect(isApiError('error string')).toBe(false);
    });

    it('should return false for object without response', () => {
      const error = new Error('Error') as ApiError;
      expect(isApiError(error)).toBe(false);
    });

    it('should return false for object with invalid response', () => {
      const error = new Error('Error') as ApiError;
      error.response = { status: 'invalid' } as unknown as ApiError['response'];

      expect(isApiError(error)).toBe(false);
    });
  });

  describe('isNetworkError', () => {
    it('should return true for NETWORK_ERROR code', () => {
      const error = new Error('Network Error') as NetworkError;
      error.code = 'NETWORK_ERROR';

      expect(isNetworkError(error)).toBe(true);
    });

    it('should return true for ECONNABORTED code', () => {
      const error = new Error('Connection aborted') as NetworkError;
      error.code = 'ECONNABORTED';

      expect(isNetworkError(error)).toBe(true);
    });

    it('should return true for ETIMEDOUT code', () => {
      const error = new Error('Timeout') as NetworkError;
      error.code = 'ETIMEDOUT';

      expect(isNetworkError(error)).toBe(true);
    });

    it('should return true for error with "Network Error" message', () => {
      const error = new Error('Network Error');

      expect(isNetworkError(error)).toBe(true);
    });

    it('should return true for error with "timeout" in message', () => {
      const error = new Error('Request timeout');

      expect(isNetworkError(error)).toBe(true);
    });

    it('should return false for plain Error', () => {
      const error = new Error('Some other error');
      expect(isNetworkError(error)).toBe(false);
    });

    it('should return false for null', () => {
      expect(isNetworkError(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isNetworkError(undefined)).toBe(false);
    });

    it('should return false for string', () => {
      expect(isNetworkError('error string')).toBe(false);
    });
  });

  describe('isTimeoutError', () => {
    it('should return true for ECONNABORTED code', () => {
      const error = new Error('Connection aborted') as TimeoutError;
      error.code = 'ECONNABORTED';

      expect(isTimeoutError(error)).toBe(true);
    });

    it('should return true for error with "timeout" in message', () => {
      const error = new Error('Request timeout');

      expect(isTimeoutError(error)).toBe(true);
    });

    it('should return true for error with "ECONNABORTED" in message', () => {
      const error = new Error('ECONNABORTED');

      expect(isTimeoutError(error)).toBe(true);
    });

    it('should return false for NETWORK_ERROR code', () => {
      const error = new Error('Network Error') as NetworkError;
      error.code = 'NETWORK_ERROR';

      expect(isTimeoutError(error)).toBe(false);
    });

    it('should return false for plain Error', () => {
      const error = new Error('Some other error');
      expect(isTimeoutError(error)).toBe(false);
    });

    it('should return false for null', () => {
      expect(isTimeoutError(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isTimeoutError(undefined)).toBe(false);
    });

    it('should return false for string', () => {
      expect(isTimeoutError('error string')).toBe(false);
    });
  });

  describe('isValidationError', () => {
    it('should return true for ValidationError with fields', () => {
      const error = new Error('Validation failed') as ValidationError;
      error.fields = { email: ['Invalid email format'] };

      expect(isValidationError(error)).toBe(true);
    });

    it('should return true for ValidationError with multiple fields', () => {
      const error = new Error('Validation failed') as ValidationError;
      error.fields = {
        email: ['Invalid email format'],
        password: ['Too short'],
      };

      expect(isValidationError(error)).toBe(true);
    });

    it('should return false for plain Error', () => {
      const error = new Error('Plain error');
      expect(isValidationError(error)).toBe(false);
    });

    it('should return false for null', () => {
      expect(isValidationError(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isValidationError(undefined)).toBe(false);
    });

    it('should return false for string', () => {
      expect(isValidationError('error string')).toBe(false);
    });

    it('should return false for object with fields as string', () => {
      const error = new Error('Error') as ValidationError;
      error.fields = 'invalid' as unknown as ValidationError['fields'];

      expect(isValidationError(error)).toBe(false);
    });
  });

  describe('isBusinessError', () => {
    it('should return true for BusinessError with businessCode', () => {
      const error = new Error('Business error') as BusinessError;
      error.businessCode = 'INSUFFICIENT_BALANCE';

      expect(isBusinessError(error)).toBe(true);
    });

    it('should return true for BusinessError with businessMessage', () => {
      const error = new Error('Business error') as BusinessError;
      error.businessMessage = 'Insufficient balance';

      expect(isBusinessError(error)).toBe(true);
    });

    it('should return true for BusinessError with both fields', () => {
      const error = new Error('Business error') as BusinessError;
      error.businessCode = 'INSUFFICIENT_BALANCE';
      error.businessMessage = 'Insufficient balance';

      expect(isBusinessError(error)).toBe(true);
    });

    it('should return false for plain Error', () => {
      const error = new Error('Plain error');
      expect(isBusinessError(error)).toBe(false);
    });

    it('should return false for null', () => {
      expect(isBusinessError(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isBusinessError(undefined)).toBe(false);
    });

    it('should return false for string', () => {
      expect(isBusinessError('error string')).toBe(false);
    });
  });

  describe('isAppError', () => {
    it('should return true for ApiError', () => {
      const error = new Error('API Error') as ApiError;
      error.response = { status: 400 };

      expect(isAppError(error)).toBe(true);
    });

    it('should return true for NetworkError', () => {
      const error = new Error('Network Error') as NetworkError;
      error.code = 'NETWORK_ERROR';

      expect(isAppError(error)).toBe(true);
    });

    it('should return true for TimeoutError', () => {
      const error = new Error('Timeout') as TimeoutError;
      error.code = 'ECONNABORTED';

      expect(isAppError(error)).toBe(true);
    });

    it('should return true for ValidationError', () => {
      const error = new Error('Validation failed') as ValidationError;
      error.fields = { email: ['Invalid'] };

      expect(isAppError(error)).toBe(true);
    });

    it('should return true for BusinessError', () => {
      const error = new Error('Business error') as BusinessError;
      error.businessCode = 'ERROR_CODE';

      expect(isAppError(error)).toBe(true);
    });

    it('should return false for plain Error', () => {
      const error = new Error('Plain error');
      expect(isAppError(error)).toBe(false);
    });

    it('should return false for null', () => {
      expect(isAppError(null)).toBe(false);
    });

    it('should return false for undefined', () => {
      expect(isAppError(undefined)).toBe(false);
    });

    it('should return false for string', () => {
      expect(isAppError('error string')).toBe(false);
    });

    it('should return false for number', () => {
      expect(isAppError(42)).toBe(false);
    });

    it('should return false for plain object', () => {
      expect(isAppError({ code: 'ERROR' })).toBe(false);
    });
  });
});

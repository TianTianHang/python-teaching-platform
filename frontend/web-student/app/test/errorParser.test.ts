import { describe, it, expect } from 'vitest';
import { parseDRError, parseError } from '../utils/errorParser';
import type { ApiError, NetworkError, TimeoutError } from '../types/errors';

describe('Error Parser', () => {
  describe('parseDRError', () => {
    it('should parse detail error', () => {
      const data = { detail: 'Not found' };
      expect(parseDRError(data)).toBe('Not found');
    });

    it('should parse field errors', () => {
      const data = {
        email: ['Invalid email format'],
        password: ['Too short'],
      };
      const result = parseDRError(data);
      expect(result).toContain('[email]: Invalid email format');
      expect(result).toContain('[password]: Too short');
    });

    it('should parse single field error', () => {
      const data = { email: ['Invalid email format'] };
      expect(parseDRError(data)).toBe('[email]: Invalid email format');
    });

    it('should parse multiple errors for same field', () => {
      const data = { email: ['Invalid email format', 'Required'] };
      const result = parseDRError(data);
      expect(result).toBe('[email]: Invalid email format, Required');
    });

    it('should parse non_field_errors', () => {
      const data = { non_field_errors: ['Invalid credentials'] };
      expect(parseDRError(data)).toBe('[non_field_errors]: Invalid credentials');
    });

    it('should parse string error', () => {
      const data = 'Something went wrong';
      expect(parseDRError(data)).toBe('Something went wrong');
    });

    it('should parse array error', () => {
      const data = ['Error 1', 'Error 2'];
      expect(parseDRError(data)).toBe('[0]: Error 1; [1]: Error 2');
    });

    it('should handle null', () => {
      expect(parseDRError(null)).toBe('请求失败，但未收到错误详情');
    });

    it('should handle undefined', () => {
      expect(parseDRError(undefined)).toBe('请求失败，但未收到错误详情');
    });

    it('should handle empty object', () => {
      expect(parseDRError({})).toBe('解析错误响应失败');
    });

    it('should handle non-string detail', () => {
      const data = { detail: 123 };
      expect(parseDRError(data)).toBe('[detail]: 123');
    });

    it('should handle field with non-array value', () => {
      const data = { email: 'Invalid email' };
      expect(parseDRError(data)).toBe('[email]: Invalid email');
    });

    it('should handle complex nested structure', () => {
      const data = {
        email: ['Invalid email format'],
        password: ['Too short'],
        non_field_errors: ['Credentials invalid'],
      };
      const result = parseDRError(data);
      expect(result).toContain('[email]: Invalid email format');
      expect(result).toContain('[password]: Too short');
      expect(result).toContain('[non_field_errors]: Credentials invalid');
    });
  });

  describe('parseError', () => {
    it('should parse ApiError with detail', () => {
      const error = new Error('API Error') as ApiError;
      error.response = {
        status: 400,
        data: { detail: 'Bad request' },
      };

      const result = parseError(error);
      expect(result.type).toBe('api');
      expect(result.status).toBe(400);
      expect(result.message).toBe('Bad request');
      expect(result.originalError).toBe(error);
    });

    it('should parse ApiError with field errors', () => {
      const error = new Error('Validation failed') as ApiError;
      error.response = {
        status: 400,
        data: { email: ['Invalid email format'] },
      };

      const result = parseError(error);
      expect(result.type).toBe('api');
      expect(result.status).toBe(400);
      expect(result.message).toBe('[email]: Invalid email format');
    });

    it('should parse 401 ApiError', () => {
      const error = new Error('Unauthorized') as ApiError;
      error.response = {
        status: 401,
        data: { detail: 'Authentication credentials were not provided' },
      };

      const result = parseError(error);
      expect(result.type).toBe('api');
      expect(result.status).toBe(401);
      expect(result.message).toBe('Authentication credentials were not provided');
    });

    it('should parse 404 ApiError', () => {
      const error = new Error('Not found') as ApiError;
      error.response = {
        status: 404,
        data: { detail: 'Not found' },
      };

      const result = parseError(error);
      expect(result.type).toBe('api');
      expect(result.status).toBe(404);
    });

    it('should parse 500 ApiError', () => {
      const error = new Error('Server error') as ApiError;
      error.response = {
        status: 500,
        data: { detail: 'Internal server error' },
      };

      const result = parseError(error);
      expect(result.type).toBe('api');
      expect(result.status).toBe(500);
    });

    it('should parse ApiError without response', () => {
      const error = new Error('API Error') as ApiError;
      
      const result = parseError(error);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('API Error');
    });

    it('should parse TimeoutError', () => {
      const error = new Error('Timeout') as TimeoutError;
      error.code = 'ECONNABORTED';

      const result = parseError(error);
      expect(result.type).toBe('timeout');
      expect(result.code).toBe('ECONNABORTED');
      expect(result.message).toBe('请求超时，请稍后重试');
    });

    it('should parse NetworkError', () => {
      const error = new Error('Network Error') as NetworkError;
      error.code = 'NETWORK_ERROR';

      const result = parseError(error);
      expect(result.type).toBe('network');
      expect(result.code).toBe('NETWORK_ERROR');
      expect(result.message).toBe('网络连接失败，请检查网络后重试');
    });

    it('should parse NetworkError with ECONNABORTED code', () => {
      const error = new Error('Connection aborted') as NetworkError;
      error.code = 'ECONNABORTED';

      const result = parseError(error);
      expect(result.type).toBe('timeout');
      expect(result.code).toBe('ECONNABORTED');
    });

    it('should parse plain Error', () => {
      const error = new Error('Something went wrong');

      const result = parseError(error);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('Something went wrong');
    });

    it('should parse Error without message', () => {
      const error = new Error();

      const result = parseError(error);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('未知错误');
    });

    it('should parse null', () => {
      const result = parseError(null);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('发生未知错误');
    });

    it('should parse undefined', () => {
      const result = parseError(undefined);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('发生未知错误');
    });

    it('should parse string', () => {
      const result = parseError('Error string');
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('发生未知错误');
    });

    it('should parse number', () => {
      const result = parseError(42);
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('发生未知错误');
    });

    it('should parse plain object', () => {
      const result = parseError({ code: 'ERROR' });
      expect(result.type).toBe('unknown');
      expect(result.message).toBe('发生未知错误');
    });

    it('should include original error in result', () => {
      const error = new Error('Test error');
      const result = parseError(error);
      expect(result.originalError).toBe(error);
    });

    it('should include details in ApiError result', () => {
      const error = new Error('API Error') as ApiError;
      const data = { detail: 'Bad request' };
      error.response = {
        status: 400,
        data,
      };

      const result = parseError(error);
      expect(result.details).toBe(data);
    });
  });
});

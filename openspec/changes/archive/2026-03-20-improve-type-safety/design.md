# 设计文档：类型安全改进方案

## 1. 设计概述

### 1.1 设计目标
- 消除所有`any`类型滥用
- 建立统一的错误处理体系
- 提供类型安全的开发体验
- 保持向后兼容性

### 1.2 设计原则
- **渐进式改进**：分阶段实施，避免大规模重构
- **类型优先**：优先定义类型，再实现功能
- **测试驱动**：为每个类型提供测试覆盖
- **文档完善**：提供清晰的类型使用指南

## 2. 核心类型设计

### 2.1 错误类型层次结构

```typescript
// types/errors.ts

/**
 * 基础错误接口
 */
export interface BaseError extends Error {
  code?: string;
  timestamp?: number;
}

/**
 * API错误响应数据
 */
export interface ApiErrorData {
  detail?: string;
  [key: string]: unknown;
}

/**
 * API错误响应
 */
export interface ApiErrorResponse {
  status: number;
  statusText?: string;
  data?: ApiErrorData;
  headers?: Record<string, string>;
}

/**
 * API错误类型
 */
export interface ApiError extends BaseError {
  response?: ApiErrorResponse;
  config?: unknown;
  request?: unknown;
}

/**
 * 网络错误类型
 */
export interface NetworkError extends BaseError {
  code: 'NETWORK_ERROR' | 'ECONNABORTED' | 'ETIMEDOUT';
  request?: unknown;
}

/**
 * 超时错误类型
 */
export interface TimeoutError extends BaseError {
  code: 'ECONNABORTED';
  timeout?: number;
}

/**
 * 验证错误类型
 */
export interface ValidationError extends BaseError {
  fields?: Record<string, string[]>;
}

/**
 * 业务逻辑错误类型
 */
export interface BusinessError extends BaseError {
  businessCode?: string;
  businessMessage?: string;
}

/**
 * 联合错误类型
 */
export type AppError = 
  | ApiError 
  | NetworkError 
  | TimeoutError 
  | ValidationError 
  | BusinessError;

/**
 * 错误处理结果
 */
export interface ErrorResult {
  type: 'api' | 'network' | 'timeout' | 'validation' | 'business' | 'unknown';
  status?: number;
  code?: string;
  message: string;
  details?: unknown;
  originalError?: unknown;
}
```

### 2.2 类型守卫函数

```typescript
// utils/typeGuards.ts

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
```

### 2.3 错误解析函数

```typescript
// utils/errorParser.ts

import type { ApiErrorData, ErrorResult } from '~/types/errors';
import { isApiError, isNetworkError, isTimeoutError } from './typeGuards';

/**
 * 解析DRF错误响应
 * DRF 400错误通常返回: { "field_name": ["error message"] }
 * DRF 401/403/404错误通常返回: { "detail": "error message" }
 */
export function parseDRError(data: unknown): string {
  if (!data) {
    return '请求失败，但未收到错误详情';
  }

  // 1. { "detail": "..." }
  if (typeof data === 'object' && data !== null && 'detail' in data) {
    const detail = (data as ApiErrorData).detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  // 2. { "field_name": ["..."] } 或 { "non_field_errors": ["..."] }
  if (typeof data === 'object' && data !== null) {
    const errorMessages: string[] = [];
    for (const key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        const value = (data as Record<string, unknown>)[key];
        const errorList = Array.isArray(value) ? value : [value];
        errorMessages.push(`[${key}]: ${errorList.join(', ')}`);
      }
    }
    if (errorMessages.length > 0) {
      return errorMessages.join('; ');
    }
  }

  // 3. 兜底，如果是字符串或数组
  if (typeof data === 'string') {
    return data;
  }
  if (Array.isArray(data)) {
    return data.join('; ');
  }

  return '解析错误响应失败';
}

/**
 * 解析错误为统一结果
 */
export function parseError(error: unknown): ErrorResult {
  if (isApiError(error)) {
    const status = error.response?.status || 500;
    const message = parseDRError(error.response?.data);
    
    return {
      type: 'api',
      status,
      message,
      details: error.response?.data,
      originalError: error
    };
  }

  if (isTimeoutError(error)) {
    return {
      type: 'timeout',
      code: error.code,
      message: '请求超时，请稍后重试',
      originalError: error
    };
  }

  if (isNetworkError(error)) {
    return {
      type: 'network',
      code: error.code,
      message: '网络连接失败，请检查网络后重试',
      originalError: error
    };
  }

  if (error instanceof Error) {
    return {
      type: 'unknown',
      message: error.message || '未知错误',
      originalError: error
    };
  }

  return {
    type: 'unknown',
    message: '发生未知错误',
    originalError: error
  };
}
```

## 3. 统一错误处理设计

### 3.1 错误处理器

```typescript
// utils/errorHandler.ts

import { redirect } from 'react-router';
import type { ErrorResult } from '~/types/errors';
import { parseError } from './errorParser';

/**
 * 错误处理选项
 */
export interface ErrorHandlerOptions {
  /** 是否重定向到登录页 */
  redirectToLogin?: boolean;
  /** 是否显示错误通知 */
  showNotification?: boolean;
  /** 自定义错误消息 */
  customMessage?: string;
  /** 错误回调函数 */
  onError?: (result: ErrorResult) => void;
}

/**
 * 处理API错误
 */
export function handleApiError(
  error: unknown,
  options: ErrorHandlerOptions = {}
): never {
  const result = parseError(error);
  
  // 调用错误回调
  if (options.onError) {
    options.onError(result);
  }

  // 401错误重定向到登录页
  if (options.redirectToLogin !== false && result.status === 401) {
    throw redirect('/auth/login');
  }

  // 抛出响应错误
  throw new Response(
    JSON.stringify({ 
      message: options.customMessage || result.message,
      code: result.code,
      details: result.details
    }),
    {
      status: result.status || 500,
      statusText: result.message
    }
  );
}

/**
 * 创建错误处理包装器
 */
export function withErrorHandling<T extends (...args: any[]) => any>(
  handler: T,
  options: ErrorHandlerOptions = {}
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await handler(...args);
    } catch (error) {
      handleApiError(error, options);
    }
  }) as T;
}

/**
 * 创建带认证的加载器包装器
 */
export function withAuthLoader<T extends (...args: any[]) => any>(
  loader: T
): T {
  return withErrorHandling(loader, { redirectToLogin: true });
}
```

### 3.2 路由错误处理集成

```typescript
// 在路由文件中使用

import { withAuthLoader } from '~/utils/errorHandler';
import type { Route } from "./+types/route";

// 原始方式（有any类型）
export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  try {
    const data = await clientHttp.get(`/api/data/${params.id}`);
    return { data };
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw redirect('/auth/login');
    }
    throw new Response(JSON.stringify({ message: error.message }), {
      status: error.response?.status || 500,
      statusText: error.message
    });
  }
}

// 改进方式（类型安全）
export const clientLoader = withAuthLoader(
  async ({ params }: Route.ClientLoaderArgs) => {
    const data = await clientHttp.get(`/api/data/${params.id}`);
    return { data };
  }
);
```

## 4. 类型定义改进

### 4.1 HTTP客户端类型

```typescript
// utils/http/types.ts

import type { AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

/**
 * 自定义请求配置
 */
export interface CustomRequestConfig {
  /** 跳过错误处理 */
  skipErrorHandler?: boolean;
  /** 请求重试次数 */
  retryCount?: number;
  /** 请求超时时间 */
  timeout?: number;
  /** 自定义请求头 */
  headers?: Record<string, string>;
}

/**
 * 内部请求配置
 */
export interface CustomInternalRequestConfig extends InternalAxiosRequestConfig {
  customConfig?: CustomRequestConfig;
  metadata?: {
    startTime: number;
    endTime?: number;
  };
}

/**
 * 拦截器钩子接口
 */
export interface InterceptorHooks {
  requestInterceptor?: (
    config: CustomInternalRequestConfig
  ) => CustomInternalRequestConfig | Promise<CustomInternalRequestConfig>;
  
  requestInterceptorCatch?: (error: AxiosError) => Promise<never>;
  
  responseInterceptor?: (
    response: AxiosResponse
  ) => AxiosResponse | Promise<AxiosResponse>;
  
  responseInterceptorCatch?: (error: AxiosError) => Promise<never>;
}

/**
 * 响应拦截器错误处理类型
 */
export type ResponseInterceptorErrorHandler = (error: AxiosError) => Promise<never>;

/**
 * 请求拦截器错误处理类型
 */
export type RequestInterceptorErrorHandler = (error: AxiosError) => Promise<never>;
```

### 4.2 用户类型改进

```typescript
// types/user.ts

/**
 * 用户订阅信息
 */
export interface Subscription {
  id: number;
  plan: string;
  startDate: string;
  endDate: string;
  isActive: boolean;
  features: string[];
}

/**
 * 用户信息
 */
export interface User {
  id: number;
  avatar: string;
  username: string;
  stNumber: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  isStaff: boolean;
  isSuperuser: boolean;
  dateJoined: string;
  lastLogin?: string;
  current_subscription: Subscription;
  has_active_subscription: boolean;
  // 添加具体类型，避免any
  preferences?: UserPreferences;
  profile?: UserProfile;
}

/**
 * 用户偏好设置
 */
export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: NotificationSettings;
}

/**
 * 通知设置
 */
export interface NotificationSettings {
  email: boolean;
  push: boolean;
  sms: boolean;
}

/**
 * 用户资料
 */
export interface UserProfile {
  bio?: string;
  website?: string;
  location?: string;
  socialLinks?: SocialLinks;
}

/**
 * 社交链接
 */
export interface SocialLinks {
  github?: string;
  twitter?: string;
  linkedin?: string;
}
```

## 5. 测试策略

### 5.1 类型守卫测试

```typescript
// test/typeGuards.test.ts

import { 
  isApiError, 
  isNetworkError, 
  isTimeoutError,
  isValidationError,
  isBusinessError
} from '~/utils/typeGuards';

describe('Type Guards', () => {
  describe('isApiError', () => {
    it('should identify API errors correctly', () => {
      const apiError = new Error('API Error') as any;
      apiError.response = { status: 400, data: { detail: 'Bad Request' } };
      
      expect(isApiError(apiError)).toBe(true);
    });

    it('should reject non-API errors', () => {
      const normalError = new Error('Normal Error');
      expect(isApiError(normalError)).toBe(false);
    });
  });

  describe('isNetworkError', () => {
    it('should identify network errors correctly', () => {
      const networkError = new Error('Network Error') as any;
      networkError.code = 'NETWORK_ERROR';
      
      expect(isNetworkError(networkError)).toBe(true);
    });

    it('should identify timeout errors', () => {
      const timeoutError = new Error('timeout of 5000ms exceeded') as any;
      timeoutError.code = 'ECONNABORTED';
      
      expect(isTimeoutError(timeoutError)).toBe(true);
    });
  });
});
```

### 5.2 错误解析测试

```typescript
// test/errorParser.test.ts

import { parseDRError, parseError } from '~/utils/errorParser';

describe('Error Parser', () => {
  describe('parseDRError', () => {
    it('should parse detail error', () => {
      const data = { detail: 'Unauthorized' };
      expect(parseDRError(data)).toBe('Unauthorized');
    });

    it('should parse field errors', () => {
      const data = { 
        username: ['This field is required'],
        email: ['Enter a valid email address']
      };
      const result = parseDRError(data);
      expect(result).toContain('[username]: This field is required');
      expect(result).toContain('[email]: Enter a valid email address');
    });
  });

  describe('parseError', () => {
    it('should parse API error correctly', () => {
      const apiError = new Error('API Error') as any;
      apiError.response = { 
        status: 400, 
        data: { detail: 'Validation failed' }
      };
      
      const result = parseError(apiError);
      expect(result.type).toBe('api');
      expect(result.status).toBe(400);
      expect(result.message).toBe('Validation failed');
    });
  });
});
```

## 6. 迁移策略

### 6.1 渐进式迁移步骤

1. **第一阶段：基础类型定义**
   - 创建错误类型定义
   - 实现类型守卫函数
   - 添加基础测试

2. **第二阶段：核心功能替换**
   - 替换关键错误处理逻辑
   - 更新HTTP客户端类型
   - 优化用户类型定义

3. **第三阶段：全面推广**
   - 更新所有路由错误处理
   - 完善工具函数类型
   - 添加集成测试

4. **第四阶段：优化完善**
   - 性能优化
   - 文档完善
   - 代码审查

### 6.2 向后兼容性保证

1. **保留原有接口**：在迁移期间保留原有函数签名
2. **渐进式替换**：逐步替换，避免大规模破坏
3. **兼容性测试**：确保新旧接口行为一致
4. **回滚机制**：准备回滚方案，应对意外问题

## 7. 性能考虑

### 7.1 类型检查性能

1. **运行时类型守卫**：使用简单的属性检查，避免复杂递归
2. **类型收窄**：利用TypeScript类型收窄减少运行时检查
3. **缓存结果**：对重复的类型检查结果进行缓存

### 7.2 内存使用

1. **类型定义**：接口和类型在编译时消除，不影响运行时内存
2. **错误对象**：确保错误对象正确清理，避免内存泄漏
3. **测试覆盖**：监控内存使用，确保没有回归

## 8. 部署策略

### 8.1 灰度发布

1. **功能开关**：使用功能开关控制新错误处理逻辑
2. **A/B测试**：对比新旧错误处理的性能和稳定性
3. **监控告警**：实时监控错误率和性能指标

### 8.2 回滚计划

1. **快速回滚**：准备一键回滚脚本
2. **数据备份**：备份关键配置和错误日志
3. **应急响应**：建立应急响应流程

## 9. 监控指标

### 9.1 代码质量指标

1. **类型覆盖率**：目标95%以上
2. **`any`类型数量**：目标5处以下
3. **类型错误数量**：目标减少90%

### 9.2 运行时指标

1. **错误率**：监控生产环境错误率变化
2. **性能影响**：监控类型检查的性能开销
3. **内存使用**：监控内存使用变化

## 10. 文档要求

### 10.1 开发文档

1. **类型使用指南**：如何使用新的类型定义
2. **错误处理最佳实践**：统一的错误处理模式
3. **迁移指南**：从旧模式迁移到新模式的步骤

### 10.2 API文档

1. **类型定义文档**：详细的类型接口说明
2. **错误码文档**：统一的错误码定义
3. **示例代码**：常见使用场景的示例代码

---

**设计文档版本**：1.0  
**创建时间**：2026年3月19日  
**最后更新**：2026年3月19日  
**设计负责人**：待定  
**评审状态**：待评审
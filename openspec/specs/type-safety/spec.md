# 类型安全规范

## 1. 概述

本规范定义了前端代码库的类型安全标准和要求，旨在消除`any`类型滥用，建立统一的类型系统，提高代码质量和开发体验。

## 2. 范围

本规范适用于所有前端TypeScript代码，包括：
- React组件
- 工具函数
- HTTP客户端
- 状态管理
- 类型定义
- 测试代码

## 3. 核心要求

### 3.1 禁止使用`any`类型

**要求**：除以下特殊情况外，禁止使用`any`类型。

**允许的特殊情况**：
1. 第三方库类型定义中的`any`（暂时无法避免）
2. 与JavaScript代码交互时的临时类型断言
3. 测试代码中的模拟数据

**替代方案**：
- 使用`unknown`类型代替`any`
- 使用具体类型定义
- 使用泛型约束
- 使用类型守卫函数

### 3.2 错误处理类型安全

**要求**：所有错误处理必须类型安全。

**具体要求**：
1. 使用`catch (error: unknown)`代替`catch (error: any)`
2. 使用类型守卫函数检查错误类型
3. 为错误响应创建具体类型定义
4. 统一错误处理逻辑

**示例**：
```typescript
// 错误示例
try {
  await fetchData();
} catch (error: any) {
  if (error.response?.status === 401) {
    redirect('/login');
  }
}

// 正确示例
try {
  await fetchData();
} catch (error: unknown) {
  if (isApiError(error) && error.response?.status === 401) {
    redirect('/login');
  }
}
```

### 3.3 函数参数类型化

**要求**：所有函数参数必须有明确的类型定义。

**具体要求**：
1. 禁止使用`(...args: any[])`函数签名
2. 为回调函数参数创建具体类型
3. 使用泛型约束函数参数
4. 为事件处理器创建具体类型

**示例**：
```typescript
// 错误示例
function processData(data: any): any {
  return data;
}

// 正确示例
interface Data {
  id: number;
  name: string;
}

function processData(data: Data): ProcessedData {
  return { ...data, processed: true };
}
```

### 3.4 组件属性类型化

**要求**：所有React组件必须有明确的属性类型定义。

**具体要求**：
1. 使用TypeScript接口定义组件属性
2. 为事件处理器创建具体类型
3. 为上下文值创建具体类型
4. 避免使用`any`作为属性类型

**示例**：
```typescript
// 错误示例
const MyComponent = (props: any) => {
  return <div>{props.data}</div>;
};

// 正确示例
interface MyComponentProps {
  data: string;
  onClick: (event: React.MouseEvent) => void;
}

const MyComponent: React.FC<MyComponentProps> = ({ data, onClick }) => {
  return <div onClick={onClick}>{data}</div>;
};
```

### 3.5 类型守卫函数

**要求**：为复杂类型创建类型守卫函数。

**具体要求**：
1. 为联合类型创建类型守卫
2. 为错误类型创建类型守卫
3. 为第三方库类型创建类型守卫
4. 类型守卫函数必须返回类型谓语

**示例**：
```typescript
// 类型定义
interface ApiError extends Error {
  response?: {
    status: number;
    data: unknown;
  };
}

interface NetworkError extends Error {
  code: 'NETWORK_ERROR' | 'ECONNABORTED';
}

type AppError = ApiError | NetworkError;

// 类型守卫
function isApiError(error: unknown): error is ApiError {
  return error instanceof Error && 'response' in error;
}

function isNetworkError(error: unknown): error is NetworkError {
  return error instanceof Error && 
    (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED');
}

// 使用示例
function handleError(error: unknown): void {
  if (isApiError(error)) {
    console.error('API Error:', error.response?.status);
  } else if (isNetworkError(error)) {
    console.error('Network Error:', error.code);
  }
}
```

## 4. 类型定义要求

### 4.1 接口定义

**要求**：所有接口必须明确定义属性和方法。

**具体要求**：
1. 为所有属性创建具体类型
2. 使用可选属性标记可能为undefined的值
3. 使用只读属性标记不可变数据
4. 为复杂属性创建嵌套接口

**示例**：
```typescript
// 错误示例
interface User {
  id: any;
  name: any;
  data: any;
}

// 正确示例
interface User {
  readonly id: number;
  name: string;
  email: string;
  profile?: UserProfile;
  preferences: UserPreferences;
}

interface UserProfile {
  bio?: string;
  avatar?: string;
  website?: string;
}

interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: NotificationSettings;
}
```

### 4.2 类型导出

**要求**：所有类型必须正确导出和导入。

**具体要求**：
1. 在类型文件中导出所有类型
2. 使用命名导出代替默认导出
3. 创建类型索引文件便于导入
4. 避免循环类型依赖

**示例**：
```typescript
// types/index.ts
export * from './errors';
export * from './user';
export * from './api';

// types/errors.ts
export interface ApiError extends Error {
  response?: {
    status: number;
    data: unknown;
  };
}

// 使用示例
import { ApiError, User } from '~/types';
```

## 5. 测试要求

### 5.1 类型测试

**要求**：为所有类型定义创建测试。

**具体要求**：
1. 测试类型守卫函数
2. 测试类型转换函数
3. 测试复杂类型定义
4. 测试类型兼容性

**示例**：
```typescript
// test/types.test.ts
import { isApiError, isNetworkError } from '~/utils/typeGuards';

describe('Type Guards', () => {
  it('should identify API errors correctly', () => {
    const apiError = new Error('API Error') as ApiError;
    apiError.response = { status: 400, data: {} };
    
    expect(isApiError(apiError)).toBe(true);
    expect(isNetworkError(apiError)).toBe(false);
  });
});
```

### 5.2 集成测试

**要求**：为类型安全的功能创建集成测试。

**具体要求**：
1. 测试错误处理流程
2. 测试类型转换流程
3. 测试类型验证流程
4. 测试类型兼容性

## 6. 代码审查要求

### 6.1 审查清单

**类型安全审查清单**：
- [ ] 没有使用`any`类型（除特殊情况外）
- [ ] 所有错误处理都是类型安全的
- [ ] 所有函数参数都有明确的类型定义
- [ ] 所有组件属性都有明确的类型定义
- [ ] 所有复杂类型都有类型守卫函数
- [ ] 所有类型定义都有相应的测试

### 6.2 审查流程

**审查步骤**：
1. 检查类型定义完整性
2. 检查类型守卫函数正确性
3. 检查错误处理类型安全性
4. 检查测试覆盖率
5. 检查文档完整性

## 7. 工具配置

### 7.1 TypeScript配置

**要求**：启用严格类型检查。

**tsconfig.json配置**：
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

### 7.2 ESLint配置

**要求**：启用类型相关ESLint规则。

**ESLint配置**：
```json
{
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unsafe-assignment": "error",
    "@typescript-eslint/no-unsafe-call": "error",
    "@typescript-eslint/no-unsafe-member-access": "error",
    "@typescript-eslint/no-unsafe-return": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/explicit-module-boundary-types": "warn"
  }
}
```

## 8. 性能考虑

### 8.1 类型检查性能

**要求**：类型检查不应显著影响运行时性能。

**具体要求**：
1. 类型守卫函数使用简单的属性检查
2. 避免复杂的递归类型检查
3. 使用缓存优化重复的类型检查
4. 监控类型检查的性能影响

### 8.2 编译性能

**要求**：类型定义不应显著增加编译时间。

**具体要求**：
1. 避免过于复杂的类型定义
2. 使用类型导入减少编译依赖
3. 优化类型定义的编译顺序
4. 监控编译时间变化

## 9. 文档要求

### 9.1 类型文档

**要求**：为所有类型创建文档。

**具体要求**：
1. 为接口添加JSDoc注释
2. 为类型守卫函数添加使用说明
3. 为错误类型添加错误码说明
4. 为复杂类型添加使用示例

### 9.2 使用指南

**要求**：创建类型使用指南。

**具体要求**：
1. 如何使用类型守卫函数
2. 如何处理类型错误
3. 如何创建新的类型定义
4. 如何迁移旧代码到新类型系统

## 10. 迁移策略

### 10.1 渐进式迁移

**要求**：采用渐进式方式迁移到新类型系统。

**具体步骤**：
1. 第一阶段：创建基础类型定义
2. 第二阶段：替换关键`any`类型
3. 第三阶段：统一错误处理
4. 第四阶段：全面推广

### 10.2 向后兼容性

**要求**：确保迁移过程中的向后兼容性。

**具体要求**：
1. 保留原有接口，添加新接口
2. 使用类型断言处理兼容性
3. 提供迁移工具和脚本
4. 创建迁移文档和示例

## 11. 监控指标

### 11.1 代码质量指标

**监控指标**：
1. `any`类型数量
2. 类型覆盖率
3. 类型错误数量
4. 类型检查时间

### 11.2 运行时指标

**监控指标**：
1. 类型检查性能影响
2. 运行时错误率
3. 内存使用变化
4. 用户满意度

## 12. 附录

### 12.1 类型定义模板

```typescript
// 错误类型模板
export interface ApiError extends Error {
  response?: {
    status: number;
    data: unknown;
    headers?: Record<string, string>;
  };
  code?: string;
  config?: unknown;
}

// 类型守卫模板
export function isApiError(error: unknown): error is ApiError {
  return error instanceof Error && 'response' in error;
}

// 错误处理模板
export function handleApiError(error: unknown): ErrorResult {
  if (isApiError(error)) {
    return {
      type: 'api',
      status: error.response?.status || 500,
      message: parseErrorData(error.response?.data)
    };
  }
  return {
    type: 'unknown',
    message: '发生未知错误'
  };
}
```

### 12.2 常见错误模式

**常见错误模式及解决方案**：
1. `catch (error: any)` → `catch (error: unknown)` + 类型守卫
2. `function handler(data: any)` → 具体类型定义
3. `interface Props { data: any }` → 具体类型定义
4. `type Response = any` → 具体类型定义

---

**规范版本**：1.0  
**创建时间**：2026年3月19日  
**最后更新**：2026年3月19日  
**适用范围**：前端TypeScript代码  
**维护团队**：前端架构组
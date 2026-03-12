# 前端测试指南

本指南说明了如何为 Submission 相关组件编写测试用例。

## 安装测试依赖

```bash
# 安装测试框架
npm install --save-dev jest @testing-library/react @testing-library/jest-dom
npm install --save-dev ts-jest @types/jest

# 或者使用 pnpm
pnpm add -D jest @testing-library/react @testing-library/jest-dom ts-jest @types/jest
```

## 配置 Jest

创建 `jest.config.mts` 文件：

```typescript
import type { Config } from 'jest';
import nextJest from 'next/jest.js';

const createJestConfig = nextJest({
  dir: './',
});

const config: Config = {
  coverageProvider: 'v8',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/app/$1',
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx'],
  transform: {
    '^.+\\.(ts|tsx)$': ['ts-jest', { tsconfig: './tsconfig.json' }],
  },
  testMatch: ['**/__tests__/**/*.{js,jsx,ts,tsx}', '**/*.{test,spec}.{js,jsx,ts,tsx}'],
};

export default createJestConfig(config);
```

创建 `jest.setup.ts` 文件：

```typescript
import '@testing-library/jest-dom';
```

## 测试文件结构

```
app/
├── test/
│   ├── mocks/
│   │   └── submission.ts  # 模拟数据
│   └── components/
│       └── Submission.test.ts  # 组件测试
├── hooks/
│   └── useSubmissionPolling.test.ts  # Hook 测试
└── utils/
    └── http/
        └── submission.test.ts  # API 测试
```

## 测试示例

### 1. Hook 测试 (useSubmissionPolling)

参考 `app/hooks/useSubmissionPolling.test.ts` 文件。

```typescript
import { renderHook, act } from '@testing-library/react';
import { useSubmissionPolling } from './useSubmissionPolling';

describe('useSubmissionPolling Hook', () => {
  it('should handle successful polling', async () => {
    const { result } = renderHook(() =>
      useSubmissionPolling({ submissionId: 1 })
    );

    // 模拟 API 调用
    act(() => {
      jest.advanceTimersByTime(5000);
    });

    expect(result.current.isPolling).toBe(false);
    expect(result.current.success).toBe(true);
  });
});
```

### 2. 组件测试 (QueueStatusCard)

```typescript
import { render } from '@testing-library/react';
import { QueueStatusCard } from '~/components/Submission/QueueStatusCard';
import { testQueueStats } from '~/test/mocks/submission';

describe('QueueStatusCard Component', () => {
  it('should display pending status', () => {
    const { getByText } = render(
      <QueueStatusCard queueStats={testQueueStats.pending} />
    );

    expect(getByText('评测状态: 等待中')).toBeInTheDocument();
    expect(getByText('队列位置: 第 10 位')).toBeInTheDocument();
  });
});
```

### 3. API 函数测试

```typescript
import { submitAndWait } from '~/utils/http/submission';
import { clientHttp } from '~/utils/http/client';

jest.mock('~/utils/http/client', () => ({
  clientHttp: {
    post: jest.fn(),
  },
}));

describe('Submission API', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should handle synchronous submission', async () => {
    const mockData = {
      code: 'print("hello")',
      language: 'python',
    };

    clientHttp.post.mockResolvedValue({
      success: true,
      submission: {
        id: 1,
        status: 'accepted',
        execution_time: 100,
      },
    });

    const result = await submitAndWait(mockData);

    expect(result.success).toBe(true);
    expect(result.submission?.status).toBe('accepted');
  });
});
```

## 测试最佳实践

### 1. 测试覆盖要点

- **Hook 测试**: 测试状态变化、错误处理、取消操作
- **组件测试**: 测试渲染输出、用户交互、样式
- **API 测试**: 测试网络请求、响应处理、错误处理

### 2. Mock 策略

- 使用 `jest.fn()` 创建模拟函数
- 使用 `jest.mock()` 模拟模块导入
- 使用 `jest.useFakeTimers()` 处理异步操作

### 3. 测试数据

使用 `app/test/mocks/submission.ts` 中的模拟数据：

```typescript
import { testSubmissions, testQueueStats } from '~/test/mocks/submission';

// 使用预定义的测试数据
const submission = testSubmissions.accepted;
const queueStats = testQueueStats.success;
```

### 4. 运行测试

```bash
# 运行所有测试
npm test

# 运行特定测试文件
npm test -- useSubmissionPolling.test.ts

# 运行测试并生成覆盖率报告
npm run test:coverage
```

## 断言库推荐

使用 `@testing-library/jest-dom` 提供的断言：

```typescript
// 元素存在
expect(getByText('提交成功')).toBeInTheDocument();

// 元素包含属性
expect(button).toHaveAttribute('disabled');

// 样式检查
expect(element).toHaveClass('loading');
```

## 异步测试

使用 `async/await` 和 `act()` 处理异步操作：

```typescript
it('should handle async operation', async () => {
  const { result } = renderHook(() => useAsyncOperation());

  // 触发异步操作
  act(() => {
    result.current.execute();
  });

  // 快进时间
  act(() => {
    jest.advanceTimersByTime(1000);
  });

  await waitFor(() => {
    expect(result.current.data).toBeDefined();
  });
});
```

## 性能测试

```typescript
import { performance } from 'perf_hooks';

it('should render within 16ms', () => {
  const start = performance.now();
  render(<Component />);
  const end = performance.now();

  expect(end - start).toBeLessThan(16);
});
```

## 集成测试

测试完整的用户流程：

```typescript
it('should handle complete submission flow', async () => {
  // 设置模拟数据
  clientHttp.post.mockResolvedValue({
    success: true,
    submission: { task_id: '123', status: 'pending' },
  });

  // 渲染组件
  render(<SubmissionComponent />);

  // 用户操作
  fireEvent.click(screen.getByRole('button', { name: '提交' }));

  // 验证结果
  await waitFor(() => {
    expect(screen.getByText('评测完成')).toBeInTheDocument();
  });
});
```

通过遵循这些最佳实践，可以确保 Submission 相关组件的稳定性和可靠性。
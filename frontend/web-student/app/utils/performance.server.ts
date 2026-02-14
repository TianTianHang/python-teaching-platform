/**
 * 性能计时工具模块
 * 用于测量 API 请求的各个阶段耗时
 */

/**
 * 性能指标数据结构
 */
export interface PerformanceMetrics {
  endpoint: string;
  // 时间点（毫秒，使用 performance.now()）
  startTime: number;        // 请求开始时间
  httpRequestStart: number; // HTTP 请求发出时间
  httpResponseEnd: number;   // HTTP 响应接收时间
  serverEnd: number;         // 服务器处理完成时间
  // 计算得出的时间段（毫秒）
  totalTime: number;        // 总时间 (serverEnd - startTime)
  backendRequest: number;   // 后端请求时间 (httpResponseEnd - httpRequestStart)
  frontendProcessing: number; // 前端服务器处理时间 (totalTime - backendRequest)
  success: boolean;         // 请求是否成功
  error?: string;           // 错误信息（如果失败）
}

/**
 * 性能计时器类
 * 用于记录各个时间点
 */
export class PerformanceTimer {
  private metrics: Omit<PerformanceMetrics, 'endpoint' | 'totalTime' | 'backendRequest' | 'frontendProcessing' | 'success' | 'error'>;
  private success: boolean = true;
  private error?: string;

  constructor() {
    const now = this.now();
    this.metrics = {
      startTime: now,
      httpRequestStart: 0,
      httpResponseEnd: 0,
      serverEnd: 0,
    };
  }

  /**
   * 获取当前高精度时间戳（毫秒）
   */
  private now(): number {
    // 在 Node.js 环境中使用 performance.now()
    if (typeof performance !== 'undefined') {
      return performance.now();
    }
    // 降级方案：使用 Date.now()
    return Date.now();
  }

  /**
   * 记录 HTTP 请求发出时间
   */
  markHttpRequestStart(timestamp: number): void {
    this.metrics.httpRequestStart = timestamp;
  }

  /**
   * 记录 HTTP 响应接收时间
   */
  markHttpResponseEnd(timestamp: number): void {
    this.metrics.httpResponseEnd = timestamp;
  }

  /**
   * 记录服务器处理完成时间
   */
  markServerEnd(): void {
    this.metrics.serverEnd = this.now();
  }

  /**
   * 标记请求失败
   */
  markFailure(error: string): void {
    this.success = false;
    this.error = error;
    this.markServerEnd();
  }

  /**
   * 生成完整的性能指标
   */
  getMetrics(endpoint: string): PerformanceMetrics {
    const { startTime, httpRequestStart, httpResponseEnd, serverEnd } = this.metrics;

    const totalTime = serverEnd - startTime;
    const backendRequest = httpResponseEnd - httpRequestStart;
    const frontendProcessing = totalTime - backendRequest;

    return {
      endpoint,
      startTime,
      httpRequestStart,
      httpResponseEnd,
      serverEnd,
      totalTime,
      backendRequest,
      frontendProcessing,
      success: this.success,
      error: this.error,
    };
  }
}

/**
 * 计时钩子接口
 */
export interface TimingHooks {
  onRequestStart: (timestamp: number) => void;
  onResponseEnd: (timestamp: number) => void;
}

/**
 * 创建计时钩子
 */
export function createTimingHooks(timer: PerformanceTimer): TimingHooks {
  return {
    onRequestStart: (timestamp: number) => timer.markHttpRequestStart(timestamp),
    onResponseEnd: (timestamp: number) => timer.markHttpResponseEnd(timestamp),
  };
}

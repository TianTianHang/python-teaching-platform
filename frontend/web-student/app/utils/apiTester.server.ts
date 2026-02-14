/**
 * API 测试函数模块
 * 用于测试各个端点的性能并返回计时数据
 */

import type { Page } from '~/types/page';
import type { Problem } from '~/types/course';
import type { Course } from '~/types/course';
import type { Chapter } from '~/types/course';
import { createTimedHttp } from './http/index.server';
import type { PerformanceMetrics } from './performance.server';
import { PerformanceTimer, createTimingHooks } from './performance.server';

// 登录响应类型
interface LoginResponse {
  access: string;
  refresh: string;
}

/**
 * 测试登录接口
 * POST /auth/login
 */
export async function testLogin(request: Request, username: string, password: string): Promise<PerformanceMetrics> {
  const timer = new PerformanceTimer();
  const timingHooks = createTimingHooks(timer);
  const http = createTimedHttp(request, timingHooks);

  try {
    await http.post<LoginResponse>('auth/login', { username, password });
    timer.markServerEnd();
    return timer.getMetrics('POST /auth/login');
  } catch (error) {
    timer.markFailure(error instanceof Error ? error.message : String(error));
    return timer.getMetrics('POST /auth/login');
  }
}

/**
 * 测试题目列表接口
 * GET /problems/
 */
export async function testProblems(request: Request): Promise<PerformanceMetrics> {
  const timer = new PerformanceTimer();
  const timingHooks = createTimingHooks(timer);
  const http = createTimedHttp(request, timingHooks);

  try {
    const queryParams = new URLSearchParams();
    queryParams.set('page', '1');
    queryParams.set('page_size', '10');
    await http.get<Page<Problem>>(`/problems/?${queryParams.toString()}`);
    timer.markServerEnd();
    return timer.getMetrics('GET /problems/');
  } catch (error) {
    timer.markFailure(error instanceof Error ? error.message : String(error));
    return timer.getMetrics('GET /problems/');
  }
}

/**
 * 测试章节列表接口
 * GET /courses/{courseId}/chapters
 */
export async function testChapters(request: Request, courseId: string): Promise<PerformanceMetrics> {
  const timer = new PerformanceTimer();
  const timingHooks = createTimingHooks(timer);
  const http = createTimedHttp(request, timingHooks);

  try {
    await http.get<Page<Chapter>>(`/courses/${courseId}/chapters`);
    timer.markServerEnd();
    return timer.getMetrics(`GET /courses/${courseId}/chapters`);
  } catch (error) {
    timer.markFailure(error instanceof Error ? error.message : String(error));
    return timer.getMetrics(`GET /courses/${courseId}/chapters`);
  }
}

/**
 * 测试课程列表接口
 * GET /courses/
 */
export async function testCourses(request: Request): Promise<PerformanceMetrics> {
  const timer = new PerformanceTimer();
  const timingHooks = createTimingHooks(timer);
  const http = createTimedHttp(request, timingHooks);

  try {
    const queryParams = new URLSearchParams();
    queryParams.set('page', '1');
    queryParams.set('page_size', '10');
    await http.get<Page<Course>>(`/courses/?${queryParams.toString()}`);
    timer.markServerEnd();
    return timer.getMetrics('GET /courses/');
  } catch (error) {
    timer.markFailure(error instanceof Error ? error.message : String(error));
    return timer.getMetrics('GET /courses/');
  }
}

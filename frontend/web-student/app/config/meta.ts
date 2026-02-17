/**
 * Meta Tag Configuration - 元标签配置
 *
 * 共享的元标签配置和工具函数，用于在 React 19 中设置页面标题和元标签。
 * 替代了 React Router 的 `meta()` 导出模式，使用原生的 `<title>` 和 `<meta>` 元素。
 *
 * @see https://react.dev/reference/react-dom/title
 * @see https://react.dev/reference/react-dom/meta
 */

/**
 * 默认元标签配置
 */
export const DEFAULT_META = {
  /** 站点名称 */
  siteName: 'Python教学平台',
  /** 站点默认描述 */
  description: '在线Python编程学习平台，提供互动式课程和练习',
  /** Open Graph 类型 */
  ogType: 'website',
} as const;

/**
 * 页面类型枚举
 */
export type PageType = 'website' | 'profile' | 'article' | 'course' | 'problem';

/**
 * 元标签数据接口
 */
export interface MetaData {
  /** 页面标题（不含站点名称） */
  title: string;
  /** 页面描述 */
  description?: string;
  /** Open Graph 类型 */
  ogType?: PageType;
}

/**
 * 格式化页面标题
 *
 * @param title - 页面标题（不含站点名称）
 * @param siteName - 站点名称（默认使用 DEFAULT_META.siteName）
 * @returns 完整的页面标题
 *
 * @example
 * ```ts
 * formatTitle('首页') // '首页 - Python教学平台'
 * formatTitle('Python基础', '我的课程') // 'Python基础 - 我的课程'
 * ```
 */
export function formatTitle(title: string, siteName: string = DEFAULT_META.siteName): string {
  // 如果标题已包含站点名称，直接返回
  if (title.includes(siteName)) {
    return title;
  }
  return `${title} - ${siteName}`;
}

/**
 * 截断描述文本以适应 SEO 要求
 *
 * @param description - 原始描述文本
 * @param maxLength - 最大长度（默认 160 字符，符合 SEO 最佳实践）
 * @returns 截断后的描述
 *
 * @example
 * ```ts
 * truncateDescription('这是一段很长的描述...', 100) // 截断到 100 字符
 * truncateDescription(undefined) // ''
 * truncateDescription(null) // ''
 * ```
 */
export function truncateDescription(description: string | null | undefined, maxLength: number = 160): string {
  if (!description) {
    return '';
  }

  if (description.length <= maxLength) {
    return description.trim();
  }

  // 在最后一个完整句子处截断
  const truncated = description.slice(0, maxLength);
  const lastPeriod = truncated.lastIndexOf('。');
  const lastExclamation = truncated.lastIndexOf('！');
  const lastQuestion = truncated.lastIndexOf('？');
  const lastSentenceEnd = Math.max(lastPeriod, lastExclamation, lastQuestion);

  if (lastSentenceEnd > maxLength * 0.7) {
    return truncated.slice(0, lastSentenceEnd + 1);
  }

  // 在最后一个空格处截断（避免截断单词）
  const lastSpace = truncated.lastIndexOf(' ');
  if (lastSpace > maxLength * 0.8) {
    return truncated.slice(0, lastSpace) + '…';
  }

  return truncated + '…';
}

/**
 * 获取 Open Graph 类型
 *
 * @param pageType - 页面类型
 * @returns Open Graph 类型字符串
 */
export function getOgType(pageType: PageType = 'website'): string {
  return pageType;
}

/**
 * 创建完整的元标签对象
 *
 * @param meta - 元标签数据
 * @returns 包含 title, description, ogType 的对象
 *
 * @example
 * ```ts
 * createMetaData({
 *   title: 'Python基础课程',
 *   description: '学习Python编程基础知识',
 *   ogType: 'course'
 * })
 * ```
 */
export function createMetaData(meta: MetaData): {
  title: string;
  description: string;
  ogType: string;
} {
  return {
    title: formatTitle(meta.title),
    description: truncateDescription(meta.description) || DEFAULT_META.description,
    ogType: getOgType(meta.ogType),
  };
}

/**
 * 常用页面标题模板
 */
export const PAGE_TITLES = {
  /** 首页 */
  home: (username?: string) => username ? `${username}的首页` : '首页',
  /** 课程列表 */
  courses: '课程列表',
  /** 课程详情 */
  course: (courseTitle: string) => courseTitle,
  /** 章节列表 */
  chapters: (courseTitle: string) => `${courseTitle} - 章节列表`,
  /** 章节详情 */
  chapter: (chapterTitle: string, courseTitle: string) => `${chapterTitle} - ${courseTitle}`,
  /** 测验列表 */
  exams: (courseTitle: string) => `${courseTitle} - 测验`,
  /** 测验详情 */
  exam: (examTitle: string) => `${examTitle}`,
  /** 测验结果 */
  examResults: (examTitle: string) => `${examTitle} - 测验结果`,
  /** 题库列表 */
  problems: '题库',
  /** 题目详情 */
  problem: (problemTitle: string) => `${problemTitle} - 题目详情`,
  /** 个人中心 */
  profile: (username?: string) => username ? `${username} - 个人中心` : '个人中心',
  /** 会员方案 */
  membership: '会员方案',
  /** 代码练习场 */
  playground: '代码练习场',
  /** 学习数据分析 */
  performance: '学习数据分析',
  /** 讨论区 */
  threads: '讨论区',
  /** 讨论帖详情 */
  thread: (threadTitle: string) => `${threadTitle} - 讨论区`,
  /** Jupyter Notebook */
  jupyter: 'Jupyter Notebook',
  /** 登录 */
  login: '登录',
  /** 注册 */
  register: '注册',
  /** 登出 */
  logout: '登出',
  /** 订单详情 */
  order: '订单详情',
  /** 创建订单 */
  createOrder: '创建订单',
  /** 支付页面 */
  payment: '支付页面',
  /** 提交详情 */
  submission: '提交详情',
} as const;

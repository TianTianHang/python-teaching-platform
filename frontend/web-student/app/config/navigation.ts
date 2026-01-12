/**
 * Navigation Configuration - 导航配置
 *
 * 这是应用导航的单一真实来源。
 * 所有导航项应该在这里定义，便于维护和扩展。
 *
 * @see https://reactrouter.com/components/link
 */

import type { ComponentType } from 'react';

/**
 * 导航项接口
 */
export interface NavItem {
  /** 显示文本 */
  text: string;
  /** 路由路径 */
  path: string;
  /** 图标组件 (可选) */
  icon?: ComponentType;
  /** 所需权限 (可选，用于未来的权限控制) */
  requiredPermission?: string;
  /** 子导航项 (可选) */
  children?: NavItem[];
  /** 是否在导航中隐藏 (用于程序化导航) */
  hidden?: boolean;
}

/**
 * 主导航配置
 *
 * 注意：'Problems' 路径在原代码中是 '/Problems' (大写 P)，
 * 但为了 RESTful 风格的一致性，建议改为 '/problems'
 */
export const navConfig: NavItem[] = [
  {
    text: '首页',
    path: '/home',
  },
  {
    text: '课程',
    path: '/courses',
  },
  {
    text: 'Problems',
    path: '/problems',
  },
  {
    text: '测验',
    path: '/courses',
    hidden: true, // 隐藏在主导航中，只在课程页面显示
  },
  {
    text: 'Playground',
    path: '/playground',
  },
  {
    text: 'JupyterLite',
    path: '/jupyter',
  },
];

/**
 * 用户菜单配置
 */
export const userMenuConfig: NavItem[] = [
  {
    text: '用户信息',
    path: '/profile',
  },
  {
    text: '会员中心',
    path: '/membership',
  },
];

/**
 * 获取导航项
 *
 * @param userRole - 用户角色 (可选，用于未来的权限控制)
 * @returns 过滤后的导航项
 *
 * @example
 * ```tsx
 * import { getNavItems } from '~/config/navigation';
 *
 * const navItems = getNavItems();
 * navItems.map(item => <Link to={item.path}>{item.text}</Link>)
 * ```
 */
export function getNavItems(userRole?: string): NavItem[] {
  // 未来: 可以根据用户角色过滤导航项
  // 例如: 教师可以看到"管理面板"，学生不能

  return navConfig.filter(item => !item.hidden);
}

/**
 * 获取用户菜单项
 *
 * @param userRole - 用户角色 (可选)
 * @returns 过滤后的用户菜单项
 */
export function getUserMenuItems(userRole?: string): NavItem[] {
  return userMenuConfig.filter(item => !item.hidden);
}

/**
 * 根据路径查找导航项
 *
 * @param path - 路由路径
 * @returns 匹配的导航项或 undefined
 */
export function findNavItem(path: string): NavItem | undefined {
  // 首先匹配顶级导航
  const topLevelMatch = navConfig.find(item => item.path === path);
  if (topLevelMatch) {
    return topLevelMatch;
  }

  // 然后搜索子导航
  for (const item of navConfig) {
    if (item.children) {
      const childMatch = item.children.find(child => child.path === path);
      if (childMatch) {
        return childMatch;
      }
    }
  }

  return undefined;
}

/**
 * 检查路径是否为活动路径
 *
 * @param currentPath - 当前路径
 * @param itemPath - 导航项路径
 * @returns 是否匹配
 */
export function isActivePath(currentPath: string, itemPath: string): boolean {
  // 精确匹配
  if (currentPath === itemPath) {
    return true;
  }

  // 前缀匹配 (用于嵌套路由)
  // 例如: /courses/123 应该高亮 /courses
  if (currentPath.startsWith(itemPath + '/')) {
    return true;
  }

  return false;
}

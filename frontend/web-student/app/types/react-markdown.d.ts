/**
 * Type definitions for react-markdown to support custom foldableBlock nodes.
 * Extends the Components type to include our custom foldableBlock handler.
 */

import type { FoldableBlock } from './mdast';
import type { Components } from 'react-markdown';
import type { ComponentType } from 'react';

/**
 * Props for the FoldableBlock component
 */
export interface FoldableBlockProps {
  type: 'fold' | 'answer' | 'warning' | 'tip';
  title?: string;
  defaultExpanded?: boolean;
  children: React.ReactNode;
}

/**
 * Extended Components type that includes foldableBlock support.
 */
export type ExtendedComponents = Components & {
  foldableBlock?: ComponentType<any>;
};

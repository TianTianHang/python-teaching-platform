/**
 * Type definitions for custom MDAST nodes.
 * Extends the mdast types to include our custom foldableBlock node.
 */

import type { Parent, Literal } from 'mdast';

/**
 * Supported foldable block types
 */
export type FoldableBlockType = 'fold' | 'answer' | 'warning' | 'tip';

/**
 * Data interface for foldable block nodes
 */
export interface FoldableBlockData {
  type: FoldableBlockType;
  title?: string;
  defaultExpanded?: boolean;
  label?: string;
}

/**
 * Custom MDAST node for foldable blocks.
 * This node type is created by the remarkFoldableBlock plugin.
 */
export interface FoldableBlock extends Parent {
  type: 'foldableBlock';
  data: FoldableBlockData;
  children: Array<any>; // Markdown content inside the block
}

/**
 * Extend the MDAST ContentMap to include our custom foldableBlock type.
 */
declare module 'mdast' {
  interface ContentMap {
    foldableBlock: FoldableBlock;
  }
}

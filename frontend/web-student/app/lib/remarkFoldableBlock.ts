/**
 * Custom remark plugin to transform containerDirective nodes into foldableBlock nodes.
 * This plugin works with remark-directive to parse :::name[label]{attributes} syntax.
 *
 * Supported directive types: fold, answer, warning, tip
 *
 * Syntax examples:
 * - :::tip{title="Optional Title"}
 * - :::warning{title="Important Warning" state="expanded"}
 * - :::answer[ref-id]{title="Answer"}
 * - :::fold{title="Optional Title" state="collapsed"}
 */

import { visit } from 'unist-util-visit';
import type { Root, Parent } from 'mdast';
import { parseDirectiveAttributes } from './parseDirectiveAttributes';

// Supported foldable block types
export const FOLDABLE_BLOCK_TYPES = ['fold', 'answer', 'warning', 'tip'] as const;
export type FoldableBlockType = typeof FOLDABLE_BLOCK_TYPES[number];

/**
 * MDAST node type for foldable blocks (defined in types/mdast.d.ts)
 */
export interface FoldableBlockData {
  type: FoldableBlockType;
  title?: string;
  defaultExpanded?: boolean;
  label?: string;
}

// Extend the Content type to include foldableBlock (handled in types/mdast.d.ts)

/**
 * Remark plugin to transform containerDirective nodes into custom foldableBlock nodes.
 */
export const remarkFoldableBlock = () => {
  return (tree: Root) => {
    visit(tree, 'containerDirective', (node: any, index: number | undefined, parent: Parent | undefined) => {
      if (!parent || index === undefined) return;

      // Check if this is a foldable block directive
      if (!FOLDABLE_BLOCK_TYPES.includes(node.name)) return;

      const type = node.name as FoldableBlockType;

      // Parse attributes to extract title and state
      const { title } = parseDirectiveAttributes(node.attributes || {});

      // Determine default expanded state based on state attribute and type defaults
      const defaultExpanded = getDefaultExpanded(type, node.attributes || {});

      // Extract optional label from directive node
      // The label is stored in the node's data or can be parsed from children
      const label = node.label;
      const data={
          type,
          title,
          defaultExpanded,
          label,
        } as FoldableBlockData
      // Create the new foldableBlock node
      const foldableBlockNode: any = {
        data:{hProperties:{data}, hName: 'foldableBlock',} ,
        children: node.children || [],
      };

      // Replace the containerDirective node with our custom node
      parent.children[index] = foldableBlockNode;
    });
  };
};

/**
 * Get the default expanded state for a foldable block.
 * Priority: explicit state attribute > class attribute > type default
 *
 * @param type - The foldable block type (fold, answer, warning, tip)
 * @param attributes - The directive attributes object
 * @returns true if the block should be expanded by default
 */
function getDefaultExpanded(
  type: FoldableBlockType,
  attributes: Record<string, string | undefined>
): boolean {
  // Check explicit state attribute
  if (attributes.state === 'expanded') return true;
  if (attributes.state === 'collapsed') return false;

  // Check class attribute for shortcuts like {.expanded} or {.collapsed}
  if (attributes.class === 'expanded') return true;
  if (attributes.class === 'collapsed') return false;

  // Use type-based defaults when not specified
  // fold: collapsed, answer: collapsed, warning: expanded, tip: expanded
  return type === 'warning' || type === 'tip';
}

export default remarkFoldableBlock;

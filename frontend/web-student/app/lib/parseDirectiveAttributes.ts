/**
 * Parse directive attributes object to extract title and state.
 * Handles various attribute formats: {title="Title"}, {title='Title'}, {title=Title}
 * Handles state attributes: {state=expanded}, {state=collapsed}, {.expanded}, {.collapsed}
 * Handles mixed attribute styles: {state=expanded .my-class title="Title"}
 */

export interface ParsedAttributes {
  title?: string;
  state?: 'expanded' | 'collapsed';
}

/**
 * Parse directive attributes for foldable blocks.
 * The attributes come from remark-directive as a Record<string, string | undefined>.
 *
 * Examples:
 * - {title="My Title"} -> { title: "My Title" }
 * - {state=expanded} -> { state: "expanded" }
 * - {.expanded} -> { state: "expanded" }
 * - {title="Title" state=collapsed} -> { title: "Title", state: "collapsed" }
 */
export function parseDirectiveAttributes(
  attributes: Record<string, string | undefined>
): ParsedAttributes {
  const result: ParsedAttributes = {};

  // Extract title from attributes
  if (attributes.title) {
    result.title = attributes.title;
  }

  // Extract state from various sources
  // Priority: explicit state attribute > class attribute > type default
  const state = attributes.state || attributes.class;

  if (state === 'expanded' || state === 'collapsed') {
    result.state = state;
  }

  // Note: Type-based defaults are handled in the remarkFoldableBlock plugin
  // and the FoldableBlock component, not here.

  return result;
}

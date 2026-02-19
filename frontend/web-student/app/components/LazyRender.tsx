/**
 * LazyRender component - Defers rendering until the element enters the viewport.
 *
 * Uses Intersection Observer API for efficient viewport detection.
 * Improves initial page load performance by only rendering visible content.
 *
 * Features:
 * - Server-side rendering compatible
 * - Configurable root margin for early/pre-load
 * - Fallback content during loading
 * - Only renders once when element comes into view
 */

'use client';

import { useEffect, useRef, useState } from 'react';

export interface LazyRenderProps {
  /** Content to render when in view */
  children: React.ReactNode;
  /** Content to show before element enters viewport (e.g., a skeleton or placeholder) */
  fallback?: React.ReactNode;
  /** Margin around the root (in pixels) to trigger loading early */
  rootMargin?: string;
  /** Fraction of element visibility required to trigger render */
  threshold?: number;
  /** Skip lazy loading and render immediately (useful for already-visible content) */
  skip?: boolean;
}

/**
 * LazyRender component defers rendering of children until they enter the viewport.
 */
export default function LazyRender({
  children,
  fallback = null,
  rootMargin = '100px',
  threshold = 0.01,
  skip = false,
}: LazyRenderProps) {
  const [isVisible, setIsVisible] = useState(skip);
  const [hasIntersected, setHasIntersected] = useState(skip);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || hasIntersected || skip) return;

    // Check if Intersection Observer is available
    if (!('IntersectionObserver' in window)) {
      // Fallback for browsers without Intersection Observer
      setIsVisible(true);
      return;
    }

    // Create Intersection Observer
    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          setIsVisible(true);
          setHasIntersected(true);
          observer.disconnect(); // Only need to observe once
        }
      },
      {
        rootMargin, // Start loading before element is fully visible
        threshold, // Trigger when 1% of element is visible
      }
    );

    observer.observe(container);

    return () => {
      observer.disconnect();
    };
  }, [hasIntersected, rootMargin, threshold, skip]);

  return (
    <div ref={containerRef} style={{ minHeight: isVisible ? 'auto' : '50px' }}>
      {isVisible ? children : fallback}
    </div>
  );
}

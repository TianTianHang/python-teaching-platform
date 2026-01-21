import { useEffect, useState, useCallback, useRef } from "react";
import { useFetcher } from "react-router";

// JSON primitive types for submission
type JsonPrimitive = string | number | boolean | null;
type JsonObject = { [key: string]: JsonValue };
type JsonArray = JsonValue[];
export type JsonValue = JsonPrimitive | JsonObject | JsonArray;

/**
 * Options for useFetcherAction hook
 */
export interface UseFetcherActionOptions<TData, TError = string> {
    /** Action URL or route path */
    action: string;
    /** HTTP method (default: 'POST') */
    method?: "POST" | "PUT" | "PATCH" | "DELETE" | "GET";
    /** Timeout in milliseconds (default: 30000) */
    timeout?: number;
    /** Callback on successful submission */
    onSuccess?: (data: TData) => void;
    /** Callback on error */
    onError?: (error: TError) => void;
    /** Custom error messages (maps error keys to messages) */
    errorMessages?: Record<string, string>;
    /** Function to check if response data indicates an error */
    isErrorResponse?: (data: unknown) => boolean;
    /** Function to extract error message from response data */
    getErrorMessage?: (data: unknown) => string;
}

/**
 * Return type for useFetcherAction hook
 */
export interface UseFetcherActionReturn<TData, TError = string> {
    /** loade data to the action */
    loader: () => void;
    /** Submit data to the action */
    submit: (data: unknown) => void;
    /** Current loading state (true when submitting or loading) */
    isLoading: boolean;
    /** Is currently submitting */
    isSubmitting: boolean;
    /** Response data from action (may be serialized) */
    data: TData | null;
    /** Error from action */
    error: TError | null;
    /** Raw fetcher for advanced use cases */
    fetcher: ReturnType<typeof useFetcher<TData>>;
}

/**
 * A generic hook that wraps React Router's useFetcher to simplify form submissions
 * and data mutations with automatic loading states, error handling, and timeouts.
 *
 * @template TData - The type of data returned from the action
 * @template TError - The type of error (defaults to string)
 *
 * @example
 * ```tsx
 * const { submit, isLoading, error } = useFetcherAction<ExamSubmission, string>({
 *   action: `/courses/${courseId}/exams/${examId}/submit`,
 *   method: 'POST',
 *   timeout: 30000,
 *   onSuccess: (data) => {
 *     navigate(`/courses/${courseId}/exams/${examId}/results`);
 *   },
 *   errorMessages: {
 *     TIMEOUT: '请求超时',
 *     NETWORK_ERROR: '网络错误',
 *   },
 * });
 *
 * const handleSubmit = () => {
 *   submit({ answers: answersArray });
 * };
 * ```
 */
export function useFetcherAction<TData = unknown, TError = string>(
    options: UseFetcherActionOptions<TData, TError>
): UseFetcherActionReturn<TData, TError> {
    const {
        action,
        method = "POST",
        timeout = 30000,
        errorMessages = {},
        isErrorResponse = () => false,
        getErrorMessage = (data) => String(data),
    } = options;

    const fetcher = useFetcher<TData>();
    const [error, setError] = useState<TError | null>(null);

    // Use ref to store the latest callbacks to avoid closure issues
    const callbacksRef = useRef<{
        onSuccess?: (data: TData) => void;
        onError?: (error: TError) => void;
    }>({});

    // Track timeout
    const timeoutRef = useRef<NodeJS.Timeout | null>(null);
    const hasTimedOutRef = useRef(false);
    const timeoutTriggeredRef = useRef(false); // Track if timeout was already triggered for this submission

    // Reset error and timeout flag when submission starts
    useEffect(() => {
        if (fetcher.state === "submitting") {
            setError(null);
            hasTimedOutRef.current = false;
            timeoutTriggeredRef.current = false; // Reset timeout triggered flag

            // Clear any existing timeout
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
            }

            // Set new timeout
            if (timeout > 0) {
                timeoutRef.current = setTimeout(() => {
                    // Only set timeout error if still submitting AND not already triggered
                    if (fetcher.state === "submitting" && !timeoutTriggeredRef.current) {
                        timeoutTriggeredRef.current = true; // Mark as triggered
                        hasTimedOutRef.current = true;
                        const timeoutError = (errorMessages.TIMEOUT || "请求超时，请重试") as TError;
                        setError(timeoutError);
                        callbacksRef.current.onError?.(timeoutError);
                    }
                }, timeout);
            }
        }

        // Cleanup timeout when fetcher state changes or component unmounts
        return () => {
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
                timeoutRef.current = null;
            }
        };
    }, [fetcher.state, timeout, errorMessages.TIMEOUT]);

    // Handle fetcher completion
    useEffect(() => {
        // Only process if we haven't timed out
        if (hasTimedOutRef.current) {
            return;
        }

        if (fetcher.state === "idle") {
            // Clear timeout when request completes
            if (timeoutRef.current) {
                clearTimeout(timeoutRef.current);
                timeoutRef.current = null;
            }

            // Check if we have data
            if (fetcher.data !== undefined) {
                // Check if the data represents an error
                if (isErrorResponse(fetcher.data)) {
                    const errorMsg = getErrorMessage(fetcher.data) as TError;
                    setError(errorMsg);
                    callbacksRef.current.onError?.(errorMsg);
                } else {
                    // Success: clear error and call success callback
                    setError(null);
                    callbacksRef.current.onSuccess?.(fetcher.data as TData);
                }
            }
        }
    }, [fetcher.state, fetcher.data]);

    // Submit function
    const submit = useCallback(
        (data: unknown) => {
            if (method === "GET") {
                throw new Error("GET method does not support submit with data. Use loader() instead.");
            }
            // Update callbacks ref
            callbacksRef.current = {
                onSuccess: options.onSuccess,
                onError: options.onError,
            };

            // Reset timeout flag
            hasTimedOutRef.current = false;

            // Submit data as JSON object directly
            // React Router will serialize it
            fetcher.submit(data as JsonValue, {
                method,
                action,
                encType: "application/json",
            });
        },
        [fetcher, action, method, options.onSuccess, options.onError]
    );
    const loader = useCallback(
        () => {
            if (method !== "GET") {
                throw new Error("Only GET method is supported for loader().");
            }
            // Update callbacks ref
            callbacksRef.current = {
                onSuccess: options.onSuccess,
                onError: options.onError,
            };

            // Reset timeout flag
            hasTimedOutRef.current = false;
            fetcher.load(action);
        },
        [fetcher, action, method, options.onSuccess, options.onError]
    );
    return {
        loader,
        submit,
        isLoading: fetcher.state !== "idle",
        isSubmitting: fetcher.state === "submitting",
        data: (fetcher.data ?? null) as TData | null,
        error,
        fetcher,
    };
}

export default useFetcherAction;
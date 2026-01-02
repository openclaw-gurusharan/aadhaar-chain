'use client';

import { useState, useCallback, useRef } from 'react';
import type { ApiCallState } from '@/lib/types';

// Configuration
const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 1000;
const DEFAULT_RETRY_ON_STATUS = [500, 502, 503, 504];

interface UseApiCallOptions {
  maxRetries?: number;
  retryDelay?: number;
  retryOnStatus?: number[];
  onSuccess?: () => void;
  onError?: (error: string) => void;
  showToasts?: boolean;
}

/**
 * Hook for managing API call state with retry logic and loading states
 *
 * @example
 * const { data, loading, error, execute } = useApiCall({
 *   maxRetries: 3,
 *   onSuccess: () => toast.success('Success!'),
 *   onError: (msg) => toast.error(msg)
 * });
 *
 * // Call with async function
 * execute(() => apiClient.getData(id));
 */
export function useApiCall<T = unknown>(options: UseApiCallOptions = {}) {
  const {
    maxRetries = MAX_RETRIES,
    retryDelay = RETRY_DELAY_MS,
    retryOnStatus = DEFAULT_RETRY_ON_STATUS,
    onSuccess,
    onError,
    showToasts = true,
  } = options;

  const [state, setState] = useState<{
    data: T | null;
    loading: boolean;
    error: string | null;
  }>({
    data: null,
    loading: false,
    error: null,
  });

  const retryCount = useRef(0);
  const abortController = useRef<AbortController | null>(null);

  const sleep = (ms: number) =>
    new Promise((resolve) => setTimeout(resolve, ms));

  const execute = useCallback(
    async (apiFunction: () => Promise<T>) => {
      // Cancel previous request
      if (abortController.current) {
        abortController.current.abort();
      }
      abortController.current = new AbortController();

      setState({ data: null, loading: true, error: null });
      retryCount.current = 0;

      let lastError: string | null = null;

      for (let attempt = 0; attempt <= maxRetries; attempt++) {
        try {
          const result = await apiFunction();

          setState({ data: result, loading: false, error: null });
          onSuccess?.();

          return result;
        } catch (err) {
          const error = err as { response?: { status?: number }; message?: string };
          lastError = error.message || 'An error occurred';

          const status = error.response?.status;
          const shouldRetry = retryOnStatus.includes(status || 0);

          if (attempt < maxRetries && shouldRetry) {
            retryCount.current = attempt + 1;
            await sleep(retryDelay * Math.pow(2, attempt)); // Exponential backoff
            continue;
          }

          setState({ data: null, loading: false, error: lastError });
          onError?.(lastError);
          throw err;
        }
      }

      return null as T | null;
    },
    [maxRetries, retryDelay, retryOnStatus, onSuccess, onError]
  );

  const reset = useCallback(() => {
    if (abortController.current) {
      abortController.current.abort();
      abortController.current = null;
    }
    setState({ data: null, loading: false, error: null });
    retryCount.current = 0;
  }, []);

  const retry = useCallback(() => {
    // Note: retry only works if the caller has stored the original apiFunction
    // This is a no-op placeholder - callers should re-call execute()
  }, []);

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    execute,
    reset,
    retry,
  } as ApiCallState<T> & { execute: (fn: () => Promise<T>) => Promise<T | null>; reset: () => void };
}

/**
 * Hook for paginated API calls
 */
export function usePaginatedApiCall<T = unknown>(options: UseApiCallOptions = {}) {
  const [state, setState] = useState<{
    data: T[];
    loading: boolean;
    error: string | null;
    hasMore: boolean;
    page: number;
  }>({
    data: [],
    loading: false,
    error: null,
    hasMore: true,
    page: 1,
  });

  const loadMore = useCallback(
    async (apiFunction: (page: number) => Promise<{ data: T[]; hasMore?: boolean }>) => {
      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const result = await apiFunction(state.page);
        const hasMore = result.hasMore ?? result.data.length > 0;

        setState((prev) => ({
          data: [...prev.data, ...result.data],
          loading: false,
          error: null,
          hasMore,
          page: prev.page + 1,
        }));

        return result;
      } catch (err) {
        const error = err as Error;
        const errorMessage = error.message || 'Failed to load more items';
        setState((prev) => ({ ...prev, loading: false, error: errorMessage }));
        throw err;
      }
    },
    [state.page]
  );

  const refresh = useCallback(
    async (apiFunction: (page: number) => Promise<{ data: T[]; hasMore?: boolean }>) => {
      setState({ data: [], loading: true, error: null, hasMore: true, page: 1 });

      try {
        const result = await apiFunction(1);
        const hasMore = result.hasMore ?? result.data.length > 0;

        setState({
          data: result.data,
          loading: false,
          error: null,
          hasMore,
          page: 2,
        });

        return result;
      } catch (err) {
        const error = err as Error;
        const errorMessage = error.message || 'Failed to refresh';
        setState({ data: [], loading: false, error: errorMessage, hasMore: true, page: 1 });
        throw err;
      }
    },
    []
  );

  return {
    data: state.data,
    loading: state.loading,
    error: state.error,
    hasMore: state.hasMore,
    loadMore,
    refresh,
  };
}

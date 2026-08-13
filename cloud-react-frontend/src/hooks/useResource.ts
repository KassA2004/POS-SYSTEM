import { useCallback, useEffect, useState } from 'react';
import { extractErrorMessage } from '@/services/api';

export interface ResourceState<T> {
  data: T;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
}

/**
 * Generic loader for a read endpoint. Pages compose one of these per resource
 * instead of each re-implementing loading/error/refetch state, which also keeps
 * the data out of component props.
 *
 * `loader` must be stable (wrap in useCallback at the call site) or the effect
 * will refetch on every render.
 */
export function useResource<T>(loader: () => Promise<T>, initial: T): ResourceState<T> {
  const [data, setData] = useState<T>(initial);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await loader();
      setData(result);
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [loader]);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const result = await loader();
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(extractErrorMessage(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void run();
    return () => {
      cancelled = true;
    };
  }, [loader]);

  return { data, loading, error, reload };
}

export default useResource;

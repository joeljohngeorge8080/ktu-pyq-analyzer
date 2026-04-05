import { useState, useEffect, useCallback } from 'react'

export function useApi(fetchFn, deps = [], opts = {}) {
  const [data, setData] = useState(opts.initial ?? null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const reload = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchFn()
      setData(result)
    } catch (e) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }, deps) // eslint-disable-line

  useEffect(() => { reload() }, [reload])

  return { data, loading, error, reload }
}

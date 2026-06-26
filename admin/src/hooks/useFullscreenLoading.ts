import { type LoadingOptions, ElLoading } from "element-plus"

const defaultOptions = {
  lock: true,
  text: "Loading..."
}

interface LoadingInstance {
  close: () => void
}

interface UseFullscreenLoading {
  <T extends (...args: any[]) => ReturnType<T>>(
    fn: T,
    options?: LoadingOptions
  ): (...args: Parameters<T>) => Promise<ReturnType<T>>
}

/**
 * Pass in a function fn, add fullscreen loading during its execution cycle
 * @param fn Function to execute
 * @param options LoadingOptions
 * @returns Returns a new function that returns a Promise
 */
export const useFullscreenLoading: UseFullscreenLoading = (fn, options = {}) => {
  let loadingInstance: LoadingInstance
  return async (...args) => {
    try {
      loadingInstance = ElLoading.service({ ...defaultOptions, ...options })
      return await fn(...args)
    } finally {
      loadingInstance?.close()
    }
  }
}

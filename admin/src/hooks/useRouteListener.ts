import { onBeforeUnmount } from "vue"
import mitt, { type Handler } from "mitt"
import { type RouteLocationNormalized } from "vue-router"

/** Callback function type */
type Callback = (route: RouteLocationNormalized) => void

const emitter = mitt()
const key = Symbol("ROUTE_CHANGE")
let latestRoute: RouteLocationNormalized

/** Set latest route info and trigger route change event */
export const setRouteChange = (to: RouteLocationNormalized) => {
  // Trigger event
  emitter.emit(key, to)
  // Cache latest route info
  latestRoute = to
}

/** Monitoring routes separately wastes rendering performance, use publish-subscribe pattern for distribution management */
export function useRouteListener() {
  /** Callback function collection */
  const callbackList: Callback[] = []

  /** Listen to route changes (can choose to execute immediately) */
  const listenerRouteChange = (callback: Callback, immediate = false) => {
    // Cache callback function
    callbackList.push(callback)
    // Listen to event
    emitter.on(key, callback as Handler)
    // Can choose to execute callback function once immediately
    immediate && latestRoute && callback(latestRoute)
  }

  /** Remove route change event listener */
  const removeRouteListener = (callback: Callback) => {
    emitter.off(key, callback as Handler)
  }

  /** Remove listeners before component is destroyed */
  onBeforeUnmount(() => {
    for (let i = 0; i < callbackList.length; i++) {
      removeRouteListener(callbackList[i])
    }
  })

  return { listenerRouteChange, removeRouteListener }
}

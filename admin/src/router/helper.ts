import {
  type Router,
  type RouteRecordNormalized,
  type RouteRecordRaw,
  createRouter,
  createWebHashHistory,
  createWebHistory
} from "vue-router"
import { cloneDeep, omit } from "lodash-es"

/** Router mode */
export const history =
  import.meta.env.VITE_ROUTER_HISTORY === "hash"
    ? createWebHashHistory(import.meta.env.VITE_PUBLIC_PATH)
    : createWebHistory(import.meta.env.VITE_PUBLIC_PATH)

/** Route flattening (converts level-3 and above routes to level-2 routes) */
export const flatMultiLevelRoutes = (routes: RouteRecordRaw[]) => {
  const routesMirror = cloneDeep(routes)
  routesMirror.forEach((route) => {
    // If route is level-3 or above, flatten it
    isMultipleRoute(route) && promoteRouteLevel(route)
  })
  return routesMirror
}

/** Check if route level is greater than 2 */
const isMultipleRoute = (route: RouteRecordRaw) => {
  const children = route.children
  if (children?.length) {
    // If any child route has children length > 0, it's a level-3+ route
    return children.some((child) => child.children?.length)
  }
  return false
}

/** Generate level-2 routes */
const promoteRouteLevel = (route: RouteRecordRaw) => {
  // Create router instance to get all route information for the current route
  let router: Router | null = createRouter({
    history,
    routes: [route]
  })
  const routes = router.getRoutes()
  // Use route information obtained above in addToChildren function to update route's children
  addToChildren(routes, route.children || [], route)
  router = null
  // After converting to level-2 routes, remove children from all child routes
  route.children = route.children?.map((item) => omit(item, "children") as RouteRecordRaw)
}

/** Add given child routes to specified route module */
const addToChildren = (routes: RouteRecordNormalized[], children: RouteRecordRaw[], routeModule: RouteRecordRaw) => {
  children.forEach((child) => {
    const route = routes.find((item) => item.name === child.name)
    if (route) {
      // Initialize routeModule's children
      routeModule.children = routeModule.children || []
      // If routeModule's children property doesn't include this route, add it
      if (!routeModule.children.includes(route)) {
        routeModule.children.push(route)
      }
      // If child route has its own children, recursively call this function to add them too
      if (child.children?.length) {
        addToChildren(routes, child.children, routeModule)
      }
    }
  })
}

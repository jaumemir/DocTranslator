import router from "@/router"
import { useUserStoreHook } from "@/store/modules/user"
import { usePermissionStoreHook } from "@/store/modules/permission"
import { ElMessage } from "element-plus"
import { setRouteChange } from "@/hooks/useRouteListener"
import { useTitle } from "@/hooks/useTitle"
import { getToken } from "@/utils/cache/cookies"
import routeSettings from "@/config/route"
import isWhiteList from "@/config/white-list"
import NProgress from "nprogress"
import "nprogress/nprogress.css"

const { setTitle } = useTitle()
NProgress.configure({ showSpinner: false })

router.beforeEach(async (to, _from, next) => {
  NProgress.start()
  const userStore = useUserStoreHook()
  const permissionStore = usePermissionStoreHook()
  const token = getToken()
  // If not logged in
  if (!token) {
    // If in the whitelist, allow direct access
    if (isWhiteList(to)) return next()
    // Other pages without access permission will be redirected to login page
    return next("/login")
  }

  // If already logged in and trying to enter Login page, redirect to home
  if (to.path === "/login") {
    return next({ path: "/" })
  }

  // If user has already obtained their permission roles
  if (userStore.roles.length !== 0) return next()

  // Otherwise, need to re-fetch permission roles
  try {
    // await userStore.getInfo()
    // Note: roles must be an array! For example: ["admin"] or ["developer", "editor"]
    const roles = userStore.roles
    // Generate accessible Routes
    routeSettings.dynamic ? permissionStore.setRoutes(roles) : permissionStore.setAllRoutes()
    // Add "dynamic routes with access permission" to Router
    permissionStore.addRoutes.forEach((route) => router.addRoute(route))
    // Ensure routes have been added
    // Set replace: true so navigation won't leave history
    // next({ ...to, replace: true })

    next()
  } catch (err: any) {
    console.log("catch")
    // If any error occurs, reset Token and redirect to login page
    userStore.resetToken()
    ElMessage.error(err.message || "Error occurred during route guard process")
    next("/login")
  }
})

router.afterEach((to) => {
  setRouteChange(to)
  setTitle(to.meta.title)
  NProgress.done()
})

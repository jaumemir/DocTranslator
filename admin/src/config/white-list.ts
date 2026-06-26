import { type RouteLocationNormalized } from "vue-router"

/** Login-free whitelist (match route path) */
const whiteListByPath: string[] = ["/login"]

/** Login-free whitelist (match route name) */
const whiteListByName: string[] = []

/** Check if in whitelist */
const isWhiteList = (to: RouteLocationNormalized) => {
  // Match either path or name
  return whiteListByPath.indexOf(to.path) !== -1 || whiteListByName.indexOf(to.name as any) !== -1
}

export default isWhiteList

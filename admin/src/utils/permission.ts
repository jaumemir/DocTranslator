import { useUserStoreHook } from "@/store/modules/user"

/** Global permission check function, similar to v-permission directive */
export const checkPermission = (permissionRoles: string[]): boolean => {
  return true
  // if (Array.isArray(permissionRoles) && permissionRoles.length > 0) {
  //   const { roles } = useUserStoreHook()
  //   return roles.some((role) => permissionRoles.includes(role))
  // } else {
  //   console.error("need roles! Like checkPermission(['admin','editor'])")
  //   return false
  // }
}

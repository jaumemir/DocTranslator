/** Route configuration */
interface RouteSettings {
  /**
   * Enable dynamic routing functionality?
   * 1. When enabled, backend cooperation is required to return fields that can be used to determine and load dynamic routes in the user details query API (this project uses the roles field)
   * 2. If the project doesn't need to display different pages for different users, set dynamic: false
   */
  dynamic: boolean
  /** When dynamic routing is disabled:
   * 1. All routes should be written in constant routes (indicating all logged-in users can access the same pages)
   * 2. The system automatically assigns a default role with no effect to the current logged-in user
   */
  defaultRoles: Array<string>
  /**
   * Enable third-level and above route caching?
   * 1. When enabled, route downgrading will occur (converting third-level and above routes to second-level routes)
   * 2. Since all will be converted to second-level routes, second-level and above routes with nested sub-routes will become invalid
   */
  thirdLevelRouteCache: boolean
}

const routeSettings: RouteSettings = {
  dynamic: true,
  defaultRoles: ["DEFAULT_ROLE"],
  thirdLevelRouteCache: false
}

export default routeSettings

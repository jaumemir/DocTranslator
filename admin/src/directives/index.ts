import { type App } from "vue"
import { permission } from "./permission"

/** Mount custom directives */
export function loadDirectives(app: App) {
  app.directive("permission", permission)
}

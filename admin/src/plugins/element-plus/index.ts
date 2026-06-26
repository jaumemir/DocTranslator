import { type App } from "vue"
import ElementPlus from "element-plus"
import en from "element-plus/es/locale/lang/en.mjs"

export function loadElementPlus(app: App) {
  /** Full import of Element Plus components with English locale */
  app.use(ElementPlus, {
    locale: en
  })
}

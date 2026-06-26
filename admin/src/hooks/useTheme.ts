import { ref, watchEffect } from "vue"
import { getActiveThemeName, setActiveThemeName } from "@/utils/cache/local-storage"

const DEFAULT_THEME_NAME = "normal"
type DefaultThemeName = typeof DEFAULT_THEME_NAME

/** Registered theme names, DefaultThemeName is required */
export type ThemeName = DefaultThemeName | "dark" | "dark-blue"

interface ThemeList {
  title: string
  name: ThemeName
}

/** Theme list */
const themeList: ThemeList[] = [
  {
    title: "Default",
    name: DEFAULT_THEME_NAME
  },
  {
    title: "Dark",
    name: "dark"
  },
  {
    title: "Dark Blue",
    name: "dark-blue"
  }
]

/** Currently applied theme name */
const activeThemeName = ref<ThemeName>(getActiveThemeName() || DEFAULT_THEME_NAME)

/** Set theme */
const setTheme = (value: ThemeName) => {
  activeThemeName.value = value
}

/** Mount class on html root element */
const setHtmlRootClassName = (value: ThemeName) => {
  document.documentElement.className = value
}

/** Initialize */
const initTheme = () => {
  // Use watchEffect to collect side effects
  watchEffect(() => {
    const value = activeThemeName.value
    setHtmlRootClassName(value)
    setActiveThemeName(value)
  })
}

/** Theme hook */
export function useTheme() {
  return { themeList, activeThemeName, initTheme, setTheme }
}

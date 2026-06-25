import { getConfigLayout } from "@/utils/cache/local-storage"
import { LayoutModeEnum } from "@/constants/app-key"

/** Project configuration type */
export interface LayoutSettings {
  /** Whether to show Settings Panel */
  showSettings: boolean
  /** Layout mode */
  layoutMode: LayoutModeEnum
  /** Whether to show tags view */
  showTagsView: boolean
  /** Whether to show Logo */
  showLogo: boolean
  /** Whether to fix Header */
  fixedHeader: boolean
  /** Whether to show Footer */
  showFooter: boolean
  /** Whether to show notifications */
  showNotify: boolean
  /** Whether to show theme switch button */
  showThemeSwitch: boolean
  /** Whether to show fullscreen button */
  showScreenfull: boolean
  /** Whether to show search menu button */
  showSearchMenu: boolean
  /** Whether to cache tags view */
  cacheTagsView: boolean
  /** Enable system watermark */
  showWatermark: boolean
  /** Whether to show grey mode */
  showGreyMode: boolean
  /** Whether to show color weakness mode */
  showColorWeakness: boolean
}

/** Default configuration */
const defaultSettings: LayoutSettings = {
  layoutMode: LayoutModeEnum.Left,
  showSettings: true,
  showTagsView: true,
  fixedHeader: true,
  showFooter: true,
  showLogo: true,
  showNotify: true,
  showThemeSwitch: true,
  showScreenfull: true,
  showSearchMenu: true,
  cacheTagsView: false,
  showWatermark: true,
  showGreyMode: false,
  showColorWeakness: false
}

/** Project configuration */
export const layoutSettings: LayoutSettings = { ...defaultSettings, ...getConfigLayout() }

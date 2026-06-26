import { type Ref, ref, watch } from "vue"
import { defineStore } from "pinia"
import { type LayoutSettings, layoutSettings } from "@/config/layouts"
import { setConfigLayout } from "@/utils/cache/local-storage"

type SettingsStore = {
  // 使用映射类型来遍历 layoutSettings 对象的键
  [Key in keyof LayoutSettings]: Ref<LayoutSettings[Key]>
}

type SettingsStoreKey = keyof SettingsStore

export const useSettingsStore = defineStore("settings", () => {
  /** State object */
  const state = {} as SettingsStore
  // Iterate over key-value pairs of layoutSettings object
  for (const [key, value] of Object.entries(layoutSettings)) {
    // Use type assertion to specify key type, wrap value in ref function to create a reactive variable
    const refValue = ref(value)
    // @ts-ignore
    state[key as SettingsStoreKey] = refValue
    // Watch each reactive variable
    watch(refValue, () => {
      // Cache
      const settings = _getCacheData()
      setConfigLayout(settings)
    })
  }
  /** Get data to cache: convert state object to settings object */
  const _getCacheData = () => {
    const settings = {} as LayoutSettings
    for (const [key, value] of Object.entries(state)) {
      // @ts-ignore
      settings[key as SettingsStoreKey] = value.value
    }
    return settings
  }

  return state
})

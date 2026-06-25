import { defineConfig, presetAttributify, presetUno } from "unocss"

export default defineConfig({
  /** Presets */
  presets: [
    /** Attributify mode & valueless attribute mode */
    presetAttributify(),
    /** Default preset */
    presetUno()
  ],
  /** Custom rules */
  rules: [["uno-padding-20", { padding: "20px" }]],
  /** Custom shortcuts */
  shortcuts: {
    "uno-wh-full": "w-full h-full",
    "uno-flex-center": "flex justify-center items-center",
    "uno-flex-x-center": "flex justify-center",
    "uno-flex-y-center": "flex items-center"
  }
})

<script lang="ts" setup>
import { computed, watchEffect } from "vue"
import { storeToRefs } from "pinia"
import { useSettingsStore } from "@/store/modules/settings"
import useResize from "./hooks/useResize"
import { useWatermark } from "@/hooks/useWatermark"
import { useDevice } from "@/hooks/useDevice"
import { useLayoutMode } from "@/hooks/useLayoutMode"
import LeftMode from "./LeftMode.vue"
import TopMode from "./TopMode.vue"
import LeftTopMode from "./LeftTopMode.vue"
import { Settings, RightPanel } from "./components"
import { getCssVariableValue, setCssVariableValue } from "@/utils"

/** Layout responsive */
useResize()

const { setWatermark, clearWatermark } = useWatermark()
const { isMobile } = useDevice()
const { isLeft, isTop, isLeftTop } = useLayoutMode()
const settingsStore = useSettingsStore()
const { showSettings, showTagsView, showWatermark, showGreyMode, showColorWeakness } = storeToRefs(settingsStore)

const classes = computed(() => {
  return {
    showGreyMode: showGreyMode.value,
    showColorWeakness: showColorWeakness.value
  }
})

//#region Remove tags view height when hidden to keep Logo component height and Header area height consistent
const cssVariableName = "--v3-tagsview-height"
const v3TagsviewHeight = getCssVariableValue(cssVariableName)
watchEffect(() => {
  showTagsView.value
    ? setCssVariableValue(cssVariableName, v3TagsviewHeight)
    : setCssVariableValue(cssVariableName, "0px")
})
//#endregion

/** Enable or disable system watermark */
watchEffect(() => {
  // showWatermark.value ? setWatermark(import.meta.env.VITE_APP_TITLE) : clearWatermark()
  clearWatermark()
})
</script>

<template>
  <div :class="classes">
    <!-- Left mode -->
    <LeftMode v-if="isLeft || isMobile" />
    <!-- Top mode -->
    <TopMode v-else-if="isTop" />
    <!-- Mixed mode -->
    <LeftTopMode v-else-if="isLeftTop" />
    <!-- Right settings panel -->
    <!-- <RightPanel v-if="showSettings">
      <Settings />
    </RightPanel> -->
  </div>
</template>

<style lang="scss" scoped>
.showGreyMode {
  filter: grayscale(1);
}

.showColorWeakness {
  filter: invert(0.8);
}
</style>

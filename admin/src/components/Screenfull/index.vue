<script lang="ts" setup>
import { computed, ref, watchEffect } from "vue"
import { ElMessage } from "element-plus"
import screenfull from "screenfull"

interface Props {
  /** Fullscreen element, default is html */
  element?: string
  /** Open fullscreen tooltip */
  openTips?: string
  /** Exit fullscreen tooltip */
  exitTips?: string
  /** Whether to only target content area */
  content?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  element: "html",
  openTips: "Fullscreen",
  exitTips: "Exit Fullscreen",
  content: false
})

//#region Fullscreen
const isFullscreen = ref<boolean>(false)
const fullscreenTips = computed(() => {
  return isFullscreen.value ? props.exitTips : props.openTips
})
const fullscreenSvgName = computed(() => {
  return isFullscreen.value ? "fullscreen-exit" : "fullscreen"
})
const handleFullscreenClick = () => {
  const dom = document.querySelector(props.element) || undefined
  screenfull.isEnabled ? screenfull.toggle(dom) : ElMessage.warning("Your browser cannot work")
}
const handleFullscreenChange = () => {
  isFullscreen.value = screenfull.isFullscreen
  // Clear all classes when exiting fullscreen
  isFullscreen.value || (document.body.className = "")
}
watchEffect((onCleanup) => {
  // Auto-execute when component mounts
  screenfull.isEnabled && screenfull.on("change", handleFullscreenChange)
  // Auto-execute when component unmounts
  onCleanup(() => {
    screenfull.isEnabled && screenfull.off("change", handleFullscreenChange)
  })
})
//#endregion

//#region Content area
const isContentLarge = ref<boolean>(false)
const contentLargeTips = computed(() => {
  return isContentLarge.value ? "Restore Content Area" : "Enlarge Content Area"
})
const contentLargeSvgName = computed(() => {
  return isContentLarge.value ? "fullscreen-exit" : "fullscreen"
})
const handleContentLargeClick = () => {
  isContentLarge.value = !isContentLarge.value
  // Hide unnecessary components when content area is enlarged
  document.body.className = isContentLarge.value ? "content-large" : ""
}
const handleContentFullClick = () => {
  // Cancel content area enlargement
  isContentLarge.value && handleContentLargeClick()
  // Hide unnecessary components when content area is fullscreen
  document.body.className = "content-full"
  // Enable fullscreen
  handleFullscreenClick()
}
//#endregion
</script>

<template>
  <div>
    <!-- Fullscreen -->
    <el-tooltip v-if="!content" effect="dark" :content="fullscreenTips" placement="bottom">
      <SvgIcon :name="fullscreenSvgName" @click="handleFullscreenClick" />
    </el-tooltip>
    <!-- Content area -->
    <el-dropdown v-else :disabled="isFullscreen">
      <SvgIcon :name="contentLargeSvgName" />
      <template #dropdown>
        <el-dropdown-menu>
          <!-- Enlarge content area -->
          <el-dropdown-item @click="handleContentLargeClick">{{ contentLargeTips }}</el-dropdown-item>
          <!-- Fullscreen content area -->
          <el-dropdown-item @click="handleContentFullClick">Fullscreen Content Area</el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </div>
</template>

<style lang="scss" scoped>
.svg-icon {
  font-size: 20px;
  &:focus {
    outline: none;
  }
}
</style>

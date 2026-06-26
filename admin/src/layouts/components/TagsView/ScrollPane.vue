<script lang="ts" setup>
import { ref, nextTick } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { useSettingsStore } from "@/store/modules/settings"
import { useRouteListener } from "@/hooks/useRouteListener"
import Screenfull from "@/components/Screenfull/index.vue"
import { ElScrollbar } from "element-plus"
import { ArrowLeft, ArrowRight } from "@element-plus/icons-vue"

interface Props {
  tagRefs: InstanceType<typeof RouterLink>[]
}

const props = defineProps<Props>()

const route = useRoute()
const settingsStore = useSettingsStore()
const { listenerRouteChange } = useRouteListener()

/** Reference to scrollbar component element */
const scrollbarRef = ref<InstanceType<typeof ElScrollbar>>()
/** Reference to scrollbar content element */
const scrollbarContentRef = ref<HTMLDivElement>()

/** Current scrollbar distance from left */
let currentScrollLeft = 0
/** Distance for each scroll */
const translateDistance = 200

/** Triggered when scrolling */
const scroll = ({ scrollLeft }: { scrollLeft: number }) => {
  currentScrollLeft = scrollLeft
}

/** Triggered when mouse wheel scrolls */
const wheelScroll = ({ deltaY }: WheelEvent) => {
  if (/^-/.test(deltaY.toString())) {
    scrollTo("left")
  } else {
    scrollTo("right")
  }
}

/** Get potentially needed widths */
const getWidth = () => {
  /** Length of scrollable content */
  const scrollbarContentRefWidth = scrollbarContentRef.value!.clientWidth
  /** Scroll viewport width */
  const scrollbarRefWidth = scrollbarRef.value!.wrapRef!.clientWidth
  /** Last remaining scrollable width */
  const lastDistance = scrollbarContentRefWidth - scrollbarRefWidth - currentScrollLeft

  return { scrollbarContentRefWidth, scrollbarRefWidth, lastDistance }
}

/** Scroll left or right */
const scrollTo = (direction: "left" | "right", distance: number = translateDistance) => {
  let scrollLeft = 0
  const { scrollbarContentRefWidth, scrollbarRefWidth, lastDistance } = getWidth()
  // No horizontal scrollbar, end directly
  if (scrollbarRefWidth > scrollbarContentRefWidth) return
  if (direction === "left") {
    scrollLeft = Math.max(0, currentScrollLeft - distance)
  } else {
    scrollLeft = Math.min(currentScrollLeft + distance, currentScrollLeft + lastDistance)
  }
  scrollbarRef.value!.setScrollLeft(scrollLeft)
}

/** Move to target position */
const moveTo = () => {
  const tagRefs = props.tagRefs
  for (let i = 0; i < tagRefs.length; i++) {
    // @ts-ignore
    if (route.path === tagRefs[i].$props.to.path) {
      // @ts-ignore
      const el: HTMLElement = tagRefs[i].$el
      const offsetWidth = el.offsetWidth
      const offsetLeft = el.offsetLeft
      const { scrollbarRefWidth } = getWidth()
      // When current tag is to the left of visible area
      if (offsetLeft < currentScrollLeft) {
        const distance = currentScrollLeft - offsetLeft
        scrollTo("left", distance)
        return
      }
      // When current tag is to the right of visible area
      const width = scrollbarRefWidth + currentScrollLeft - offsetWidth
      if (offsetLeft > width) {
        const distance = offsetLeft - width
        scrollTo("right", distance)
        return
      }
    }
  }
}

/** Listen to route changes and move to target position */
listenerRouteChange(() => {
  nextTick(moveTo)
})
</script>

<template>
  <div class="scroll-container">
    <el-icon class="arrow left" @click="scrollTo('left')">
      <ArrowLeft />
    </el-icon>
    <el-scrollbar ref="scrollbarRef" @wheel.passive="wheelScroll" @scroll="scroll">
      <div ref="scrollbarContentRef" class="scrollbar-content">
        <slot />
      </div>
    </el-scrollbar>
    <el-icon class="arrow right" @click="scrollTo('right')">
      <ArrowRight />
    </el-icon>
    <!-- <Screenfull v-if="settingsStore.showScreenfull" :content="true" class="screenfull" /> -->
  </div>
</template>

<style lang="scss" scoped>
.scroll-container {
  height: 100%;
  user-select: none;
  display: flex;
  justify-content: space-between;
  .arrow {
    width: 40px;
    height: 100%;
    font-size: 18px;
    cursor: pointer;
    &.left {
      box-shadow: 5px 0 5px -6px var(--el-border-color-darker);
    }
    &.right {
      box-shadow: -5px 0 5px -6px var(--el-border-color-darker);
    }
  }
  .el-scrollbar {
    flex: 1;
    // 防止换行（超出宽度时，显示滚动条）
    white-space: nowrap;
    .scrollbar-content {
      display: inline-block;
    }
  }
  .screenfull {
    width: 40px;
    display: flex;
    justify-content: center;
    align-items: center;
    cursor: pointer;
  }
}
</style>

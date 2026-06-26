<script lang="ts" setup>
import { getCurrentInstance, onBeforeMount, onBeforeUnmount, onMounted, ref } from "vue"
import { type RouteRecordName, type RouteRecordRaw } from "vue-router"

interface Props {
  list: RouteRecordRaw[]
  isPressUpOrDown: boolean
}

/** Selected menu */
const modelValue = defineModel<RouteRecordName | undefined>({ required: true })
const props = defineProps<Props>()

const instance = getCurrentInstance()
const scrollbarHeight = ref<number>(0)

/** Menu style */
const itemStyle = (item: RouteRecordRaw) => {
  const flag = item.name === modelValue.value
  return {
    background: flag ? "var(--el-color-primary)" : "",
    color: flag ? "#ffffff" : ""
  }
}

/** Mouse enter */
const handleMouseenter = (item: RouteRecordRaw) => {
  // If up/down key and mouseenter event both take effect, prioritize up/down key and do not execute assignment logic of this function
  if (props.isPressUpOrDown) return
  modelValue.value = item.name
}

/** Calculate scrollbar visible area height */
const getScrollbarHeight = () => {
  // el-scrollbar max-height="40vh"
  scrollbarHeight.value = Number((window.innerHeight * 0.4).toFixed(1))
}

/** Calculate distance to top based on index */
const getScrollTop = (index: number) => {
  const currentInstance = instance?.proxy?.$refs[`resultItemRef${index}`] as HTMLDivElement[]
  if (!currentInstance) return 0
  const currentRef = currentInstance[0]
  const scrollTop = currentRef.offsetTop + 128 // 128 = sum of two result-item (56 + 56 = 112) height and top/bottom margin (8 + 8 = 16) size
  return scrollTop > scrollbarHeight.value ? scrollTop - scrollbarHeight.value : 0
}

/** Add window resize event listener before component mount */
onBeforeMount(() => {
  window.addEventListener("resize", getScrollbarHeight)
})

/** Calculate scrollbar visible area height immediately when component mounts */
onMounted(() => {
  getScrollbarHeight()
})

/** Remove window resize event listener before component unmount */
onBeforeUnmount(() => {
  window.removeEventListener("resize", getScrollbarHeight)
})

defineExpose({ getScrollTop })
</script>

<template>
  <!-- Outer div cannot be deleted, it is used to receive parent component click event -->
  <div>
    <div
      v-for="(item, index) in list"
      :key="index"
      :ref="`resultItemRef${index}`"
      class="result-item"
      :style="itemStyle(item)"
      @mouseenter="handleMouseenter(item)"
    >
      <SvgIcon v-if="item.meta?.svgIcon" :name="item.meta.svgIcon" />
      <component v-else-if="item.meta?.elIcon" :is="item.meta.elIcon" class="el-icon" />
      <span class="result-item-title">
        {{ item.meta?.title }}
      </span>
      <SvgIcon v-if="modelValue && modelValue === item.name" name="keyboard-enter" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.result-item {
  display: flex;
  align-items: center;
  height: 56px;
  padding: 0 15px;
  margin-top: 8px;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  cursor: pointer;
  .svg-icon {
    min-width: 1em;
    font-size: 18px;
  }
  .el-icon {
    width: 1em;
    font-size: 18px;
  }
  &-title {
    flex: 1;
    margin-left: 12px;
  }
}
</style>

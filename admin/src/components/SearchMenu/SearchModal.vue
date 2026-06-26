<script lang="ts" setup>
import { computed, ref, shallowRef } from "vue"
import { type RouteRecordName, type RouteRecordRaw, useRouter } from "vue-router"
import { usePermissionStore } from "@/store/modules/permission"
import SearchResult from "./SearchResult.vue"
import SearchFooter from "./SearchFooter.vue"
import { ElMessage, ElScrollbar } from "element-plus"
import { cloneDeep, debounce } from "lodash-es"
import { useDevice } from "@/hooks/useDevice"
import { isExternal } from "@/utils/validate"

/** Control modal visibility */
const modelValue = defineModel<boolean>({ required: true })

const router = useRouter()
const { isMobile } = useDevice()

const inputRef = ref<HTMLInputElement | null>(null)
const scrollbarRef = ref<InstanceType<typeof ElScrollbar> | null>(null)
const searchResultRef = ref<InstanceType<typeof SearchResult> | null>(null)

const keyword = ref<string>("")
const resultList = shallowRef<RouteRecordRaw[]>([])
const activeRouteName = ref<RouteRecordName | undefined>(undefined)
/** Whether up or down key is pressed (to resolve conflicts with mouseenter event) */
const isPressUpOrDown = ref<boolean>(false)

/** Control search dialog width */
const modalWidth = computed(() => (isMobile.value ? "80vw" : "40vw"))
/** Tree menu */
const menusData = computed(() => cloneDeep(usePermissionStore().routes))

/** Search (debounced) */
const handleSearch = debounce(() => {
  const flatMenusData = flatTree(menusData.value)
  resultList.value = flatMenusData.filter((menu) =>
    keyword.value ? menu.meta?.title?.toLocaleLowerCase().includes(keyword.value.toLocaleLowerCase().trim()) : false
  )
  // Select first search result by default
  const length = resultList.value?.length
  activeRouteName.value = length > 0 ? resultList.value[0].name : undefined
}, 500)

/** Flatten tree menu into one-dimensional array for menu search */
const flatTree = (arr: RouteRecordRaw[], result: RouteRecordRaw[] = []) => {
  arr.forEach((item) => {
    result.push(item)
    item.children && flatTree(item.children, result)
  })
  return result
}

/** Close search dialog */
const handleClose = () => {
  modelValue.value = false
  // Delayed processing to prevent users from seeing data reset operation
  setTimeout(() => {
    keyword.value = ""
    resultList.value = []
  }, 200)
}

/** Scroll based on index position */
const scrollTo = (index: number) => {
  if (!searchResultRef.value) return
  const scrollTop = searchResultRef.value.getScrollTop(index)
  // Manually control el-scrollbar scrolling, set distance from scrollbar to top
  scrollbarRef.value?.setScrollTop(scrollTop)
}

/** Keyboard up key */
const handleUp = () => {
  isPressUpOrDown.value = true
  const { length } = resultList.value
  if (length === 0) return
  // Get the first occurrence position of this name in the menu
  const index = resultList.value.findIndex((item) => item.name === activeRouteName.value)
  // If already at the top
  if (index === 0) {
    const bottomName = resultList.value[length - 1].name
    // If top and bottom bottomName are the same and length is greater than 1, jump one more position (to solve the problem of up key not working when encountering two same names at the beginning and end)
    if (activeRouteName.value === bottomName && length > 1) {
      activeRouteName.value = resultList.value[length - 2].name
      scrollTo(length - 2)
    } else {
      // Jump to bottom
      activeRouteName.value = bottomName
      scrollTo(length - 1)
    }
  } else {
    activeRouteName.value = resultList.value[index - 1].name
    scrollTo(index - 1)
  }
}

/** Keyboard down key */
const handleDown = () => {
  isPressUpOrDown.value = true
  const { length } = resultList.value
  if (length === 0) return
  // Get the last occurrence position of this name in the menu (to solve the problem of down key not working when encountering two consecutive same names)
  const index = resultList.value.map((item) => item.name).lastIndexOf(activeRouteName.value)
  // If already at the bottom
  if (index === length - 1) {
    const topName = resultList.value[0].name
    // If bottom and top topName are the same and length is greater than 1, jump one more position (to solve the problem of down key not working when encountering two same names at the beginning and end)
    if (activeRouteName.value === topName && length > 1) {
      activeRouteName.value = resultList.value[1].name
      scrollTo(1)
    } else {
      // Jump to top
      activeRouteName.value = topName
      scrollTo(0)
    }
  } else {
    activeRouteName.value = resultList.value[index + 1].name
    scrollTo(index + 1)
  }
}

/** Keyboard enter key */
const handleEnter = () => {
  const { length } = resultList.value
  if (length === 0) return
  const name = activeRouteName.value
  const path = resultList.value.find((item) => item.name === name)?.path
  if (path && isExternal(path)) {
    window.open(path, "_blank", "noopener, noreferrer")
    return
  }
  if (!name) {
    ElMessage.warning("Cannot enter this menu through search, please set a unique Name for the corresponding route")
    return
  }
  try {
    router.push({ name })
  } catch {
    ElMessage.error("This menu has required dynamic parameters and cannot be entered through search")
    return
  }
  handleClose()
}

/** Release up or down key */
const handleReleaseUpOrDown = () => {
  isPressUpOrDown.value = false
}
</script>

<template>
  <el-dialog
    v-model="modelValue"
    @opened="inputRef?.focus()"
    @closed="inputRef?.blur()"
    @keydown.up="handleUp"
    @keydown.down="handleDown"
    @keydown.enter="handleEnter"
    @keyup.up.down="handleReleaseUpOrDown"
    :before-close="handleClose"
    :width="modalWidth"
    top="5vh"
    class="search-modal__private"
    append-to-body
  >
    <el-input ref="inputRef" v-model="keyword" @input="handleSearch" placeholder="Search Menu" size="large" clearable>
      <template #prefix>
        <SvgIcon name="search" />
      </template>
    </el-input>
    <el-empty v-if="resultList.length === 0" description="No search results" :image-size="100" />
    <template v-else>
      <p>Search Results</p>
      <el-scrollbar ref="scrollbarRef" max-height="40vh" always>
        <SearchResult
          ref="searchResultRef"
          v-model="activeRouteName"
          :list="resultList"
          :isPressUpOrDown="isPressUpOrDown"
          @click="handleEnter"
        />
      </el-scrollbar>
    </template>
    <template #footer>
      <SearchFooter :total="resultList.length" />
    </template>
  </el-dialog>
</template>

<style lang="scss">
.search-modal__private {
  .svg-icon {
    font-size: 18px;
  }
  .el-dialog__header {
    display: none;
  }
  .el-dialog__footer {
    border-top: 1px solid var(--el-border-color);
    padding: var(--el-dialog-padding-primary);
  }
}
</style>

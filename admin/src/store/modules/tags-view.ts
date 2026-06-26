import { ref, watchEffect } from "vue"
import { defineStore } from "pinia"
import { useSettingsStore } from "./settings"
import { type RouteLocationNormalized } from "vue-router"
import { getVisitedViews, setVisitedViews, getCachedViews, setCachedViews } from "@/utils/cache/local-storage"

export type TagView = Partial<RouteLocationNormalized>

export const useTagsViewStore = defineStore("tags-view", () => {
  const { cacheTagsView } = useSettingsStore()
  const visitedViews = ref<TagView[]>(cacheTagsView ? getVisitedViews() : [])
  const cachedViews = ref<string[]>(cacheTagsView ? getCachedViews() : [])

  /** Cache tags view data */
  watchEffect(() => {
    setVisitedViews(visitedViews.value)
    setCachedViews(cachedViews.value)
  })

  //#region add
  const addVisitedView = (view: TagView) => {
    // Check if the same visitedView already exists
    const index = visitedViews.value.findIndex((v) => v.path === view.path)
    if (index !== -1) {
      // Prevent query parameters from being lost
      visitedViews.value[index].fullPath !== view.fullPath && (visitedViews.value[index] = { ...view })
    } else {
      // Add new visitedView
      visitedViews.value.push({ ...view })
    }
  }

  const addCachedView = (view: TagView) => {
    if (typeof view.name !== "string") return
    if (cachedViews.value.includes(view.name)) return
    if (view.meta?.keepAlive) cachedViews.value.push(view.name)
  }
  //#endregion

  //#region del
  const delVisitedView = (view: TagView) => {
    const index = visitedViews.value.findIndex((v) => v.path === view.path)
    if (index !== -1) visitedViews.value.splice(index, 1)
  }

  const delCachedView = (view: TagView) => {
    if (typeof view.name !== "string") return
    const index = cachedViews.value.indexOf(view.name)
    if (index !== -1) cachedViews.value.splice(index, 1)
  }
  //#endregion

  //#region delOthers
  const delOthersVisitedViews = (view: TagView) => {
    visitedViews.value = visitedViews.value.filter((v) => {
      return v.meta?.affix || v.path === view.path
    })
  }

  const delOthersCachedViews = (view: TagView) => {
    if (typeof view.name !== "string") return
    const index = cachedViews.value.indexOf(view.name)
    if (index !== -1) {
      cachedViews.value = cachedViews.value.slice(index, index + 1)
    } else {
      // If index = -1, no cached tags
      cachedViews.value = []
    }
  }
  //#endregion

  //#region delAll
  const delAllVisitedViews = () => {
    // Keep pinned tags
    visitedViews.value = visitedViews.value.filter((tag) => tag.meta?.affix)
  }

  const delAllCachedViews = () => {
    cachedViews.value = []
  }
  //#endregion

  return {
    visitedViews,
    cachedViews,
    addVisitedView,
    addCachedView,
    delVisitedView,
    delCachedView,
    delOthersVisitedViews,
    delOthersCachedViews,
    delAllVisitedViews,
    delAllCachedViews
  }
})

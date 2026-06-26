import { onBeforeMount, onMounted, onBeforeUnmount } from "vue"
import { useAppStore } from "@/store/modules/app"
import { useRouteListener } from "@/hooks/useRouteListener"
import { DeviceEnum } from "@/constants/app-key"

/** Reference Bootstrap's responsive design, set maximum mobile width to 992 */
const MAX_MOBILE_WIDTH = 992

/** Change Layout based on browser width changes */
export default () => {
  const appStore = useAppStore()
  const { listenerRouteChange } = useRouteListener()

  /** Check if current device is mobile */
  const _isMobile = () => {
    const rect = document.body.getBoundingClientRect()
    return rect.width - 1 < MAX_MOBILE_WIDTH
  }

  /** Handle window resize events */
  const _resizeHandler = () => {
    if (!document.hidden) {
      const isMobile = _isMobile()
      appStore.toggleDevice(isMobile ? DeviceEnum.Mobile : DeviceEnum.Desktop)
      isMobile && appStore.closeSidebar(true)
    }
  }
  /** Listen to route changes and adjust layout based on device type */
  listenerRouteChange(() => {
    if (appStore.device === DeviceEnum.Mobile && appStore.sidebar.opened) {
      appStore.closeSidebar(false)
    }
  })

  /** Add window resize event listener before component mount */
  onBeforeMount(() => {
    window.addEventListener("resize", _resizeHandler)
  })

  /** Determine device type and adjust layout based on window size after component mount */
  onMounted(() => {
    if (_isMobile()) {
      appStore.toggleDevice(DeviceEnum.Mobile)
      appStore.closeSidebar(true)
    }
  })

  /** Remove window resize event listener before component unmount */
  onBeforeUnmount(() => {
    window.removeEventListener("resize", _resizeHandler)
  })
}

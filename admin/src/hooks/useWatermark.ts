import { type Ref, onBeforeUnmount, ref } from "vue"
import { debounce } from "lodash-es"

type Observer = {
  watermarkElMutationObserver?: MutationObserver
  parentElMutationObserver?: MutationObserver
  parentElResizeObserver?: ResizeObserver
}

type DefaultConfig = typeof defaultConfig

/** Default configuration */
const defaultConfig = {
  /** Defense (enabled by default, can prevent watermark from being deleted or hidden, but may have performance impact) */
  defense: true,
  /** Text color */
  color: "#c0c4cc",
  /** Text opacity */
  opacity: 0.5,
  /** Text font size */
  size: 16,
  /** Text font family */
  family: "serif",
  /** Text rotation angle */
  angle: -20,
  /** Width occupied by one watermark (larger value means lower density) */
  width: 300,
  /** Height occupied by one watermark (larger value means lower density) */
  height: 200
}

/** body element */
const bodyEl = ref<HTMLElement>(document.body)

/**
 * Create watermark
 * 1. Can optionally pass a container element to mount the watermark, defaults to body
 * 2. Implements watermark defense to effectively prevent users from deleting or hiding the watermark via console
 */
export function useWatermark(parentEl: Ref<HTMLElement | null> = bodyEl) {
  /** Backup text */
  let backupText: string
  /** Final configuration */
  let mergeConfig: DefaultConfig
  /** Watermark element */
  let watermarkEl: HTMLElement | null = null
  /** Observers */
  const observer: Observer = {
    watermarkElMutationObserver: undefined,
    parentElMutationObserver: undefined,
    parentElResizeObserver: undefined
  }

  /** Set watermark */
  const setWatermark = (text: string, config: Partial<DefaultConfig> = {}) => {
    if (!parentEl.value) {
      console.warn("Please call setWatermark method after DOM is mounted")
      return
    }
    // Backup text
    backupText = text
    // Merge configuration
    mergeConfig = { ...defaultConfig, ...config }
    // Create or update watermark element
    watermarkEl ? updateWatermarkEl() : createWatermarkEl()
    // Listen to watermark element and container element changes
    addElListener(parentEl.value)
  }

  /** Create watermark element */
  const createWatermarkEl = () => {
    const isBody = parentEl.value!.tagName.toLowerCase() === bodyEl.value.tagName.toLowerCase()
    const watermarkElPosition = isBody ? "fixed" : "absolute"
    const parentElPosition = isBody ? "" : "relative"
    watermarkEl = document.createElement("div")
    watermarkEl.style.pointerEvents = "none"
    watermarkEl.style.top = "0"
    watermarkEl.style.left = "0"
    watermarkEl.style.position = watermarkElPosition
    watermarkEl.style.zIndex = "99999"
    const { clientWidth, clientHeight } = parentEl.value!
    updateWatermarkEl({ width: clientWidth, height: clientHeight })
    // Set watermark container to relative positioning
    parentEl.value!.style.position = parentElPosition
    // Add watermark element to watermark container
    parentEl.value!.appendChild(watermarkEl)
  }

  /** Update watermark element */
  const updateWatermarkEl = (
    options: Partial<{
      width: number
      height: number
    }> = {}
  ) => {
    if (!watermarkEl) return
    backupText && (watermarkEl.style.background = `url(${createBase64()}) left top repeat`)
    options.width && (watermarkEl.style.width = `${options.width}px`)
    options.height && (watermarkEl.style.height = `${options.height}px`)
  }

  /** Create base64 image */
  const createBase64 = () => {
    const { color, opacity, size, family, angle, width, height } = mergeConfig
    const canvasEl = document.createElement("canvas")
    canvasEl.width = width
    canvasEl.height = height
    const ctx = canvasEl.getContext("2d")
    if (ctx) {
      ctx.fillStyle = color
      ctx.globalAlpha = opacity
      ctx.font = `${size}px ${family}`
      ctx.rotate((Math.PI / 180) * angle)
      ctx.fillText(backupText, 0, height / 2)
    }
    return canvasEl.toDataURL()
  }

  /** Clear watermark */
  const clearWatermark = () => {
    if (!parentEl.value || !watermarkEl) return
    // Remove listeners on watermark element and container element
    removeListener()
    // Remove watermark element
    try {
      parentEl.value.removeChild(watermarkEl)
    } catch {
      // For example, when there's no defense and user deletes the element via console
      console.warn("Watermark element no longer exists, please recreate")
    } finally {
      watermarkEl = null
    }
  }

  /** Refresh watermark (called when defense is active) */
  const updateWatermark = debounce(() => {
    clearWatermark()
    createWatermarkEl()
    addElListener(parentEl.value!)
  }, 100)

  /** Listen to watermark element and container element changes (DOM changes & DOM size changes) */
  const addElListener = (targetNode: HTMLElement) => {
    // Check if defense is enabled
    if (mergeConfig.defense) {
      // Prevent duplicate listener additions
      if (!observer.watermarkElMutationObserver && !observer.parentElMutationObserver) {
        // Listen to DOM changes
        addMutationListener(targetNode)
      }
    } else {
      // No mutation listener needed when defense is disabled
      removeListener("mutation")
    }
    // Prevent duplicate listener additions
    if (!observer.parentElResizeObserver) {
      // Listen to DOM size changes
      addResizeListener(targetNode)
    }
  }

  /** Remove listeners on watermark element and container element, can specify which listener to remove, defaults to removing all */
  const removeListener = (kind: "mutation" | "resize" | "all" = "all") => {
    // Remove mutation listeners
    if (kind === "mutation" || kind === "all") {
      observer.watermarkElMutationObserver?.disconnect()
      observer.watermarkElMutationObserver = undefined
      observer.parentElMutationObserver?.disconnect()
      observer.parentElMutationObserver = undefined
    }
    // Remove resize listeners
    if (kind === "resize" || kind === "all") {
      observer.parentElResizeObserver?.disconnect()
      observer.parentElResizeObserver = undefined
    }
  }

  /** Listen to DOM changes */
  const addMutationListener = (targetNode: HTMLElement) => {
    // Callback executed when mutations are observed
    const mutationCallback = debounce((mutationList: MutationRecord[]) => {
      // Watermark defense (prevent users from manually deleting watermark element or hiding watermark via CSS)
      mutationList.forEach(
        debounce((mutation: MutationRecord) => {
          switch (mutation.type) {
            case "attributes":
              mutation.target === watermarkEl && updateWatermark()
              break
            case "childList":
              mutation.removedNodes.forEach((item) => {
                item === watermarkEl && targetNode.appendChild(watermarkEl)
              })
              break
          }
        }, 100)
      )
    }, 100)
    // Create observer instances and pass in callbacks
    observer.watermarkElMutationObserver = new MutationObserver(mutationCallback)
    observer.parentElMutationObserver = new MutationObserver(mutationCallback)
    // Start observing target nodes with above configuration
    observer.watermarkElMutationObserver.observe(watermarkEl!, {
      // Observe whether target node attributes change, defaults to true
      attributes: true,
      // Observe whether child nodes are added or removed, defaults to false
      childList: false,
      // Whether to extend observation to all descendant nodes, defaults to false
      subtree: false
    })
    observer.parentElMutationObserver.observe(targetNode, {
      attributes: false,
      childList: true,
      subtree: false
    })
  }

  /** Listen to DOM size changes */
  const addResizeListener = (targetNode: HTMLElement) => {
    // Update entire watermark size when targetNode element size changes
    const resizeCallback = debounce(() => {
      const { clientWidth, clientHeight } = targetNode
      updateWatermarkEl({ width: clientWidth, height: clientHeight })
    }, 500)
    // Create an observer instance and pass in callback
    observer.parentElResizeObserver = new ResizeObserver(resizeCallback)
    // Start observing target node
    observer.parentElResizeObserver.observe(targetNode)
  }

  /** Remove watermark and all listeners before component unmount */
  onBeforeUnmount(() => {
    clearWatermark()
  })

  return { setWatermark, clearWatermark }
}

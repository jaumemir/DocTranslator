import { type VNode, cloneVNode, createVNode, defineComponent, h, KeepAlive } from "vue"
import { useRoute } from "vue-router"
import { useTagsViewStore } from "@/store/modules/tags-view"

interface CompConsumerProps {
  component: VNode
}

/** Define compMap object for storing route names and corresponding components */
const compMap = new Map<string, VNode>()

/**
 * CompConsumer component
 * Usage: Replace <keep-alive> tag and internal code with: <CompConsumer :component="Component" />
 * Advantages: When caching routes, only need to write route Name, no need to write component Name
 * Disadvantages: When route table has dynamic route matching (pointing to the same component), component reuse will occur (e.g., modifying /info/1 will also change /info/2)
 */
export const CompConsumer = defineComponent(
  (props: CompConsumerProps) => {
    const tagsViewStore = useTagsViewStore()
    const route = useRoute()
    return () => {
      // Get the passed component
      const component = props.component
      // Check if current route has name, if not, directly handle name removal
      if (!route.name) return component
      // Get current component name
      const compName = (component.type as any)?.name
      // Get current route name
      const routeName = route.name as string
      let Comp: VNode
      // Check if compMap already has the corresponding component
      if (compMap.has(routeName)) {
        // If exists, directly use the component for rendering
        Comp = compMap.get(routeName)!
      } else {
        // If not exists, clone the passed component and create a new component, add it to compMap
        const node = cloneVNode(component)
        if (compName && compName === routeName) {
          ;(node.type as any).name = `__${compName}__CUSTOM_NAME`
        }
        // @ts-expect-error this is VNode
        Comp = defineComponent({
          name: routeName,
          setup() {
            return () => node
          }
        })
        compMap.set(routeName, Comp)
      }
      // Use createVNode function to create a KeepAlive component and cache the corresponding component in cachedViews array
      return createVNode(
        KeepAlive,
        {
          include: tagsViewStore.cachedViews
        },
        {
          default: () => h(Comp)
        }
      )
    }
  },
  {
    name: "CompConsumer",
    props: ["component"]
  }
)

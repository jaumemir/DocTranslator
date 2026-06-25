import { type RouteRecordRaw, createRouter } from "vue-router"
import { history, flatMultiLevelRoutes } from "./helper"
import routeSettings from "@/config/route"

const Layouts = () => import("@/layouts/index.vue")

/**
 * Constant routes
 * Except for hidden pages like redirect/403/404/login, other pages should set Name attribute
 */
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: "/redirect",
    component: Layouts,
    meta: {
      hidden: true
    },
    children: [
      {
        path: ":path(.*)",
        component: () => import("@/views/redirect/index.vue")
      }
    ]
  },
  {
    path: "/403",
    component: () => import("@/views/error-page/403.vue"),
    meta: {
      hidden: true
    }
  },
  {
    path: "/404",
    component: () => import("@/views/error-page/404.vue"),
    meta: {
      hidden: true
    },
    alias: "/:pathMatch(.*)*"
  },
  {
    path: "/login",
    component: () => import("@/views/login/index.vue"),
    meta: {
      hidden: true
    }
  },

  {
    path: "/",
    component: Layouts,
    redirect: "/dashboard",
    children: [
      {
        path: "dashboard",
        component: () => import("@/views/dashboard/index.vue"),
        name: "Dashboard",
        meta: {
          title: "Dashboard",
          svgIcon: "dashboard",
          affix: true
        }
      }
    ]
  },
  {
    path: "/customer",
    component: Layouts,
    children: [
      {
        path: "",
        component: () => import("@/views/customer/index.vue"),
        name: "customer",
        meta: {
          title: "User Management",
          elIcon: "user",
          affix: true
        }
      }
    ]
  },
  {
    path: "/translate",
    component: Layouts,
    children: [
      {
        path: "",
        component: () => import("@/views/translate/index.vue"),
        name: "translate_list",
        meta: {
          title: "Translation Tasks",
          elIcon: "tickets",
          affix: true
        }
      }
    ]
  },
  {
    path: "/setting",
    component: Layouts,
    meta: {
      title: "System Settings",
      elIcon: "setting",
      affix: true
    },
    children: [
      {
        path: "api",
        component: () => import("@/views/setting/api.vue"),
        name: "setting_api",
        meta: {
          title: "API Settings",
          elIcon: "key",
          affix: true
        }
      },

      {
        path: "password",
        component: () => import("@/views/password/index.vue"),
        name: "ChangePassword",
        meta: {
          title: "Change Password",
          elIcon: "lock",
          affix: true
        }
      },
      {
        path: "file-storage",
        component: () => import("@/views/setting/file.vue"),
        name: "FileStorage",
        meta: {
          title: "File Storage Management",
          elIcon: "files",
          affix: true
        }
      },
      {
        path: "mcp",
        component: () => import("@/views/setting/mcp.vue"),
        name: "McpSetting",
        meta: {
          title: "MCP Management",
          elIcon: "connection",
          affix: true
        }
      },
            {
        path: "other",
        component: () => import("@/views/setting/other.vue"),
        name: "setting_other",
        meta: {
          title: "Other Settings",
          elIcon: "tools",
          affix: true
        }
      },
      {
        path: "site",
        component: () => import("@/views/setting/site.vue"),
        name: "setting_site",
        meta: {
          title: "Site Settings",
          elIcon: "setting",
          affix: true
        }
      },
    ]
  }
]

/**
 * Dynamic routes
 * Used for routes with permissions (Roles attribute)
 * Must have Name attribute
 */
export const dynamicRoutes: RouteRecordRaw[] = []

const router = createRouter({
  history,
  routes: routeSettings.thirdLevelRouteCache ? flatMultiLevelRoutes(constantRoutes) : constantRoutes
})
console.log(routeSettings.thirdLevelRouteCache ? flatMultiLevelRoutes(constantRoutes) : constantRoutes)
/** Reset router */
export function resetRouter() {
  // Note: All dynamic routes must have Name attribute, otherwise they may not be completely reset
  try {
    router.getRoutes().forEach((route) => {
      const { name, meta } = route
      if (name && meta.roles?.length) {
        router.hasRoute(name) && router.removeRoute(name)
      }
    })
  } catch {
    // Force refresh browser is also acceptable, but user experience is not great
    window.location.reload()
  }
}

export default router

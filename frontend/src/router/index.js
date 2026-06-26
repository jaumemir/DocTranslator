import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/pages/layout/index.vue'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
// Configure routes
const constantRoute = [
  {
    path: '/',
    component: Layout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '/',
        component: () => import('@/pages/trans/index.vue'),
        name: 'home',
        meta: {
          title: 'Home',
          noCache: true,

        }
      },
      {
        path: '/profile',
        component: () => import('@/pages/profile/index.vue'),
        name: 'profile',
        meta: {
          title: 'Profile',
          noCache: true,
          requiresAuth: true
        }
      }
    ]
  },
  {
    path: '/corpus',
    component: Layout,
    redirect: '/corpus/index', // Redirect
    meta: { requiresAuth: true },
    children: [
      {
        path: 'index',
        component: () => import('@/pages/corpus/index.vue'),
        name: 'corpus',
        meta: {
          title: 'Corpus',
          noCache: true
        }
      },
      {
        path: 'square',
        component: () => import('@/pages/corpus/square.vue'),
        name: 'square',
        meta: {
          title: 'Public',
          noCache: true
        }
      }
    ]
  },
  // Login/Registration
  {
    path: '/login',
    name: 'login',
    meta: { guestOnly: true },
    component: () => import('@/pages/login/index.vue')
  },
  // Reset password
  {
    path: '/password',
    name: 'password',
    meta: { requiresAuth: true },
    component: () => import('@/pages/password/index.vue')
  },

  // 404 route, placed at the end
  {
    path: '/404',
    name: '404',
    component: () => import('@/components/notFound.vue'),
    hidden: true
  },
  {
    path: '/:pathMatch(.*)',
    redirect: '/404',
    hidden: true
  }
]

// Create router
let router = createRouter({
  history: createWebHistory(),
  routes: constantRoute
})

// Add global before guard
// Route interception logic
router.beforeEach((to) => {
  const userStore = useUserStore()
  // Check if login is required
  if (to.meta.requiresAuth) {
    // Not logged in
    if (!userStore.token) {
      // Redirect to login page with original path
      return {
        name: 'login',
        query: {
          redirect: to.fullPath // Save original target path
        }
      }
    }
  }

  // Logged-in users accessing login page
  // if (to.name === 'login' && userStore.token) {
  //   ElMessage.warning('You are already logged in')
  //   return '/' // Redirect to homepage
  // }
  // Otherwise allow passage
  return true
})

export default router

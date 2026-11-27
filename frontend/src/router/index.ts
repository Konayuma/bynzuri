import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { adminRoutes } from './admin'
import axios from 'axios'
import { hasSession } from '@/services/api'

let userStore: ReturnType<typeof useUserStore> | null = null

function getUserStore() {
  if (!userStore) {
    userStore = useUserStore()
  }
  return userStore
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue')
  },
  {
    path: '/catalog',
    name: 'catalog',
    component: () => import('@/pages/catalog/CatalogPage.vue')
  },
  {
    path: '/product/:slug',
    name: 'product-detail',
    component: () => import('@/pages/product/ProductDetailPage.vue')
  },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/pages/checkout/CheckoutPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/order/confirmation/:id',
    name: 'order-confirmation',
    component: () => import('@/pages/order/OrderConfirmationPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/account',
    name: 'account',
    component: () => import('@/pages/account/AccountPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/account/orders',
    name: 'order-history',
    component: () => import('@/pages/order/OrderHistoryPage.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/session-unavailable',
    name: 'session-unavailable',
    component: () => import('@/pages/auth/SessionUnavailablePage.vue')
  },
  {
    path: '/auth/login',
    name: 'login',
    component: () => import('@/pages/auth/LoginPage.vue')
  },
  {
    path: '/auth/register',
    name: 'register',
    component: () => import('@/pages/auth/RegisterPage.vue')
  },
  {
    path: '/auth/forgot-password',
    name: 'forgot-password',
    component: () => import('@/pages/auth/ForgotPasswordPage.vue')
  },
  {
    path: '/auth/reset-password',
    name: 'reset-password',
    component: () => import('@/pages/auth/ResetPasswordPage.vue')
  },
  {
    path: '/auth/verify-email',
    name: 'verify-email',
    component: () => import('@/pages/auth/VerifyEmailPage.vue')
  },
  ...adminRoutes,
  {
    path: '/access-denied',
    name: 'access-denied',
    component: () => import('@/pages/AccessDeniedPage.vue')
  },
  {
    path: '/wishlist',
    name: 'wishlist',
    component: () => import('@/pages/WishlistPage.vue')
  },
  {
    path: '/help',
    name: 'help',
    component: () => import('@/pages/HelpPage.vue')
  },
  {
    path: '/privacy-policy',
    alias: '/privacy',
    name: 'privacy-policy',
    component: () => import('@/pages/PrivacyPolicyPage.vue')
  },
  {
    path: '/terms-of-service',
    alias: '/terms',
    name: 'terms-of-service',
    component: () => import('@/pages/TermsOfServicePage.vue')
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/pages/NotFoundPage.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) return { el: to.hash, top: 96 }
    return { top: 0 }
  }
})

router.beforeEach(async (to, from, next) => {
  const store = getUserStore()

  if (to.meta.requiresAuth) {
    const token = hasSession()
    if (!token) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
    if (!store.user || to.meta.requiresAdmin) {
      try {
        await store.fetchProfile()
      } catch (error) {
        if (!hasSession()) return next({ name: 'login', query: { redirect: to.fullPath, reason: 'expired' } })
        if (axios.isAxiosError(error) && error.response?.status === 403) return next({ name: 'access-denied' })
        return next({ name: 'session-unavailable', query: { redirect: to.fullPath } })
      }
    }
    if (!store.user) {
      return next({ name: 'login', query: { redirect: to.fullPath } })
    }
  }

  if (to.meta.requiresAdmin && !store.isAdmin) {
    return next({ name: 'access-denied' })
  }

  next()
})

export default router

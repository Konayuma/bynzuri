import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

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
    component: () => import('@/pages/checkout/CheckoutPage.vue')
  },
  {
    path: '/order/confirmation/:id',
    name: 'order-confirmation',
    component: () => import('@/pages/order/OrderConfirmationPage.vue')
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
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/pages/admin/AdminDashboardPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/products',
    name: 'admin-products',
    component: () => import('@/pages/admin/AdminProductsPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/orders',
    name: 'admin-orders',
    component: () => import('@/pages/admin/AdminOrdersPage.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router

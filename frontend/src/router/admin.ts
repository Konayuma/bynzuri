import type { RouteRecordRaw } from 'vue-router'

// All administration routes inherit the same authentication and staff checks.
export const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin',
    component: () => import('@/layouts/AdminRouteView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true, adminArea: true },
    children: [
      { path: '', name: 'admin-dashboard', component: () => import('@/pages/admin/AdminDashboardPage.vue') },
      { path: 'products', name: 'admin-products', component: () => import('@/pages/admin/AdminProductsPage.vue') },
      { path: 'orders', name: 'admin-orders', component: () => import('@/pages/admin/AdminOrdersPage.vue') },
      { path: 'delivery', name: 'admin-delivery', component: () => import('@/pages/admin/AdminDeliveryPage.vue') },
    ],
  },
]

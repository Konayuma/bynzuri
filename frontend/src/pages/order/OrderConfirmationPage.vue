<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { orderService } from '@/services/order.service'
import { CheckCircle } from '@lucide/vue'
import BaseButton from '@/components/base/BaseButton.vue'
import type { Order } from '@/types'

const route = useRoute()
const router = useRouter()
const order = ref<Order | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const id = route.params.id as string
    order.value = await orderService.getOrder(id)
  } catch {
    // order not found
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="max-w-lg mx-auto px-4 py-16 text-center">
    <div v-if="loading" class="space-y-4">
      <div class="w-16 h-16 rounded-full bg-primary/30 animate-pulse mx-auto" />
      <div class="h-6 w-48 bg-primary/30 rounded animate-pulse mx-auto" />
    </div>

    <template v-else-if="order">
      <div class="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center mx-auto mb-4">
        <CheckCircle class="w-8 h-8 text-success" />
      </div>
      <h1 class="font-heading text-2xl font-semibold text-dark mb-2">Order Confirmed!</h1>
      <p class="text-sm text-muted mb-2">
        Thank you for your order. Your order reference is
        <span class="font-medium text-dark">#{{ order.id.slice(0, 8).toUpperCase() }}</span>.
      </p>
      <p class="text-sm text-muted mb-6">
        We'll send a confirmation to your email and phone shortly. You can track your order status in your account.
      </p>

      <div class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] text-left mb-6">
        <div class="space-y-3">
          <div class="flex justify-between text-sm">
            <span class="text-muted">Order Reference</span>
            <span class="font-medium text-dark">{{ order.id.slice(0, 8).toUpperCase() }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Total</span>
            <span class="font-semibold text-dark">K{{ order.grand_total }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Payment</span>
            <span class="font-medium text-dark capitalize">{{ order.payment_method.replace('_', ' ') }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Status</span>
            <span class="text-gold font-medium capitalize">{{ order.status.replace('_', ' ') }}</span>
          </div>
          <p v-if="order.status === 'awaiting_payment'" class="text-xs text-muted mt-1">
            Complete your payment to confirm this order.
          </p>
        </div>
      </div>

      <div class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] text-left mb-6">
        <h3 class="text-sm font-semibold text-dark mb-3">What happens next?</h3>
        <div class="space-y-2 text-sm text-muted">
          <p v-if="order.status === 'awaiting_payment'">1. Complete your payment to confirm the order</p>
          <p v-else>1. Your payment has been received</p>
          <p>2. We'll prepare and package your items</p>
          <p>3. Your order will be dispatched for delivery</p>
        </div>
      </div>

      <BaseButton @click="router.push('/')">
        Continue Shopping
      </BaseButton>
    </template>

    <div v-else>
      <p class="text-muted mb-2">We couldn't find this order.</p>
      <p class="text-sm text-muted mb-4">It may take a moment to appear. Try refreshing, or check your order history.</p>
      <BaseButton class="mt-2" @click="router.push('/')">
        Go Home
      </BaseButton>
    </div>
  </div>
</template>

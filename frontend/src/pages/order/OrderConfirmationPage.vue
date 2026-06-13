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
      <p class="text-sm text-muted mb-6">
        Thank you for your order. We&apos;ll send you a confirmation shortly.
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
        </div>
      </div>

      <BaseButton @click="router.push('/')">
        Continue Shopping
      </BaseButton>
    </template>

    <div v-else>
      <p class="text-muted">Order not found</p>
      <BaseButton class="mt-4" @click="router.push('/')">
        Go Home
      </BaseButton>
    </div>
  </div>
</template>

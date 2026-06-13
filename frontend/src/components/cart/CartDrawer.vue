<script setup lang="ts">
import BaseDrawer from '@/components/base/BaseDrawer.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import { useCartStore } from '@/stores/cart'
import { Minus, Plus, Trash2 } from '@lucide/vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const cartStore = useCartStore()
const router = useRouter()

function handleCheckout() {
  emit('close')
  router.push('/checkout')
}
</script>

<template>
  <BaseDrawer :open="open" title="Shopping Cart" position="right" @close="emit('close')">
    <div v-if="cartStore.items.length === 0" class="flex flex-col items-center justify-center h-full px-4 text-center">
      <div class="w-16 h-16 rounded-full bg-primary/40 flex items-center justify-center mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" class="text-muted"><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"/><path d="M3 6h18"/><path d="M16 10a4 4 0 0 1-8 0"/></svg>
      </div>
      <p class="text-dark font-medium mb-1">Your cart is empty</p>
      <p class="text-sm text-muted mb-6">Add some products to get started</p>
      <BaseButton variant="outline" @click="emit('close')">
        Continue Shopping
      </BaseButton>
    </div>

    <div v-else class="flex flex-col h-full">
      <div class="flex-1 px-4 py-4 space-y-4 overflow-y-auto">
        <div
          v-for="item in cartStore.items"
          :key="item.id"
          class="flex gap-4 pb-4 border-b border-primary/20"
        >
          <div class="w-20 h-24 rounded-[14px] bg-primary/30 shrink-0 overflow-hidden">
            <img
              v-if="item.product.images?.[0]?.image"
              :src="item.product.images[0].image"
              :alt="item.product.title"
              class="w-full h-full object-cover"
            />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-sm font-medium text-dark truncate">{{ item.product.title }}</h3>
            <p class="text-sm font-semibold text-dark mt-1">K{{ item.product.price }}</p>
            <div class="flex items-center gap-2 mt-2">
              <button
                class="w-7 h-7 rounded-full border border-primary/40 flex items-center justify-center hover:bg-primary/30 transition-colors"
                @click="cartStore.updateQuantity(item.id, Math.max(1, item.quantity - 1))"
              >
                <Minus class="w-3 h-3" />
              </button>
              <span class="text-sm font-medium w-6 text-center">{{ item.quantity }}</span>
              <button
                class="w-7 h-7 rounded-full border border-primary/40 flex items-center justify-center hover:bg-primary/30 transition-colors"
                @click="cartStore.updateQuantity(item.id, item.quantity + 1)"
              >
                <Plus class="w-3 h-3" />
              </button>
            </div>
          </div>
          <div class="flex flex-col items-end justify-between">
            <p class="text-sm font-semibold text-dark">K{{ (parseFloat(item.product.price) * item.quantity).toFixed(2) }}</p>
            <button
              class="p-1 hover:text-red-500 transition-colors"
              @click="cartStore.removeItem(item.id)"
              aria-label="Remove item"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <div class="border-t border-primary/20 px-4 py-4 space-y-3 shrink-0">
        <div class="flex justify-between text-sm">
          <span class="text-muted">Subtotal</span>
          <span class="font-semibold text-dark">K{{ cartStore.subtotal }}</span>
        </div>
        <p class="text-xs text-muted">Delivery calculated at checkout</p>
        <BaseButton fullWidth @click="handleCheckout">
          Checkout
        </BaseButton>
        <button
          class="w-full text-sm text-muted hover:text-dark transition-colors text-center"
          @click="emit('close')"
        >
          Continue Shopping
        </button>
      </div>
    </div>
  </BaseDrawer>
</template>

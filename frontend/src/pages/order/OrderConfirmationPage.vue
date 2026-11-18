<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { orderService } from '@/services/order.service'
import { CheckCircle } from '@lucide/vue'
import BaseButton from '@/components/base/BaseButton.vue'
import type { Order } from '@/types'
import { paymentService, type Payment } from '@/services/payment.service'
import { isZambianPhone, normalizeZambianPhone } from '@/utils/formValidation'

const route = useRoute()
const router = useRouter()
const order = ref<Order | null>(null)
const loading = ref(true)
const payment = ref<Payment | null>(null)
const paymentLoading = ref(false)
const paymentError = ref('')
const paymentStatusChecked = ref(false)
const paymentPhone = ref('')
const paymentMethod = ref('mtn_momo')

async function checkPayment() {
  if (!order.value) return
  paymentLoading.value = true
  paymentError.value = ''
  paymentStatusChecked.value = false
  try {
    payment.value = await paymentService.getPaymentStatus(order.value.id)
    paymentStatusChecked.value = true
    order.value = await orderService.getOrder(order.value.id)
  } catch (e: unknown) {
    if ((e as { response?: { status?: number } }).response?.status === 404) { payment.value = null; paymentStatusChecked.value = true }
    else paymentError.value = 'Unable to check payment status. Please try again.'
  } finally { paymentLoading.value = false }
}

async function retryPayment() {
  if (!order.value) return
  if (!isZambianPhone(paymentPhone.value)) { paymentError.value = 'Enter a valid Zambian mobile number.'; return }
  paymentLoading.value = true
  paymentError.value = ''
  try {
    payment.value = await paymentService.initiatePayment(order.value.id, paymentMethod.value, normalizeZambianPhone(paymentPhone.value))
    if (payment.value.status === 'success') order.value = await orderService.getOrder(order.value.id)
  } catch (e: unknown) {
    paymentError.value = (e as { response?: { data?: { detail?: string } } }).response?.data?.detail || 'Could not start payment. Please try again.'
  } finally { paymentLoading.value = false }
}

onMounted(async () => {
  try {
    const id = route.params.id as string
    order.value = await orderService.getOrder(id)
    if (order.value.status === 'awaiting_payment') await checkPayment()
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
      <h1 class="font-heading text-2xl font-semibold text-dark mb-2">{{ order.status === 'awaiting_payment' ? 'Order awaiting payment' : 'Order details' }}</h1>
      <p class="text-sm text-muted mb-2">
        Thank you for your order. Your order reference is
        <span class="font-medium text-dark">#{{ order.id.slice(0, 8).toUpperCase() }}</span>.
      </p>
      <p class="text-sm text-muted mb-6">
        You can track your order status in your account.
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

      <div v-if="order.status === 'awaiting_payment'" class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] text-left mb-6 space-y-3">
        <h2 class="font-semibold text-dark">Mobile money payment</h2>
        <p v-if="payment && ['pending', 'processing'].includes(payment.status)" class="text-sm text-muted">Your payment is pending. Check your phone for the prompt, then check the status here.</p>
        <template v-else-if="paymentStatusChecked && !paymentLoading">
          <p class="text-sm text-muted">{{ payment?.status === 'failed' ? 'The previous payment failed. You can try again.' : 'Choose a network and enter your mobile money number.' }}</p>
          <label for="retry-method" class="block text-sm text-dark">Mobile money network</label>
          <select id="retry-method" v-model="paymentMethod" class="w-full rounded-xl border border-primary/40 p-3"><option value="mtn_momo">MTN Mobile Money</option><option value="airtel_money">Airtel Money</option></select>
          <label for="retry-phone" class="block text-sm text-dark">Mobile money number</label>
          <input id="retry-phone" v-model="paymentPhone" type="tel" autocomplete="tel" class="w-full rounded-xl border border-primary/40 p-3" placeholder="0971234567" />
          <BaseButton :loading="paymentLoading" @click="retryPayment">Request payment</BaseButton>
        </template>
        <p v-if="paymentLoading" role="status" class="text-sm text-muted">Checking payment status…</p>
        <p v-if="paymentError" role="alert" class="text-sm text-red-600">{{ paymentError }}</p>
        <button type="button" class="block text-sm underline text-dark" :disabled="paymentLoading" @click="checkPayment">Check payment status</button>
      </div>

      <div class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] text-left mb-6">
        <h3 class="text-sm font-semibold text-dark mb-3">What happens next?</h3>
        <div class="space-y-2 text-sm text-muted">
          <p v-if="order.status === 'awaiting_payment'">1. Complete your payment to confirm the order</p>
          <p v-else-if="['paid', 'processing', 'dispatched', 'delivered'].includes(order.status)">1. Your payment has been received</p>
          <p v-else>1. Check the status above for this order</p>
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

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { orderService } from '@/services/order.service'
import { CheckCircle } from '@lucide/vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
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
const printReceipt = () => window.print()
const paymentMethodOptions = [
  { value: 'mtn_momo', label: 'MTN Mobile Money' },
  { value: 'airtel_money', label: 'Airtel Money' },
]

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
    await checkPayment()
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

      <section v-if="payment?.status === 'success'" class="receipt bg-white rounded-[20px] p-6 text-left mb-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)]" aria-labelledby="receipt-title">
        <img src="/By%20Nzuri%20Vector%20Logo%20-01.svg" alt="By Nzuri" class="mx-auto h-40 w-64 max-w-full object-contain" />
        <div class="flex items-center justify-between gap-4 border-b border-primary/20 pb-4 mb-4">
          <h2 id="receipt-title" class="text-sm text-muted">Payment receipt</h2>
          <span class="text-sm font-medium text-success">Paid</span>
        </div>
        <div class="space-y-2 text-sm text-dark">
          <p>Order: {{ order.id }}</p>
          <p>Payment reference: {{ payment.lenco_reference || payment.transaction_reference || payment.id }}</p>
          <p>Payment initiated: {{ new Date(payment.created_at).toLocaleString() }}</p>
          <p>Method: {{ payment.method === 'mtn_momo' ? 'MTN Mobile Money' : payment.method === 'airtel_money' ? 'Airtel Money' : payment.method }}</p>
          <div class="border-t border-primary/20 pt-3 mt-3 space-y-2">
            <div v-for="item in order.items" :key="item.id" class="flex justify-between gap-4"><span>{{ item.product_title }} × {{ item.quantity }}</span><span>{{ payment.currency }} {{ (Number(item.price_at_purchase) * item.quantity).toFixed(2) }}</span></div>
            <div class="flex justify-between gap-4"><span>Delivery</span><span>{{ payment.currency }} {{ order.delivery_fee }}</span></div>
            <div class="flex justify-between gap-4 font-semibold border-t border-primary/20 pt-3"><span>Amount paid</span><span>{{ payment.currency }} {{ payment.amount }}</span></div>
          </div>
        </div>
        <button type="button" class="receipt-action mt-5 text-sm font-medium underline text-dark" @click="printReceipt">Print or save receipt as PDF</button>
      </section>

      <div v-if="order.status === 'awaiting_payment'" class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] text-left mb-6 space-y-3">
        <h2 class="font-semibold text-dark">Mobile money payment</h2>
        <p v-if="payment && ['pending', 'processing'].includes(payment.status)" class="text-sm text-muted">Your payment is pending. Check your phone for the prompt, then check the status here.</p>
        <template v-else-if="paymentStatusChecked && !paymentLoading">
          <p class="text-sm text-muted">{{ payment?.status === 'failed' ? 'The previous payment failed. You can try again.' : 'Choose a network and enter your mobile money number.' }}</p>
          <BaseSelect
            id="retry-method"
            v-model="paymentMethod"
            label="Mobile money network"
            :options="paymentMethodOptions"
          />
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

<style>
@media print {
  body * { visibility: hidden !important; }
  .receipt, .receipt * { visibility: visible !important; }
  .receipt { position: absolute; inset: 0 auto auto 0; width: 100%; box-shadow: none; }
  .receipt .receipt-action { display: none; }
}
</style>

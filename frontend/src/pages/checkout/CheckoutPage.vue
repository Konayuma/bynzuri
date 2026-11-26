<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { orderService } from '@/services/order.service'
import { addressService } from '@/services/address.service'
import { paymentService } from '@/services/payment.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import { ChevronLeft, ChevronRight, ChevronDown, MapPin, Loader2, CheckCircle2, XCircle, Smartphone, ShoppingBag } from '@lucide/vue'
import type { Province, Town, DeliveryMethod, Address, Order } from '@/types'
import { isEmail, isZambianPhone, isZambianMobileMoneyPhone, normalizeZambianPhone } from '@/utils/formValidation'
import { signatureImage } from '@/utils/productImage'
import { useDialogFocus } from '@/composables/useDialogFocus'

const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()
const loading = ref(false)
const currentStep = ref(1)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})

const paymentStatus = ref<'idle' | 'processing' | 'success' | 'failed' | 'unknown'>('idle')
const paymentOverlay = ref<HTMLElement | null>(null)
useDialogFocus(() => paymentStatus.value !== 'idle', paymentOverlay, () => {})
watch(paymentStatus, async (state, previous) => {
  if (state !== 'idle' && previous !== 'idle') {
    await nextTick()
    paymentOverlay.value?.focus()
  }
})
const paymentMessage = ref('')
const pendingKey = 'bynzuri_checkout_attempt'
const createdOrderId = ref<string | null>(null)
const createdOrder = ref<Order | null>(null)
const checkoutCartLoading = ref(true)
const orderLoadError = ref('')
let checkoutKey = ''
let paymentRun = 0
try {
  const saved = JSON.parse(sessionStorage.getItem(pendingKey) || 'null')
  if (saved?.userId === userStore.user?.id && typeof saved?.key === 'string') {
    checkoutKey = saved.key
    createdOrderId.value = saved.orderId || null
  }
} catch { /* Storage may be blocked; checkout will explain before placing an order. */ }

function saveCheckoutAttempt(orderId: string | null = null) {
  try {
    sessionStorage.setItem(pendingKey, JSON.stringify({ key: checkoutKey, orderId, userId: userStore.user?.id }))
    return true
  } catch { return false }
}
function clearCheckoutAttempt() { try { sessionStorage.removeItem(pendingKey) } catch { /* Storage is unavailable. */ } checkoutKey = '' }
function viewOrder() {
  paymentRun++
  if (createdOrderId.value) {
    clearCheckoutAttempt()
    cartStore.clearCart()
    router.push(`/order/confirmation/${createdOrderId.value}`)
  }
}

const provinces = ref<Province[]>([])
const towns = ref<Town[]>([])
const deliveryMethods = ref<DeliveryMethod[]>([])
const deliveryLoading = ref(false)
const deliveryError = ref('')
const savedAddresses = ref<Address[]>([])
const selectedAddressId = ref<string | null>(null)
const addressLoading = ref(false)
const addressSaving = ref(false)
const addressError = ref('')
const addressNotice = ref('')
const townsLoading = ref(false)
const townsError = ref('')
let townRequest = 0

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '260',
  province: '',
  town: '',
  street_address: '',
  delivery_method: '',
  payment_method: '',
  payment_phone: '260',
  notes: ''
})

const totalSteps = 4
const stepLabels = ['Details', 'Location', 'Delivery', 'Payment']
const mobileSummaryOpen = ref(false)

const stepTitle = computed(() => {
  const titles = ['', 'Your Details', 'Delivery Location', 'Delivery Method', 'Review & Pay']
  return titles[currentStep.value]
})

const summaryItems = computed(() => {
  if (createdOrder.value?.items?.length) {
    return createdOrder.value.items.map(item => ({
      id: item.id,
      title: item.product_title,
      quantity: item.quantity,
      lineTotal: (Number(item.price_at_purchase) * item.quantity).toFixed(2),
      image: '',
    }))
  }
  return cartStore.items.map(item => ({
    id: item.id,
    title: item.product.title,
    quantity: item.quantity,
    lineTotal: (Number(item.product.sale_price ?? item.product.price) * item.quantity).toFixed(2),
    image: item.product.images?.[0]?.image ?? signatureImage(item.product.slug) ?? '',
  }))
})

const summaryItemCount = computed(() =>
  summaryItems.value.reduce((sum, item) => sum + item.quantity, 0)
)

function goToStep(step: number) {
  if (step < currentStep.value && step >= 1) {
    currentStep.value = step
  }
}

const selectedDeliveryMethod = computed(() =>
  deliveryMethods.value.find(m => m.id === form.value.delivery_method)
)

const checkoutSubtotal = computed(() => createdOrder.value?.total_amount ?? cartStore.subtotal)
const checkoutDelivery = computed(() => createdOrder.value?.delivery_fee ?? selectedDeliveryMethod.value?.price ?? '0.00')
const grandTotal = computed(() => createdOrder.value?.grand_total ?? ((Number(cartStore.subtotal) || 0) + (Number(selectedDeliveryMethod.value?.price) || 0)).toFixed(2))

const isMobileMoney = computed(() =>
  ['mtn_momo', 'airtel_money'].includes(form.value.payment_method)
)

const operatorLabel = computed(() => {
  const labels: Record<string, string> = {
    mtn_momo: 'MTN',
    airtel_money: 'Airtel',
  }
  return labels[form.value.payment_method] || ''
})

function validateStep(step: number): boolean {
  const errors: Record<string, string> = {}
  const data = form.value
  if (step === 1) {
    if (!data.first_name.trim()) errors.first_name = 'Enter your first name.'
    if (!data.last_name.trim()) errors.last_name = 'Enter your last name.'
    if (!isEmail(data.email)) errors.email = 'Enter a valid email address.'
    if (!isZambianPhone(data.phone)) errors.phone = 'Enter a Zambian number, for example 0971234567 or +260971234567.'
  } else if (step === 2) {
    if (!data.province) errors.province = 'Select a province.'
    if (!data.town || !towns.value.some(t => t.id === data.town)) errors.town = 'Select a town in this province.'
    if (!data.street_address.trim()) errors.street_address = 'Enter a street address or landmark.'
  } else if (step === 3) {
    if (!deliveryMethods.value.some(m => m.id === data.delivery_method)) errors.delivery_method = 'Select a delivery method.'
  } else {
    if (!paymentMethods.some(m => m.value === data.payment_method)) errors.payment_method = 'Select a payment method.'
    if (isMobileMoney.value && !isZambianMobileMoneyPhone(data.payment_phone)) errors.payment_phone = 'Enter a valid Zambian mobile number, for example 0971234567 or +260971234567.'
  }
  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

function nextStep() {
  if (currentStep.value === 2 && townsLoading.value) { townsError.value = 'Please wait for towns to load.'; return }
  if (currentStep.value < totalSteps && validateStep(currentStep.value)) {
    error.value = ''
    currentStep.value++
  }
}
for (const key of Object.keys(form.value) as Array<keyof typeof form.value>) {
  watch(() => form.value[key], () => {
    delete fieldErrors.value[key]
    error.value = ''
  })
}

function prevStep() {
  if (currentStep.value > 1) currentStep.value--
}

async function handleProvinceChange(provinceId: string) {
  const request = ++townRequest
  form.value.province = provinceId
  form.value.town = ''
  selectedAddressId.value = null
  towns.value = []
  townsError.value = ''
  townsLoading.value = Boolean(provinceId)
  if (provinceId) {
    try {
      const result = await orderService.getTowns(provinceId)
      if (request === townRequest) towns.value = result
    } catch {
      if (request === townRequest) townsError.value = 'Could not load towns. Try again.'
    } finally {
      if (request === townRequest) townsLoading.value = false
    }
  }
}

async function selectSavedAddress(address: Address, applyPhone = true) {
  const request = ++townRequest
  selectedAddressId.value = address.id
  form.value.province = address.province
  form.value.town = ''
  form.value.street_address = address.street_address
  if (applyPhone && address.phone) {
    form.value.phone = address.phone
  }
  towns.value = []
  townsError.value = ''
  townsLoading.value = true
  try {
    const result = await orderService.getTowns(address.province)
    if (request !== townRequest) return
    towns.value = result
    if (result.some(town => town.id === address.town)) form.value.town = address.town
    else townsError.value = 'This saved town is no longer available. Please choose another town.'
  } catch {
    if (request === townRequest) townsError.value = 'Could not load towns for this address. Try again.'
  } finally {
    if (request === townRequest) townsLoading.value = false
  }
}

function useCustomAddress() {
  townRequest++
  townsLoading.value = false
  townsError.value = ''
  selectedAddressId.value = null
  form.value.province = ''
  form.value.town = ''
  form.value.street_address = ''
  towns.value = []
}

async function loadSavedAddresses() {
  addressLoading.value = true
  addressError.value = ''
  try { savedAddresses.value = await addressService.getAddresses() }
  catch { addressError.value = 'Could not load saved addresses. You can enter an address or try again.' }
  finally { addressLoading.value = false }
}

async function saveAddress() {
  if (addressSaving.value || townsLoading.value) return
  addressNotice.value = ''
  addressError.value = ''
  if (!validateStep(2)) return
  if (!isZambianPhone(form.value.phone)) { addressError.value = 'Enter a valid delivery phone number in Your Details first.'; return }
  const details = { province: form.value.province, town: form.value.town, street_address: form.value.street_address.trim(), phone: form.value.phone.trim() }
  const matches = (address: Address) => address.province === details.province && address.town === details.town && address.street_address.trim() === details.street_address && address.phone === details.phone
  addressSaving.value = true
  try {
    // Refresh first so a retry after a lost response does not create a duplicate.
    const existing = await addressService.getAddresses()
    const address = existing.find(matches) || await addressService.createAddress({ ...details, is_default: existing.length === 0 })
    savedAddresses.value = existing.some(item => item.id === address.id) ? existing : [...existing, address]
    selectedAddressId.value = address.id
    addressNotice.value = 'Delivery address saved to your account for next time.'
  } catch {
    addressError.value = 'We could not confirm whether the address was saved. Try again; your checkout details are still here.'
  } finally { addressSaving.value = false }
}

async function handleSubmit() {
  if (loading.value) return
  if (createdOrderId.value) { viewOrder(); return }
  if (checkoutCartLoading.value || cartStore.loading) { error.value = 'Your cart is still loading. Please wait.'; return }
  if (cartStore.error) { error.value = 'Your cart could not be loaded. Please retry before placing your order.'; return }
  if (!cartStore.items.length) { error.value = 'Your cart is empty. Add a product before placing an order.'; return }
  if (!validateStep(4)) return
  if (!form.value.payment_method) {
    error.value = 'Please select a payment method to continue'
    return
  }

  if (isMobileMoney.value && !form.value.payment_phone) {
    error.value = 'Please enter your mobile money phone number'
    return
  }

  loading.value = true
  error.value = ''

  try {
    if (!checkoutKey) {
      checkoutKey = crypto.randomUUID()
      if (!saveCheckoutAttempt()) {
        checkoutKey = ''
        error.value = 'Your browser is blocking session storage. Enable it before placing an order so we can safely recover your checkout.'
        return
      }
    }
    const order = createdOrderId.value ? { id: createdOrderId.value } : await orderService.createOrder({
      checkout_key: checkoutKey,
      province: form.value.province,
      town: form.value.town,
      delivery_method: form.value.delivery_method,
      payment_method: form.value.payment_method,
      street_address: form.value.street_address,
      phone: form.value.phone,
      notes: form.value.notes || undefined
    })

    createdOrderId.value = order.id
    createdOrder.value = order as Order
    saveCheckoutAttempt(order.id)
    if (isMobileMoney.value) {
      const run = ++paymentRun
      paymentStatus.value = 'processing'
      paymentMessage.value = 'Sending your payment request. Please wait.'

      try {
        const payment = await paymentService.initiatePayment(
          order.id,
          form.value.payment_method,
          normalizeZambianPhone(form.value.payment_phone)
        )

        if (run !== paymentRun) return
        if (payment.status === 'failed') {
          paymentStatus.value = 'failed'
          paymentMessage.value = payment.failure_reason === 'provider_access_denied'
            ? 'The payment provider could not authorize this request. No payment prompt was sent. Please contact the store; your order remains unpaid.'
            : 'The payment request was declined. Check the order status before trying again.'
          return
        }

        paymentMessage.value = payment.status === 'processing' ? `Check ${form.value.payment_phone} for a payment prompt and enter your PIN to authorize it.` : 'Checking whether the payment request reached your provider. Please do not submit another payment.'
        const finalPayment = payment.status === 'success' ? payment : await paymentService.pollPaymentStatus(order.id)

        if (run !== paymentRun) return
        if (finalPayment.status === 'success') {
          paymentStatus.value = 'success'
          paymentMessage.value = 'Payment successful! Redirecting...'
          cartStore.clearCart()
          clearCheckoutAttempt()
          setTimeout(() => {
            router.push(`/order/confirmation/${order.id}`)
          }, 2000)
        } else {
          paymentStatus.value = 'failed'
          paymentMessage.value = 'Payment was not completed. Please try again.'
        }
      } catch {
        if (run !== paymentRun) return
        paymentStatus.value = 'unknown'
        paymentMessage.value = 'We could not confirm whether the request reached your phone. Check the order status before making another payment.'
      }
    } else {
      clearCheckoutAttempt()
      cartStore.clearCart()
      router.push(`/order/confirmation/${order.id}`)
    }
  } catch (e: unknown) {
    const response = (e as { response?: { status?: number; data?: { detail?: string } } }).response
    if (response && response.status && response.status < 500) {
      clearCheckoutAttempt()
      error.value = response.data?.detail || 'We could not place your order. Check your details and try again.'
    } else {
      error.value = 'We could not confirm your order. Retry this checkout to recover it, or check your order history before starting another.'
    }
    paymentStatus.value = 'idle'
  } finally {
    loading.value = false
  }
}

watch(() => form.value.payment_method, (val) => {
  if (isMobileMoney.value) {
    form.value.payment_phone = form.value.phone || '260'
  }
})

async function loadDeliveryMethods() {
  deliveryLoading.value = true
  deliveryError.value = ''
  try {
    deliveryMethods.value = await orderService.getDeliveryMethods()
  } catch {
    deliveryError.value = 'Delivery methods could not be loaded. Check your connection and try again.'
  } finally {
    deliveryLoading.value = false
  }
}

onMounted(async () => {
  if (userStore.user) {
    form.value.first_name = userStore.user.first_name || ''
    form.value.last_name = userStore.user.last_name || ''
    form.value.email = userStore.user.email || ''
    form.value.phone = userStore.user.phone || '260'
  }
  await Promise.all([
    (async () => {
      try {
        if (createdOrderId.value) createdOrder.value = await orderService.getOrder(createdOrderId.value)
        else await cartStore.fetchCart()
      } catch { orderLoadError.value = 'Could not load the order total. Open order status and try again.' }
      finally { checkoutCartLoading.value = false }
    })(),
    orderService.getProvinces().then(data => { provinces.value = data }).catch(() => { error.value = 'Could not load provinces. Please refresh and try again.' }),
    loadDeliveryMethods(),
  ])

  if (userStore.isAuthenticated) {
    await loadSavedAddresses()
    const defaultAddress = savedAddresses.value.find(address => address.is_default)
    if (defaultAddress && currentStep.value === 1 && !form.value.province && !form.value.street_address && !createdOrderId.value) {
      await selectSavedAddress(defaultAddress, form.value.phone === (userStore.user?.phone || '260'))
    }
  }
})
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-8">
    <!-- Payment Processing Overlay -->
    <div v-if="paymentStatus !== 'idle'" ref="paymentOverlay" tabindex="-1" role="dialog" aria-modal="true" aria-label="Payment status" class="fixed inset-0 bg-white/90 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="text-center max-w-sm px-4">
        <div role="status" aria-live="polite" class="sr-only">{{ paymentMessage }}</div>
        <div v-if="paymentStatus === 'processing'" class="space-y-4">
          <Loader2 class="w-12 h-12 text-gold animate-spin mx-auto" />
          <h2 class="font-heading text-xl font-semibold text-dark">Processing Payment</h2>
          <p class="text-sm text-muted">{{ paymentMessage }}</p>
          <button v-if="createdOrderId" type="button" class="block mx-auto text-sm underline text-dark" @click="viewOrder">View order status</button>
          <div class="flex items-center justify-center gap-2 text-xs text-muted">
            <Smartphone class="w-4 h-4" />
            <span>Check your phone for the payment prompt</span>
          </div>
        </div>

        <div v-else-if="paymentStatus === 'success'" class="space-y-4">
          <CheckCircle2 class="w-12 h-12 text-green-500 mx-auto" />
          <h2 class="font-heading text-xl font-semibold text-dark">Payment Confirmed</h2>
          <p class="text-sm text-muted">{{ paymentMessage }}</p>
        </div>

        <div v-else-if="paymentStatus === 'unknown'" class="space-y-4">
          <h2 class="font-heading text-xl font-semibold text-dark">Payment status unknown</h2>
          <p class="text-sm text-muted">{{ paymentMessage }}</p>
          <BaseButton variant="secondary" @click="viewOrder">View order and check status</BaseButton>
        </div>

        <div v-else-if="paymentStatus === 'failed'" class="space-y-4">
          <XCircle class="w-12 h-12 text-red-500 mx-auto" />
          <h2 class="font-heading text-xl font-semibold text-dark">Payment Failed</h2>
          <p class="text-sm text-muted">{{ paymentMessage }}</p>
          <BaseButton variant="secondary" @click="paymentStatus = 'idle'; currentStep = 4">
            Check or retry payment
          </BaseButton>
          <button type="button" class="block mx-auto text-sm underline text-dark" @click="viewOrder">View order status</button>
        </div>
      </div>
    </div>

    <div v-if="createdOrderId && paymentStatus === 'idle'" class="mb-5 rounded-xl border border-primary/40 p-4 text-sm" role="status">
      You have an order awaiting payment. Check its status before starting another payment.
      <button type="button" class="block mt-2 underline" @click="viewOrder">View order status</button>
    </div>
    <div v-if="checkoutCartLoading" role="status" class="mb-4 text-sm text-muted">Loading your order summary…</div>
    <div v-else-if="orderLoadError" role="alert" class="mb-4 text-sm text-red-700">{{ orderLoadError }}</div>
    <div v-else-if="!createdOrderId && cartStore.error" role="alert" class="mb-4 text-sm text-red-700">
      {{ cartStore.error }} <button type="button" class="underline" @click="cartStore.fetchCart()">Try again</button>
    </div>
    <div v-else-if="!createdOrderId && cartStore.items.length === 0" role="alert" class="mb-4 text-sm text-red-700">
      Your cart is empty. <router-link class="underline" to="/catalog">Add a product</router-link> before placing an order.
    </div>
    <div class="lg:grid lg:grid-cols-12 lg:gap-8 lg:items-start">
      <div class="lg:col-span-7">
        <!-- Mobile collapsible order summary -->
        <div v-if="summaryItems.length > 0" class="mb-6 rounded-[16px] border border-primary/40 bg-white lg:hidden">
          <button
            type="button"
            class="flex w-full min-h-12 items-center justify-between px-4 py-3 text-sm font-medium text-dark"
            :aria-expanded="mobileSummaryOpen"
            aria-controls="mobile-order-summary"
            @click="mobileSummaryOpen = !mobileSummaryOpen"
          >
            <span class="flex items-center gap-2">
              <ShoppingBag class="w-4 h-4 text-gold" aria-hidden="true" />
              <span>Order summary ({{ summaryItemCount }} {{ summaryItemCount === 1 ? 'item' : 'items' }})</span>
            </span>
            <span class="flex items-center gap-2 font-semibold tabular-nums">
              K{{ grandTotal }}
              <ChevronDown class="w-4 h-4 text-muted transition-transform" :class="{ 'rotate-180': mobileSummaryOpen }" aria-hidden="true" />
            </span>
          </button>
          <div v-show="mobileSummaryOpen" id="mobile-order-summary" class="border-t border-primary/20 px-4 py-3 space-y-3">
            <ul class="space-y-2.5">
              <li v-for="item in summaryItems" :key="item.id" class="flex items-center gap-3 text-sm">
                <div class="h-12 w-10 shrink-0 overflow-hidden rounded-lg bg-primary/20">
                  <img v-if="item.image" :src="item.image" :alt="item.title" class="h-full w-full object-cover" />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="truncate font-medium text-dark">{{ item.title }}</p>
                  <p class="text-xs text-muted">Qty {{ item.quantity }}</p>
                </div>
                <span class="shrink-0 font-medium text-dark tabular-nums">K{{ item.lineTotal }}</span>
              </li>
            </ul>
            <div class="border-t border-primary/20 pt-2.5 space-y-1 text-sm">
              <div class="flex justify-between"><span class="text-muted">Subtotal</span><span class="tabular-nums">K{{ checkoutSubtotal }}</span></div>
              <div class="flex justify-between"><span class="text-muted">Delivery</span><span class="tabular-nums">K{{ checkoutDelivery }}</span></div>
              <div class="flex justify-between font-semibold text-dark pt-1"><span>Total</span><span class="tabular-nums">K{{ grandTotal }}</span></div>
            </div>
          </div>
        </div>

        <!-- Progress -->
        <nav class="mb-8" aria-label="Checkout steps">
          <div class="flex items-center justify-between mb-3">
            <span class="text-xs text-muted">Step {{ currentStep }} of {{ totalSteps }}</span>
            <span class="text-sm font-medium text-dark">{{ stepTitle }}</span>
          </div>
          <ol class="grid grid-cols-4 gap-2">
            <li v-for="(label, idx) in stepLabels" :key="label">
              <button
                type="button"
                class="w-full text-left group focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold rounded"
                :disabled="idx + 1 >= currentStep"
                :aria-current="idx + 1 === currentStep ? 'step' : undefined"
                @click="goToStep(idx + 1)"
              >
                <span
                  class="block h-1.5 w-full rounded-full transition-colors"
                  :class="idx + 1 <= currentStep ? 'bg-dark' : 'bg-primary/40'"
                />
                <span
                  class="mt-1.5 block text-[11px] font-medium truncate"
                  :class="idx + 1 === currentStep ? 'text-dark' : idx + 1 < currentStep ? 'text-gold group-hover:underline' : 'text-muted'"
                >
                  {{ idx + 1 }}. {{ label }}
                </span>
              </button>
            </li>
          </ol>
        </nav>

    <form novalidate @submit.prevent="currentStep === totalSteps ? handleSubmit() : nextStep()">
      <!-- Step 1: Customer Details -->
      <div v-if="currentStep === 1" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Your Details</h2>
        <div class="grid grid-cols-2 gap-3">
          <BaseInput
            v-model="form.first_name"
            label="First Name"
            required
            id="first_name"
          :error="fieldErrors.first_name"
          />
          <BaseInput
            v-model="form.last_name"
            label="Last Name"
            required
            id="last_name"
          :error="fieldErrors.last_name"
          />
        </div>
        <BaseInput
          v-model="form.email"
          label="Email"
          type="email"
          required
          id="email"
          :error="fieldErrors.email"
        />
        <BaseInput
          v-model="form.phone"
          label="Phone Number"
          type="tel"
          required
          id="phone"
          :error="fieldErrors.phone"
          placeholder="260xxxxxxxxx"
        />
        <p class="text-xs text-muted -mt-2">Enter a Zambian number for delivery updates.</p>
      </div>

      <!-- Step 2: Delivery Location -->
      <div v-if="currentStep === 2" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Delivery Location</h2>

        <p v-if="addressLoading" role="status" class="text-sm text-muted">Loading saved addresses…</p>
        <div v-if="addressError" role="alert" class="rounded-xl bg-red-50 p-4 text-sm text-red-700"><p>{{ addressError }}</p><button v-if="!addressSaving" type="button" class="mt-2 min-h-11 font-medium underline" @click="loadSavedAddresses">Reload saved addresses</button></div>

        <div v-if="savedAddresses.length > 0" class="space-y-2 mb-4">
          <p class="text-sm font-medium text-dark">Deliver to a saved address</p>
          <div class="space-y-2">
            <button
              v-for="address in savedAddresses"
              :key="address.id"
              type="button"
              class="w-full p-3 border rounded-[14px] text-left transition-all"
              :class="selectedAddressId === address.id && form.province === address.province && form.town === address.town && form.street_address === address.street_address ? 'border-gold bg-gold/5' : 'border-primary/40 hover:border-primary'"
              @click="selectSavedAddress(address)"
            >
              <div class="flex items-start gap-2">
                <MapPin class="w-4 h-4 text-muted mt-0.5 shrink-0" />
                <div class="min-w-0">
                  <p class="text-sm text-dark break-words">{{ address.street_address }}</p>
                  <p class="text-xs text-muted">{{ address.town_name || address.town }}, {{ address.province_name || address.province }}</p>
                  <p class="text-xs text-muted">Phone: {{ address.phone }}</p>
                </div>
                <span
                  v-if="address.is_default"
                  class="ml-auto text-[10px] font-medium text-gold bg-gold/10 px-2 py-0.5 rounded-full shrink-0"
                >Default</span>
              </div>
            </button>
          </div>
          <button
            type="button"
            class="text-sm text-gold hover:underline"
            @click="useCustomAddress"
          >
            + Enter a new address
          </button>
          <div class="border-t border-primary/20 pt-4" />
        </div>

        <BaseSelect
          v-model="form.province"
          label="Province"
          :options="provinces.map(p => ({ value: p.id, label: p.name }))"
          required
          id="province"
          :error="fieldErrors.province"
          @update:modelValue="handleProvinceChange"
        />
        <BaseSelect
          v-model="form.town"
          label="Town / City"
          :options="towns.map(t => ({ value: t.id, label: t.name }))"
          required
          id="town"
          :error="fieldErrors.town"
          :disabled="!form.province || townsLoading"
        />
        <p v-if="townsLoading" role="status" class="text-sm text-muted">Loading towns…</p>
        <p v-if="townsError" role="alert" class="text-sm text-red-700">{{ townsError }} <button type="button" class="min-h-11 underline" @click="handleProvinceChange(form.province)">Try again</button></p>
        <BaseInput
          v-model="form.street_address"
          label="Street Address"
          required
          id="street_address"
          :error="fieldErrors.street_address"
          placeholder="Street, building, landmark"
        />
        <div v-if="userStore.isAuthenticated" class="rounded-xl border border-primary/40 bg-white p-4">
          <p class="text-sm font-medium text-dark">Save this delivery address</p>
          <p class="mt-1 text-sm text-muted">Keep this address and delivery phone in your account for a faster checkout. You can manage saved addresses in your account.</p>
          <button type="button" class="mt-2 min-h-11 font-semibold text-sm text-dark underline underline-offset-4 disabled:opacity-50 focus-visible:outline-2 focus-visible:outline-gold" :disabled="addressSaving || addressLoading || townsLoading" @click="saveAddress">{{ addressSaving ? 'Saving address…' : 'Save address' }}</button>
          <p v-if="addressNotice" role="status" class="mt-1 text-sm text-green-800">{{ addressNotice }}</p>
        </div>
      </div>

      <!-- Step 3: Delivery Method -->
      <div v-if="currentStep === 3" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Delivery Method</h2>
        <p v-if="deliveryLoading" role="status" class="text-sm text-muted">Loading delivery methods…</p>
        <div v-else-if="deliveryError" role="alert" class="rounded-xl bg-red-50 p-4 text-sm text-red-700">
          <p>{{ deliveryError }}</p><button type="button" class="mt-2 underline" @click="loadDeliveryMethods">Try again</button>
        </div>
        <div v-else-if="deliveryMethods.length === 0" role="status" class="rounded-xl border border-primary/40 p-4 text-sm text-muted">
          No delivery methods are available right now. Please contact the store for assistance.
          <button type="button" class="mt-2 block underline" @click="loadDeliveryMethods">Check again</button>
        </div>
        <div v-else class="space-y-3">
          <label
            v-for="method in deliveryMethods"
            :key="method.id"
            class="block p-4 border rounded-[16px] cursor-pointer transition-all focus-within:ring-2 focus-within:ring-gold/50"
            :class="form.delivery_method === method.id ? 'border-gold bg-gold/5' : 'border-primary/40 hover:border-primary'"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                <div
                  class="w-4 h-4 rounded-full border-2 flex items-center justify-center"
                  :class="form.delivery_method === method.id ? 'border-gold' : 'border-primary/60'"
                >
                  <div v-if="form.delivery_method === method.id" class="w-2 h-2 rounded-full bg-gold" />
                </div>
                <div>
                  <p class="text-sm font-medium text-dark">{{ method.name }}</p>
                  <p class="text-xs text-muted">{{ method.description }} &middot; {{ method.estimated_days }}</p>
                </div>
              </div>
              <p class="text-sm font-semibold text-dark">K{{ method.price }}</p>
            </div>
            <input
              type="radio"
              name="delivery_method"
              :value="method.id"
              v-model="form.delivery_method"
              class="sr-only peer"
            />
          </label>
        </div>
        <p v-if="fieldErrors.delivery_method" role="alert" class="text-sm text-red-700">{{ fieldErrors.delivery_method }}</p>
      </div>

      <!-- Step 4: Payment -->
      <div v-if="currentStep === 4" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Payment</h2>
        <p class="text-sm text-muted mb-4">Choose how you'd like to pay. You'll be prompted to complete payment after placing your order.</p>
        <div class="space-y-3">
          <label
            v-for="method in paymentMethods"
            :key="method.value"
            class="block p-4 border rounded-[16px] cursor-pointer transition-all focus-within:ring-2 focus-within:ring-gold/50"
            :class="form.payment_method === method.value ? 'border-gold bg-gold/5' : 'border-primary/40 hover:border-primary'"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0"
                :class="form.payment_method === method.value ? 'border-gold' : 'border-primary/60'"
              >
                <div v-if="form.payment_method === method.value" class="w-2 h-2 rounded-full bg-gold" />
              </div>
              <div>
                <span class="text-sm font-medium text-dark">{{ method.label }}</span>
                <p class="text-xs text-muted">{{ method.description }}</p>
              </div>
            </div>
            <input
              type="radio"
              name="payment_method"
              :value="method.value"
              v-model="form.payment_method"
              class="sr-only peer"
            />
          </label>
        </div>

        <p v-if="fieldErrors.payment_method" role="alert" class="text-sm text-red-700">{{ fieldErrors.payment_method }}</p>

        <!-- Mobile Money Phone Input -->
        <div v-if="isMobileMoney" class="mt-4 p-4 bg-gold/5 border border-gold/20 rounded-[16px] space-y-3">
          <div class="flex items-center gap-2">
            <Smartphone class="w-4 h-4 text-gold" />
            <p class="text-sm font-medium text-dark">{{ operatorLabel }} Mobile Money</p>
          </div>
          <BaseInput
            v-model="form.payment_phone"
            :label="`${operatorLabel} Phone Number`"
            type="tel"
            required
            id="payment_phone"
          :error="fieldErrors.payment_phone"
            placeholder="260xxxxxxxxx"
          />
          <p class="text-xs text-muted">Enter the phone number registered with your {{ operatorLabel }} Money account</p>
        </div>

        <div class="rounded-[16px] border border-primary/50 bg-white p-4 text-sm space-y-3">
          <h3 class="font-semibold text-dark">Delivery details</h3>
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-xs text-muted">Contact</p>
              <p class="text-dark">{{ form.first_name }} {{ form.last_name }} · {{ form.phone }}</p>
            </div>
            <button type="button" class="text-xs font-medium text-gold underline underline-offset-2 shrink-0" @click="currentStep = 1">Edit</button>
          </div>
          <div class="flex items-start justify-between gap-3 border-t border-primary/15 pt-2.5">
            <div class="min-w-0">
              <p class="text-xs text-muted">Address</p>
              <p class="text-dark">{{ form.street_address }}, {{ towns.find(t => t.id === form.town)?.name }}, {{ provinces.find(p => p.id === form.province)?.name }}</p>
            </div>
            <button type="button" class="text-xs font-medium text-gold underline underline-offset-2 shrink-0" @click="currentStep = 2">Edit</button>
          </div>
          <div class="flex items-start justify-between gap-3 border-t border-primary/15 pt-2.5">
            <div class="min-w-0">
              <p class="text-xs text-muted">Delivery method</p>
              <p class="text-dark">{{ selectedDeliveryMethod?.name }}</p>
            </div>
            <button type="button" class="text-xs font-medium text-gold underline underline-offset-2 shrink-0" @click="currentStep = 3">Edit</button>
          </div>
        </div>

        <!-- Order Summary (mobile/inline on Review step) -->
        <div class="bg-white p-4 rounded-[16px] border border-primary/30 mt-6 space-y-2 lg:hidden">
          <div class="flex justify-between text-sm">
            <span class="text-muted">Subtotal</span>
            <span class="font-medium tabular-nums">K{{ checkoutSubtotal }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Delivery</span>
            <span class="font-medium tabular-nums">K{{ checkoutDelivery }}</span>
          </div>
          <div class="flex justify-between text-sm font-semibold pt-2 border-t border-primary/20">
            <span class="text-dark">Total</span>
            <span class="text-dark tabular-nums">K{{ grandTotal }}</span>
          </div>
        </div>

        <p v-if="error" role="alert" class="text-sm text-red-700">{{ error }}</p>
      </div>

      <!-- Navigation -->
      <div class="flex items-center justify-between mt-8">
        <button
          v-if="currentStep > 1"
          type="button"
          class="flex items-center gap-1 min-h-11 px-2 text-sm text-muted hover:text-dark transition-colors"
          @click="prevStep"
        >
          <ChevronLeft class="w-4 h-4" /> Back
        </button>
        <div v-else />

        <BaseButton
          :type="currentStep === totalSteps ? 'submit' : 'button'"
          variant="secondary"
          :loading="loading"
          :disabled="checkoutCartLoading || (currentStep === totalSteps && !createdOrderId && (!!cartStore.error || cartStore.loading || cartStore.items.length === 0))"
          @click="currentStep < totalSteps ? nextStep() : undefined"
        >
          {{ currentStep === totalSteps ? (createdOrderId ? 'View order status' : 'Place Order & Pay') : 'Continue' }}
          <ChevronRight class="w-4 h-4 ml-1" />
        </BaseButton>
      </div>
    </form>
      </div>

      <!-- Desktop sticky order summary sidebar -->
      <aside v-if="summaryItems.length > 0" aria-label="Order summary" class="hidden lg:block lg:col-span-5 lg:sticky lg:top-24">
        <div class="rounded-[20px] border border-primary/40 bg-white p-6 space-y-4">
          <div class="flex items-center justify-between">
            <h2 class="font-heading text-base font-semibold text-dark">Order Summary</h2>
            <span class="text-xs text-muted">{{ summaryItemCount }} {{ summaryItemCount === 1 ? 'item' : 'items' }}</span>
          </div>
          <ul class="space-y-3 max-h-80 overflow-y-auto pr-1">
            <li v-for="item in summaryItems" :key="item.id" class="flex items-center gap-3 text-sm">
              <div class="h-14 w-12 shrink-0 overflow-hidden rounded-xl bg-primary/20">
                <img v-if="item.image" :src="item.image" :alt="item.title" class="h-full w-full object-cover" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-dark">{{ item.title }}</p>
                <p class="text-xs text-muted">Qty {{ item.quantity }}</p>
              </div>
              <span class="shrink-0 font-medium text-dark tabular-nums">K{{ item.lineTotal }}</span>
            </li>
          </ul>
          <div class="border-t border-primary/20 pt-4 space-y-2 text-sm">
            <div class="flex justify-between">
              <span class="text-muted">Subtotal</span>
              <span class="font-medium text-dark tabular-nums">K{{ checkoutSubtotal }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted">Delivery</span>
              <span class="font-medium text-dark tabular-nums">{{ selectedDeliveryMethod || createdOrder ? `K${checkoutDelivery}` : 'Calculated at step 3' }}</span>
            </div>
            <div class="flex justify-between text-base font-semibold pt-2 border-t border-primary/20">
              <span class="text-dark">Total</span>
              <span class="text-dark tabular-nums">K{{ grandTotal }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script lang="ts">
const paymentMethods = [
  { value: 'mtn_momo', label: 'MTN Mobile Money', description: 'Pay with your MTN MoMo account' },
  { value: 'airtel_money', label: 'Airtel Money', description: 'Pay with your Airtel Money account' },
]
</script>

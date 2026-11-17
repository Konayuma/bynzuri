<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { useUserStore } from '@/stores/user'
import { orderService } from '@/services/order.service'
import { addressService } from '@/services/address.service'
import { paymentService } from '@/services/payment.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import { ChevronLeft, ChevronRight, MapPin, Loader2, CheckCircle2, XCircle, Smartphone } from '@lucide/vue'
import type { Province, Town, DeliveryMethod, Address } from '@/types'
import { isEmail, isZambianPhone, normalizeZambianPhone } from '@/utils/formValidation'

const router = useRouter()
const cartStore = useCartStore()
const userStore = useUserStore()
const loading = ref(false)
const currentStep = ref(1)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})

const paymentStatus = ref<'idle' | 'processing' | 'success' | 'failed'>('idle')
const paymentMessage = ref('')
const createdOrderId = ref<string | null>(null)

const provinces = ref<Province[]>([])
const towns = ref<Town[]>([])
const deliveryMethods = ref<DeliveryMethod[]>([])
const savedAddresses = ref<Address[]>([])
const selectedAddressId = ref<string | null>(null)

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

const stepTitle = computed(() => {
  const titles = ['', 'Your Details', 'Delivery Location', 'Delivery Method', 'Review & Pay']
  return titles[currentStep.value]
})

const selectedDeliveryMethod = computed(() =>
  deliveryMethods.value.find(m => m.id === form.value.delivery_method)
)

const grandTotal = computed(() => {
  const subtotal = parseFloat(cartStore.subtotal) || 0
  const delivery = parseFloat(selectedDeliveryMethod.value?.price || '0')
  return (subtotal + delivery).toFixed(2)
})

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
    if (isMobileMoney.value && !isZambianPhone(data.payment_phone)) errors.payment_phone = 'Enter a valid Zambian mobile number.'
  }
  fieldErrors.value = errors
  return Object.keys(errors).length === 0
}

function nextStep() {
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
  form.value.province = provinceId
  form.value.town = ''
  if (provinceId) {
    towns.value = await orderService.getTowns(provinceId)
  } else {
    towns.value = []
  }
}

async function selectSavedAddress(address: Address) {
  selectedAddressId.value = address.id
  form.value.province = address.province
  form.value.town = address.town
  form.value.street_address = address.street_address
  form.value.phone = address.phone
  if (address.province) {
    towns.value = await orderService.getTowns(address.province)
  }
}

function useCustomAddress() {
  selectedAddressId.value = null
  form.value.province = ''
  form.value.town = ''
  form.value.street_address = ''
  form.value.phone = '260'
  towns.value = []
}

async function handleSubmit() {
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
    const order = createdOrderId.value ? { id: createdOrderId.value } : await orderService.createOrder({
      province: form.value.province,
      town: form.value.town,
      delivery_method: form.value.delivery_method,
      payment_method: form.value.payment_method,
      street_address: form.value.street_address,
      phone: form.value.phone,
      notes: form.value.notes || undefined
    })

    createdOrderId.value = order.id
    if (isMobileMoney.value) {
      paymentStatus.value = 'processing'
      paymentMessage.value = 'Sending your payment request. Please wait.'

      try {
        const payment = await paymentService.initiatePayment(
          order.id,
          form.value.payment_method,
          normalizeZambianPhone(form.value.payment_phone)
        )

        if (payment.status === 'failed') {
          paymentStatus.value = 'failed'
          paymentMessage.value = 'Payment initiation failed. Please try again.'
          return
        }

        paymentMessage.value = `Check ${form.value.payment_phone} for a payment prompt and enter your PIN to authorize it.`
        const finalPayment = payment.status === 'success' ? payment : await paymentService.pollPaymentStatus(order.id)

        if (finalPayment.status === 'success') {
          paymentStatus.value = 'success'
          paymentMessage.value = 'Payment successful! Redirecting...'
          cartStore.clearCart()
          setTimeout(() => {
            router.push(`/order/confirmation/${order.id}`)
          }, 2000)
        } else {
          paymentStatus.value = 'failed'
          paymentMessage.value = 'Payment was not completed. Please try again.'
        }
      } catch {
        paymentStatus.value = 'failed'
        paymentMessage.value = 'We could not confirm the payment yet. Check your order status before making another payment.'
      }
    } else {
      cartStore.clearCart()
      router.push(`/order/confirmation/${order.id}`)
    }
  } catch (e: unknown) {
    error.value = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'We couldn\'t place your order. Please check your details and try again.'
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

onMounted(async () => {
  const [provincesData, methodsData] = await Promise.all([
    orderService.getProvinces(),
    orderService.getDeliveryMethods(),
  ])
  provinces.value = provincesData
  deliveryMethods.value = methodsData

  if (userStore.isAuthenticated) {
    try {
      savedAddresses.value = await addressService.getAddresses()
    } catch {
      savedAddresses.value = []
    }
    if (userStore.user) {
      form.value.first_name = userStore.user.first_name || ''
      form.value.last_name = userStore.user.last_name || ''
      form.value.email = userStore.user.email || ''
      form.value.phone = userStore.user.phone || '260'
    }
  }
})
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <!-- Payment Processing Overlay -->
    <div v-if="paymentStatus !== 'idle'" class="fixed inset-0 bg-white/90 backdrop-blur-sm z-50 flex items-center justify-center">
      <div class="text-center max-w-sm px-4">
        <div v-if="paymentStatus === 'processing'" class="space-y-4">
          <Loader2 class="w-12 h-12 text-gold animate-spin mx-auto" />
          <h2 class="font-heading text-xl font-semibold text-dark">Processing Payment</h2>
          <p class="text-sm text-muted">{{ paymentMessage }}</p>
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

        <div v-else-if="paymentStatus === 'failed'" class="space-y-4">
          <XCircle class="w-12 h-12 text-red-500 mx-auto" />
          <h2 class="font-heading text-xl font-semibold text-dark">Payment Failed</h2>
          <p class="text-sm text-muted">{{ paymentMessage }}</p>
          <BaseButton variant="secondary" @click="paymentStatus = 'idle'; currentStep = 4">
            Check or retry payment
          </BaseButton>
          <button type="button" class="block mx-auto text-sm underline text-dark" @click="cartStore.clearCart(); router.push(`/order/confirmation/${createdOrderId}`)">View order status</button>
        </div>
      </div>
    </div>

    <!-- Progress -->
    <div class="mb-8">
      <div class="flex items-center justify-between mb-2">
        <span class="text-xs text-muted">Step {{ currentStep }} of {{ totalSteps }}</span>
        <span class="text-sm font-medium text-dark">{{ stepTitle }}</span>
      </div>
      <div class="flex gap-2">
        <div
          v-for="i in totalSteps"
          :key="i"
          class="h-1 flex-1 rounded-full transition-colors"
          :class="i <= currentStep ? 'bg-dark' : 'bg-primary/40'"
        />
      </div>
    </div>

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
        <p class="text-xs text-muted -mt-2">We'll send delivery updates via SMS</p>
      </div>

      <!-- Step 2: Delivery Location -->
      <div v-if="currentStep === 2" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Delivery Location</h2>

        <div v-if="savedAddresses.length > 0" class="space-y-2 mb-4">
          <p class="text-sm font-medium text-dark">Deliver to a saved address</p>
          <div class="space-y-2">
            <button
              v-for="address in savedAddresses"
              :key="address.id"
              type="button"
              class="w-full p-3 border rounded-[14px] text-left transition-all"
              :class="selectedAddressId === address.id ? 'border-gold bg-gold/5' : 'border-primary/40 hover:border-primary'"
              @click="selectSavedAddress(address)"
            >
              <div class="flex items-start gap-2">
                <MapPin class="w-4 h-4 text-muted mt-0.5 shrink-0" />
                <div>
                  <p class="text-sm text-dark">{{ address.street_address }}</p>
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
          :disabled="!form.province"
        />
        <BaseInput
          v-model="form.street_address"
          label="Street Address"
          required
          id="street_address"
          :error="fieldErrors.street_address"
          placeholder="Street, building, landmark"
        />
      </div>

      <!-- Step 3: Delivery Method -->
      <div v-if="currentStep === 3" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Delivery Method</h2>
        <div class="space-y-3">
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

        <div class="rounded-[16px] border border-primary/50 bg-white p-4 text-sm space-y-2">
          <div class="flex items-center justify-between"><h3 class="font-semibold text-dark">Delivery details</h3><button type="button" class="text-gold underline underline-offset-2" @click="currentStep = 2">Edit</button></div>
          <p class="text-dark">{{ form.first_name }} {{ form.last_name }} · {{ form.phone }}</p>
          <p class="text-muted">{{ form.street_address }}, {{ towns.find(t => t.id === form.town)?.name }}, {{ provinces.find(p => p.id === form.province)?.name }}</p>
          <p class="text-muted">{{ selectedDeliveryMethod?.name }}</p>
        </div>

        <!-- Order Summary -->
        <div class="bg-white p-4 rounded-[16px] mt-6 space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-muted">Subtotal</span>
            <span class="font-medium">K{{ cartStore.subtotal }}</span>
          </div>
          <div class="flex justify-between text-sm">
            <span class="text-muted">Delivery</span>
            <span class="font-medium">K{{ selectedDeliveryMethod?.price || '0.00' }}</span>
          </div>
          <div class="flex justify-between text-sm font-semibold pt-2 border-t border-primary/20">
            <span class="text-dark">Total</span>
            <span class="text-dark">K{{ grandTotal }}</span>
          </div>
        </div>

        <p v-if="error" class="text-xs text-red-500">{{ error }}</p>
      </div>

      <!-- Navigation -->
      <div class="flex items-center justify-between mt-8">
        <button
          v-if="currentStep > 1"
          type="button"
          class="flex items-center gap-1 text-sm text-muted hover:text-dark transition-colors"
          @click="prevStep"
        >
          <ChevronLeft class="w-4 h-4" /> Back
        </button>
        <div v-else />

        <BaseButton
          :type="currentStep === totalSteps ? 'submit' : 'button'"
          variant="secondary"
          :loading="loading"
          @click="currentStep < totalSteps ? nextStep() : undefined"
        >
          {{ currentStep === totalSteps ? 'Place Order & Pay' : 'Continue' }}
          <ChevronRight class="w-4 h-4 ml-1" />
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
const paymentMethods = [
  { value: 'mtn_momo', label: 'MTN Mobile Money', description: 'Pay with your MTN MoMo account' },
  { value: 'airtel_money', label: 'Airtel Money', description: 'Pay with your Airtel Money account' },
]
</script>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '@/stores/cart'
import { orderService } from '@/services/order.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import { ChevronLeft, ChevronRight, Check } from '@lucide/vue'
import type { Province, Town, DeliveryMethod } from '@/types'

const router = useRouter()
const cartStore = useCartStore()
const loading = ref(false)
const currentStep = ref(1)
const error = ref('')

const provinces = ref<Province[]>([])
const towns = ref<Town[]>([])
const deliveryMethods = ref<DeliveryMethod[]>([])

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
  notes: ''
})

const totalSteps = 4

const stepTitle = computed(() => {
  const titles = ['', 'Your Details', 'Delivery Location', 'Delivery Method', 'Payment']
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

function nextStep() {
  if (currentStep.value < totalSteps) currentStep.value++
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

async function handleSubmit() {
  if (!form.value.payment_method) {
    error.value = 'Please select a payment method'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const order = await orderService.createOrder({
      province: form.value.province,
      town: form.value.town,
      delivery_method: form.value.delivery_method,
      payment_method: form.value.payment_method,
      street_address: form.value.street_address,
      phone: form.value.phone,
      notes: form.value.notes || undefined
    })
    cartStore.clearCart()
    router.push(`/order/confirmation/${order.id}`)
  } catch (e: unknown) {
    error.value = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Something went wrong. Please try again.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  provinces.value = await orderService.getProvinces()
  deliveryMethods.value = await orderService.getDeliveryMethods()
})
</script>

<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
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

    <form @submit.prevent="currentStep === totalSteps ? handleSubmit() : nextStep()">
      <!-- Step 1: Customer Details -->
      <div v-if="currentStep === 1" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Your Details</h2>
        <div class="grid grid-cols-2 gap-3">
          <BaseInput
            v-model="form.first_name"
            label="First Name"
            required
            id="first_name"
          />
          <BaseInput
            v-model="form.last_name"
            label="Last Name"
            required
            id="last_name"
          />
        </div>
        <BaseInput
          v-model="form.email"
          label="Email"
          type="email"
          required
          id="email"
        />
        <BaseInput
          v-model="form.phone"
          label="Phone Number"
          type="tel"
          required
          id="phone"
          placeholder="260xxxxxxxxx"
        />
      </div>

      <!-- Step 2: Delivery Location -->
      <div v-if="currentStep === 2" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Delivery Location</h2>
        <BaseSelect
          v-model="form.province"
          label="Province"
          :options="provinces.map(p => ({ value: p.id, label: p.name }))"
          required
          id="province"
          @update:modelValue="handleProvinceChange"
        />
        <BaseSelect
          v-model="form.town"
          label="Town / City"
          :options="towns.map(t => ({ value: t.id, label: t.name }))"
          required
          id="town"
          :disabled="!form.province"
        />
        <BaseInput
          v-model="form.street_address"
          label="Street Address"
          required
          id="street_address"
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
            class="block p-4 border rounded-[16px] cursor-pointer transition-all"
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
                  <p class="text-xs text-muted">{{ method.description }} ({{ method.estimated_days }})</p>
                </div>
              </div>
              <p class="text-sm font-semibold text-dark">K{{ method.price }}</p>
            </div>
            <input
              type="radio"
              :value="method.id"
              v-model="form.delivery_method"
              class="hidden"
            />
          </label>
        </div>
      </div>

      <!-- Step 4: Payment -->
      <div v-if="currentStep === 4" class="space-y-4">
        <h2 class="font-heading text-xl font-semibold text-dark mb-4">Payment</h2>
        <p class="text-sm text-muted mb-4">Select your preferred payment method</p>
        <div class="space-y-3">
          <label
            v-for="method in paymentMethods"
            :key="method.value"
            class="block p-4 border rounded-[16px] cursor-pointer transition-all"
            :class="form.payment_method === method.value ? 'border-gold bg-gold/5' : 'border-primary/40 hover:border-primary'"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-4 h-4 rounded-full border-2 flex items-center justify-center shrink-0"
                :class="form.payment_method === method.value ? 'border-gold' : 'border-primary/60'"
              >
                <div v-if="form.payment_method === method.value" class="w-2 h-2 rounded-full bg-gold" />
              </div>
              <span class="text-sm font-medium text-dark">{{ method.label }}</span>
            </div>
            <input
              type="radio"
              :value="method.value"
              v-model="form.payment_method"
              class="hidden"
            />
          </label>
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
          {{ currentStep === totalSteps ? 'Place Order' : 'Continue' }}
          <ChevronRight class="w-4 h-4 ml-1" />
        </BaseButton>
      </div>
    </form>
  </div>
</template>

<script lang="ts">
const paymentMethods = [
  { value: 'mtn_momo', label: 'MTN MoMo' },
  { value: 'airtel_money', label: 'Airtel Money' },
  { value: 'visa', label: 'Visa' },
  { value: 'mastercard', label: 'Mastercard' }
]
</script>

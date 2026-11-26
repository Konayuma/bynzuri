<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useCartStore } from '@/stores/cart'
import { useWishlistStore } from '@/stores/wishlist'
import { useUIStore } from '@/stores/ui'
import { useRouter } from 'vue-router'
import { addressService } from '@/services/address.service'
import { orderService } from '@/services/order.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseModal from '@/components/base/BaseModal.vue'
import {
  User, Package, MapPin, LogOut, Plus, Pencil, Trash2, Star,
  Heart, ShieldCheck, KeyRound, HelpCircle, LayoutDashboard, CheckCircle2, ChevronRight
} from '@lucide/vue'
import type { Address, Province, Town, Order } from '@/types'
import { isZambianPhone } from '@/utils/formValidation'
import { isValidPhoneNumber } from 'libphonenumber-js'

const userStore = useUserStore()
const cartStore = useCartStore()
const wishlistStore = useWishlistStore()
const uiStore = useUIStore()
const router = useRouter()

// Profile editing state
const editingProfile = ref(false)
const savingProfile = ref(false)
const profileError = ref('')
const profileForm = ref({
  first_name: '',
  last_name: '',
  phone: '',
})

// Recent orders state
const recentOrders = ref<Order[]>([])
const loadingOrders = ref(true)
const ordersError = ref(false)

// Addresses state
const addresses = ref<Address[]>([])
const loadingAddresses = ref(true)
const addressesLoadError = ref(false)
const showModal = ref(false)
const editingAddress = ref<Address | null>(null)
const saving = ref(false)
const formError = ref('')
const addressError = ref('')
const confirmDeleteId = ref<string | null>(null)
const deletingId = ref<string | null>(null)

const provinces = ref<Province[]>([])
const towns = ref<Town[]>([])

const form = ref({
  province: '',
  town: '',
  street_address: '',
  phone: '260',
  is_default: false,
})

const fullName = computed(() => {
  const name = [userStore.user?.first_name, userStore.user?.last_name].filter(Boolean).join(' ').trim()
  return name || 'My Account'
})

const initials = computed(() => {
  const first = userStore.user?.first_name?.trim()?.[0] || ''
  const last = userStore.user?.last_name?.trim()?.[0] || ''
  return (first + last).toUpperCase()
})

const provinceOptions = computed(() =>
  Array.isArray(provinces.value)
    ? provinces.value.map(p => ({ value: p.id, label: p.name }))
    : []
)

const townOptions = computed(() =>
  Array.isArray(towns.value)
    ? towns.value.map(t => ({ value: t.id, label: t.name }))
    : []
)

const statusColors: Record<string, string> = {
  awaiting_payment: 'text-gold bg-gold/10',
  paid: 'text-blue-600 bg-blue-50',
  processing: 'text-dark bg-primary/30',
  dispatched: 'text-success bg-success/10',
  delivered: 'text-success bg-success/10',
  cancelled: 'text-red-600 bg-red-50',
}

const statusLabels: Record<string, string> = {
  awaiting_payment: 'Awaiting Payment',
  paid: 'Paid',
  processing: 'Processing',
  dispatched: 'Dispatched',
  delivered: 'Delivered',
  cancelled: 'Cancelled',
}

function syncProfileForm() {
  profileForm.value = {
    first_name: userStore.user?.first_name || '',
    last_name: userStore.user?.last_name || '',
    phone: userStore.user?.phone || '',
  }
}

watch(() => userStore.user, () => {
  if (!editingProfile.value) syncProfileForm()
}, { immediate: true })

function startEditProfile() {
  syncProfileForm()
  profileError.value = ''
  editingProfile.value = true
}

function cancelEditProfile() {
  syncProfileForm()
  profileError.value = ''
  editingProfile.value = false
}

async function saveProfile() {
  const firstName = profileForm.value.first_name.trim()
  const lastName = profileForm.value.last_name.trim()
  const phone = profileForm.value.phone.trim()

  if (!firstName) {
    profileError.value = 'Enter your first name.'
    return
  }
  if (phone && !isZambianPhone(phone) && !isValidPhoneNumber(phone)) {
    profileError.value = 'Enter a valid phone number with its country code, for example +260 97 123 4567.'
    return
  }

  savingProfile.value = true
  profileError.value = ''
  try {
    await userStore.updateProfile({
      first_name: firstName,
      last_name: lastName,
      phone,
    })
    editingProfile.value = false
    uiStore.showToast('Profile details updated.')
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    profileError.value = detail || 'Could not update your profile. Please try again.'
  } finally {
    savingProfile.value = false
  }
}

function handleLogout() {
  userStore.logout()
  cartStore.cart = null
  cartStore.initGuestCart()
  router.push('/')
}

async function loadOrders() {
  loadingOrders.value = true
  ordersError.value = false
  try {
    const data = await orderService.getOrders()
    recentOrders.value = Array.isArray(data) ? data : []
  } catch {
    recentOrders.value = []
    ordersError.value = true
  } finally {
    loadingOrders.value = false
  }
}

async function loadAddresses() {
  loadingAddresses.value = true
  addressesLoadError.value = false
  try {
    const data = await addressService.getAddresses()
    addresses.value = Array.isArray(data) ? data : []
  } catch {
    addresses.value = []
    addressesLoadError.value = true
  } finally {
    loadingAddresses.value = false
  }
}

async function loadProvinces() {
  try {
    const data = await orderService.getProvinces()
    provinces.value = Array.isArray(data) ? data : []
  } catch {
    provinces.value = []
  }
}

async function handleProvinceChange(provinceId: string) {
  form.value.province = provinceId
  form.value.town = ''
  if (provinceId) {
    try {
      const data = await orderService.getTowns(provinceId)
      towns.value = Array.isArray(data) ? data : []
    } catch {
      towns.value = []
    }
  } else {
    towns.value = []
  }
}

function openCreateModal() {
  editingAddress.value = null
  form.value = {
    province: '',
    town: '',
    street_address: '',
    phone: userStore.user?.phone || '260',
    is_default: addresses.value.length === 0,
  }
  formError.value = ''
  towns.value = []
  showModal.value = true
}

async function openEditModal(address: Address) {
  editingAddress.value = address
  form.value = {
    province: address.province,
    town: address.town,
    street_address: address.street_address,
    phone: address.phone,
    is_default: address.is_default,
  }
  formError.value = ''
  if (address.province) {
    try {
      const data = await orderService.getTowns(address.province)
      towns.value = Array.isArray(data) ? data : []
    } catch {
      towns.value = []
    }
  }
  showModal.value = true
}

async function saveAddress() {
  if (!form.value.province || !form.value.town || !form.value.street_address || !form.value.phone) {
    formError.value = 'Please fill in all address fields.'
    return
  }
  if (!form.value.street_address.trim()) { formError.value = 'Enter a street address or landmark.'; return }
  if (!towns.value.some(t => t.id === form.value.town)) { formError.value = 'Select a town in the chosen province.'; return }
  if (!isZambianPhone(form.value.phone)) { formError.value = 'Enter a Zambian number, for example 0971234567 or +260971234567.'; return }
  saving.value = true
  formError.value = ''
  try {
    if (editingAddress.value) {
      await addressService.updateAddress(editingAddress.value.id, form.value)
      uiStore.showToast('Address updated.')
    } else {
      await addressService.createAddress(form.value)
      uiStore.showToast('Address saved.')
    }
    showModal.value = false
    await loadAddresses()
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    formError.value = detail || 'Could not save this address. Please try again.'
  } finally {
    saving.value = false
  }
}

async function deleteAddress(address: Address) {
  deletingId.value = address.id
  addressError.value = ''
  try {
    await addressService.deleteAddress(address.id)
    confirmDeleteId.value = null
    uiStore.showToast('Address removed.')
    await loadAddresses()
  } catch {
    addressError.value = 'Could not delete this address. Please try again.'
  } finally {
    deletingId.value = null
  }
}

async function setDefault(address: Address) {
  addressError.value = ''
  try {
    await addressService.updateAddress(address.id, { is_default: true })
    uiStore.showToast('Default delivery address updated.')
    await loadAddresses()
  } catch {
    addressError.value = 'Could not update your default address. Please try again.'
  }
}

onMounted(async () => {
  await Promise.all([loadAddresses(), loadProvinces(), loadOrders()])
})
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 py-8 sm:py-10">
    <div class="mb-7 flex flex-wrap items-end justify-between gap-4 border-b border-primary/40 pb-5">
      <div>
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-gold mb-1.5">Your Account</p>
        <h1 class="font-heading text-2xl sm:text-3xl font-semibold text-dark">Welcome, {{ userStore.user?.first_name || 'there' }}</h1>
      </div>
      <router-link
        v-if="userStore.isAdmin"
        to="/admin"
        class="inline-flex min-h-10 items-center gap-2 rounded-full border border-gold/40 bg-gold/10 px-4 text-xs font-semibold uppercase tracking-wider text-dark hover:bg-gold/20 transition-colors"
      >
        <LayoutDashboard class="w-4 h-4 text-gold" aria-hidden="true" />
        Admin Dashboard
      </router-link>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-start">
      <!-- Left sidebar: Identity & quick navigation -->
      <aside class="lg:col-span-4 space-y-5 lg:sticky lg:top-24">
        <div class="bg-white rounded-[20px] p-6 border border-primary/30 shadow-[0_8px_30px_rgba(0,0,0,0.04)]">
          <div class="flex items-center gap-4 mb-5">
            <div class="w-14 h-14 rounded-full bg-primary/50 flex items-center justify-center shrink-0">
              <span v-if="initials" class="font-heading text-lg font-semibold text-dark">{{ initials }}</span>
              <User v-else class="w-6 h-6 text-dark" aria-hidden="true" />
            </div>
            <div class="min-w-0">
              <p class="font-medium text-dark truncate">{{ fullName }}</p>
              <p class="text-xs text-muted truncate">{{ userStore.user?.email }}</p>
              <span
                v-if="userStore.user?.email_verified"
                class="mt-1.5 inline-flex items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-[11px] font-medium text-success"
              >
                <CheckCircle2 class="w-3 h-3" aria-hidden="true" />
                Verified email
              </span>
            </div>
          </div>

          <!-- Quick stats -->
          <div class="grid grid-cols-3 gap-2 border-y border-primary/20 py-3.5 mb-4 text-center">
            <router-link to="/account/orders" class="rounded-xl p-1.5 hover:bg-primary/15 transition-colors">
              <span class="block text-base font-semibold text-dark tabular-nums">{{ loadingOrders ? '–' : recentOrders.length }}</span>
              <span class="block text-[11px] text-muted">Orders</span>
            </router-link>
            <a href="#saved-addresses" class="rounded-xl p-1.5 hover:bg-primary/15 transition-colors">
              <span class="block text-base font-semibold text-dark tabular-nums">{{ loadingAddresses ? '–' : addresses.length }}</span>
              <span class="block text-[11px] text-muted">Addresses</span>
            </a>
            <router-link to="/wishlist" class="rounded-xl p-1.5 hover:bg-primary/15 transition-colors">
              <span class="block text-base font-semibold text-dark tabular-nums">{{ wishlistStore.count }}</span>
              <span class="block text-[11px] text-muted">Wishlist</span>
            </router-link>
          </div>

          <nav aria-label="Account sections" class="space-y-1">
            <a
              href="#personal-details"
              class="flex items-center gap-3 px-3 min-h-11 rounded-xl hover:bg-primary/20 transition-colors text-sm text-dark"
            >
              <User class="w-4 h-4 text-muted shrink-0" aria-hidden="true" />
              <span>Personal Details</span>
            </a>
            <router-link
              to="/account/orders"
              class="flex items-center justify-between gap-3 px-3 min-h-11 rounded-xl hover:bg-primary/20 transition-colors text-sm text-dark"
            >
              <span class="flex items-center gap-3">
                <Package class="w-4 h-4 text-muted shrink-0" aria-hidden="true" />
                <span>Order History</span>
              </span>
              <ChevronRight class="w-4 h-4 text-muted" aria-hidden="true" />
            </router-link>
            <a
              href="#saved-addresses"
              class="flex items-center gap-3 px-3 min-h-11 rounded-xl hover:bg-primary/20 transition-colors text-sm text-dark"
            >
              <MapPin class="w-4 h-4 text-muted shrink-0" aria-hidden="true" />
              <span>Saved Addresses</span>
            </a>
            <router-link
              to="/wishlist"
              class="flex items-center justify-between gap-3 px-3 min-h-11 rounded-xl hover:bg-primary/20 transition-colors text-sm text-dark"
            >
              <span class="flex items-center gap-3">
                <Heart class="w-4 h-4 text-muted shrink-0" aria-hidden="true" />
                <span>Wishlist</span>
              </span>
              <ChevronRight class="w-4 h-4 text-muted" aria-hidden="true" />
            </router-link>
            <a
              href="#security-help"
              class="flex items-center gap-3 px-3 min-h-11 rounded-xl hover:bg-primary/20 transition-colors text-sm text-dark"
            >
              <ShieldCheck class="w-4 h-4 text-muted shrink-0" aria-hidden="true" />
              <span>Security &amp; Support</span>
            </a>
            <div class="pt-2 mt-2 border-t border-primary/20">
              <button
                type="button"
                class="flex items-center gap-3 px-3 min-h-11 rounded-xl hover:bg-red-50 transition-colors w-full text-left text-sm text-red-600"
                @click="handleLogout"
              >
                <LogOut class="w-4 h-4 shrink-0" aria-hidden="true" />
                <span>Sign Out</span>
              </button>
            </div>
          </nav>
        </div>
      </aside>

      <!-- Right main column -->
      <div class="lg:col-span-8 space-y-6">
        <!-- Personal Details Section -->
        <section id="personal-details" class="scroll-mt-24 bg-white rounded-[20px] p-6 border border-primary/30 shadow-[0_8px_30px_rgba(0,0,0,0.04)]">
          <div class="flex items-center justify-between gap-3 mb-5">
            <div>
              <h2 class="font-heading text-lg font-semibold text-dark">Personal Details</h2>
              <p class="text-xs text-muted mt-0.5">Used to prefill checkout and send delivery updates.</p>
            </div>
            <BaseButton v-if="!editingProfile" size="sm" variant="outline" @click="startEditProfile">
              <Pencil class="w-3.5 h-3.5 mr-1.5" aria-hidden="true" /> Edit
            </BaseButton>
          </div>

          <form v-if="editingProfile" class="space-y-4" @submit.prevent="saveProfile">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <BaseInput
                id="profile-first-name"
                v-model="profileForm.first_name"
                label="First Name"
                required
              />
              <BaseInput
                id="profile-last-name"
                v-model="profileForm.last_name"
                label="Last Name"
              />
            </div>
            <BaseInput
              id="profile-phone"
              v-model="profileForm.phone"
              label="Phone Number"
              type="tel"
              placeholder="0971234567 or +260971234567"
            />
            <p class="text-xs text-muted -mt-2">We use this number for delivery SMS updates and mobile money prefill.</p>
            <p v-if="profileError" role="alert" class="text-sm text-red-700">{{ profileError }}</p>
            <div class="flex justify-end gap-3 pt-1">
              <BaseButton variant="ghost" @click="cancelEditProfile">Cancel</BaseButton>
              <BaseButton type="submit" variant="secondary" :loading="savingProfile">Save Changes</BaseButton>
            </div>
          </form>

          <dl v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
            <div class="rounded-xl bg-background/80 p-3.5 border border-primary/20">
              <dt class="text-xs text-muted mb-1">Full Name</dt>
              <dd class="font-medium text-dark">{{ fullName }}</dd>
            </div>
            <div class="rounded-xl bg-background/80 p-3.5 border border-primary/20">
              <dt class="text-xs text-muted mb-1">Email Address</dt>
              <dd class="font-medium text-dark break-all">{{ userStore.user?.email || '—' }}</dd>
            </div>
            <div class="rounded-xl bg-background/80 p-3.5 border border-primary/20 sm:col-span-2">
              <dt class="text-xs text-muted mb-1">Phone Number</dt>
              <dd class="font-medium text-dark">{{ userStore.user?.phone || 'Not added yet' }}</dd>
            </div>
          </dl>
        </section>

        <!-- Recent Orders Preview -->
        <section class="bg-white rounded-[20px] p-6 border border-primary/30 shadow-[0_8px_30px_rgba(0,0,0,0.04)]">
          <div class="flex items-center justify-between gap-3 mb-4">
            <h2 class="font-heading text-lg font-semibold text-dark">Recent Orders</h2>
            <router-link to="/account/orders" class="text-xs font-semibold uppercase tracking-wider text-gold underline underline-offset-4 hover:text-dark">
              View all
            </router-link>
          </div>

          <div v-if="loadingOrders" class="space-y-3" role="status" aria-live="polite">
            <div v-for="i in 2" :key="i" class="rounded-xl border border-primary/20 p-4">
              <div class="h-4 w-28 bg-primary/30 rounded animate-pulse mb-2" />
              <div class="h-3 w-44 bg-primary/20 rounded animate-pulse" />
            </div>
          </div>

          <div v-else-if="ordersError" role="alert" class="rounded-xl border border-primary/30 p-4 text-sm text-muted flex items-center justify-between gap-3">
            <span>Could not load your recent orders.</span>
            <button type="button" class="underline text-dark font-medium" @click="loadOrders">Try again</button>
          </div>

          <div v-else-if="recentOrders.length === 0" class="rounded-xl border border-dashed border-primary/50 p-6 text-center">
            <p class="text-sm font-medium text-dark">No orders yet</p>
            <p class="text-xs text-muted mt-1 mb-4">When you place an order, you can track its status and receipts here.</p>
            <router-link to="/catalog" class="inline-flex min-h-10 items-center justify-center rounded-full bg-dark px-5 text-xs font-semibold uppercase tracking-wider text-background hover:bg-dark/90">
              Browse products
            </router-link>
          </div>

          <div v-else class="space-y-3">
            <router-link
              v-for="order in recentOrders.slice(0, 3)"
              :key="order.id"
              :to="`/order/confirmation/${order.id}`"
              class="block rounded-xl border border-primary/30 p-4 hover:border-gold/60 hover:bg-primary/5 transition-colors"
            >
              <div class="flex items-center justify-between gap-2 mb-1.5">
                <span class="text-xs font-mono text-muted">#{{ order.id.slice(0, 8).toUpperCase() }}</span>
                <span
                  class="text-[11px] font-medium px-2.5 py-0.5 rounded-full capitalize"
                  :class="statusColors[order.status] || 'text-muted bg-primary/20'"
                >
                  {{ statusLabels[order.status] || order.status.replace('_', ' ') }}
                </span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-muted">
                  {{ new Date(order.created_at).toLocaleDateString('en-ZM', { year: 'numeric', month: 'short', day: 'numeric' }) }}
                  · {{ order.items.length }} item{{ order.items.length !== 1 ? 's' : '' }}
                </span>
                <span class="font-semibold text-dark tabular-nums">K{{ order.grand_total }}</span>
              </div>
            </router-link>
          </div>
        </section>

        <!-- Saved Addresses Section -->
        <section id="saved-addresses" class="scroll-mt-24 bg-white rounded-[20px] p-6 border border-primary/30 shadow-[0_8px_30px_rgba(0,0,0,0.04)]">
          <div class="flex items-center justify-between gap-3 mb-4">
            <div>
              <h2 class="font-heading text-lg font-semibold text-dark">Saved Addresses</h2>
              <p class="text-xs text-muted mt-0.5">Save your Lusaka or provincial delivery addresses for faster checkout.</p>
            </div>
            <BaseButton size="sm" @click="openCreateModal">
              <Plus class="w-4 h-4 mr-1" aria-hidden="true" /> Add Address
            </BaseButton>
          </div>

          <p v-if="addressError" role="alert" class="mb-4 text-sm text-red-700">{{ addressError }}</p>

          <div v-if="loadingAddresses" class="space-y-3" role="status" aria-live="polite">
            <div v-for="i in 2" :key="i" class="rounded-[14px] border border-primary/20 p-4">
              <div class="h-4 w-40 bg-primary/30 rounded animate-pulse mb-2" />
              <div class="h-3 w-32 bg-primary/20 rounded animate-pulse" />
            </div>
          </div>

          <div v-else-if="addressesLoadError" role="alert" class="rounded-xl border border-primary/30 p-4 text-sm text-muted flex items-center justify-between gap-3">
            <span>Could not load your saved addresses.</span>
            <button type="button" class="underline text-dark font-medium" @click="loadAddresses">Try again</button>
          </div>

          <div v-else-if="addresses.length === 0" class="rounded-xl border border-dashed border-primary/50 p-6 text-center text-muted text-sm">
            No saved addresses yet. Add one to speed up your next checkout.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="address in addresses"
              :key="address.id"
              class="p-4 border rounded-[14px] transition-colors"
              :class="address.is_default ? 'border-gold bg-gold/5' : 'border-primary/40'"
            >
              <div class="flex items-start justify-between gap-2">
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-2 mb-1">
                    <span class="text-sm font-medium text-dark">{{ address.street_address }}</span>
                    <span
                      v-if="address.is_default"
                      class="inline-flex items-center gap-1 text-[10px] font-medium text-gold bg-gold/10 px-2 py-0.5 rounded-full"
                    >
                      <Star class="w-2.5 h-2.5 fill-gold" aria-hidden="true" /> Default
                    </span>
                  </div>
                  <p class="text-xs text-muted">{{ address.town_name || address.town }}, {{ address.province_name || address.province }}</p>
                  <p class="text-xs text-muted mt-0.5">Phone: {{ address.phone }}</p>
                </div>
                <div class="flex items-center gap-1 shrink-0">
                  <button
                    v-if="!address.is_default"
                    type="button"
                    class="grid h-10 w-10 place-items-center hover:bg-primary/20 rounded-lg transition-colors text-muted focus-visible:outline-2 focus-visible:outline-gold"
                    aria-label="Set as default address"
                    title="Set as default"
                    @click="setDefault(address)"
                  >
                    <Star class="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    class="grid h-10 w-10 place-items-center hover:bg-primary/20 rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-gold"
                    aria-label="Edit address"
                    title="Edit"
                    @click="openEditModal(address)"
                  >
                    <Pencil class="w-4 h-4 text-muted" />
                  </button>
                  <button
                    type="button"
                    class="grid h-10 w-10 place-items-center hover:bg-red-50 rounded-lg transition-colors focus-visible:outline-2 focus-visible:outline-gold"
                    aria-label="Delete address"
                    title="Delete"
                    @click="confirmDeleteId = confirmDeleteId === address.id ? null : address.id"
                  >
                    <Trash2 class="w-4 h-4 text-red-500" />
                  </button>
                </div>
              </div>
              <div v-if="confirmDeleteId === address.id" class="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-primary/20 pt-3 text-xs">
                <span class="text-dark">Remove this saved address?</span>
                <div class="flex items-center gap-2">
                  <button type="button" class="min-h-9 px-3 rounded-lg border border-primary/40 text-dark hover:bg-primary/15" @click="confirmDeleteId = null">Cancel</button>
                  <button type="button" class="min-h-9 px-3 rounded-lg bg-red-600 text-white font-medium hover:bg-red-700 disabled:opacity-50" :disabled="deletingId === address.id" @click="deleteAddress(address)">
                    {{ deletingId === address.id ? 'Removing…' : 'Remove' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Security & Support Section -->
        <section id="security-help" class="scroll-mt-24 bg-white rounded-[20px] p-6 border border-primary/30 shadow-[0_8px_30px_rgba(0,0,0,0.04)]">
          <h2 class="font-heading text-lg font-semibold text-dark mb-4">Security &amp; Support</h2>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <router-link
              to="/auth/forgot-password"
              class="flex items-center gap-3 rounded-xl border border-primary/30 p-4 hover:border-gold/60 hover:bg-primary/5 transition-colors"
            >
              <div class="w-10 h-10 rounded-full bg-primary/30 flex items-center justify-center shrink-0">
                <KeyRound class="w-4 h-4 text-dark" aria-hidden="true" />
              </div>
              <div class="min-w-0">
                <p class="text-sm font-medium text-dark">Reset Password</p>
                <p class="text-xs text-muted">Request a password reset link</p>
              </div>
            </router-link>
            <router-link
              to="/help"
              class="flex items-center gap-3 rounded-xl border border-primary/30 p-4 hover:border-gold/60 hover:bg-primary/5 transition-colors"
            >
              <div class="w-10 h-10 rounded-full bg-primary/30 flex items-center justify-center shrink-0">
                <HelpCircle class="w-4 h-4 text-dark" aria-hidden="true" />
              </div>
              <div class="min-w-0">
                <p class="text-sm font-medium text-dark">Help &amp; Returns</p>
                <p class="text-xs text-muted">Delivery info, FAQs, and contact</p>
              </div>
            </router-link>
          </div>
        </section>
      </div>
    </div>

    <!-- Add/Edit Address Modal -->
    <BaseModal :open="showModal" :title="editingAddress ? 'Edit Address' : 'Add Address'" @close="showModal = false">
      <div class="space-y-4">
        <BaseSelect
          v-model="form.province"
          label="Province"
          :options="provinceOptions"
          required
          @update:modelValue="handleProvinceChange"
        />
        <BaseSelect
          v-model="form.town"
          label="Town / City"
          :options="townOptions"
          required
          :disabled="!form.province"
        />
        <BaseInput v-model="form.street_address" label="Street Address" required placeholder="Street, building, landmark" />
        <BaseInput v-model="form.phone" label="Phone Number" type="tel" required placeholder="260xxxxxxxxx" />
        <p class="text-xs text-muted -mt-2">For delivery updates via SMS</p>
        <div class="flex items-center gap-2">
          <input id="is_default" v-model="form.is_default" type="checkbox" class="rounded accent-gold" />
          <label for="is_default" class="text-sm text-dark">Set as default address</label>
        </div>
        <p v-if="formError" role="alert" class="text-sm text-red-700">{{ formError }}</p>
        <div class="flex justify-end gap-3 pt-2">
          <BaseButton variant="ghost" @click="showModal = false">Cancel</BaseButton>
          <BaseButton :loading="saving" @click="saveAddress">
            {{ editingAddress ? 'Update' : 'Save' }}
          </BaseButton>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

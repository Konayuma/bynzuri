<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { addressService } from '@/services/address.service'
import { orderService } from '@/services/order.service'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseModal from '@/components/base/BaseModal.vue'
import { User, Package, MapPin, LogOut, Plus, Pencil, Trash2, Star } from '@lucide/vue'
import type { Address, Province, Town } from '@/types'

const userStore = useUserStore()
const router = useRouter()

const addresses = ref<Address[]>([])
const loadingAddresses = ref(true)
const showModal = ref(false)
const editingAddress = ref<Address | null>(null)
const saving = ref(false)
const formError = ref('')

const provinces = ref<Province[]>([])
const towns = ref<Town[]>([])

const form = ref({
  province: '',
  town: '',
  street_address: '',
  phone: '260',
  is_default: false,
})

function handleLogout() {
  userStore.logout()
  router.push('/')
}

async function loadAddresses() {
  loadingAddresses.value = true
  try {
    addresses.value = await addressService.getAddresses()
  } catch {
    addresses.value = []
  } finally {
    loadingAddresses.value = false
  }
}

async function loadProvinces() {
  try {
    provinces.value = await orderService.getProvinces()
  } catch {
    provinces.value = []
  }
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

function openCreateModal() {
  editingAddress.value = null
  form.value = { province: '', town: '', street_address: '', phone: '260', is_default: false }
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
    towns.value = await orderService.getTowns(address.province)
  }
  showModal.value = true
}

async function saveAddress() {
  if (!form.value.province || !form.value.town || !form.value.street_address || !form.value.phone) {
    formError.value = 'Please fill in all address fields'
    return
  }
  saving.value = true
  formError.value = ''
  try {
    if (editingAddress.value) {
      await addressService.updateAddress(editingAddress.value.id, form.value)
    } else {
      await addressService.createAddress(form.value)
    }
    showModal.value = false
    await loadAddresses()
  } catch (e: any) {
    formError.value = e.response?.data?.detail || 'Could not save this address. Please try again.'
  } finally {
    saving.value = false
  }
}

async function deleteAddress(address: Address) {
  if (!confirm('Delete this address? It will be removed from your saved addresses.')) return
  try {
    await addressService.deleteAddress(address.id)
    await loadAddresses()
  } catch {
    /* ignore */
  }
}

async function setDefault(address: Address) {
  try {
    await addressService.updateAddress(address.id, { is_default: true })
    await loadAddresses()
  } catch {
    /* ignore */
  }
}

onMounted(async () => {
  await Promise.all([loadAddresses(), loadProvinces()])
})
</script>

<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="font-heading text-2xl font-semibold text-dark mb-6">My Account</h1>

    <div class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)] mb-6">
      <div class="flex items-center gap-4 mb-4">
        <div class="w-14 h-14 rounded-full bg-primary/50 flex items-center justify-center">
          <User class="w-6 h-6 text-dark" />
        </div>
        <div>
          <p class="font-medium text-dark">{{ userStore.user?.first_name }} {{ userStore.user?.last_name }}</p>
          <p class="text-sm text-muted">{{ userStore.user?.email }}</p>
        </div>
      </div>

      <div class="space-y-3">
        <router-link
          to="/account/orders"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-primary/20 transition-colors"
        >
          <Package class="w-4 h-4 text-muted" />
          <span class="text-sm text-dark">Order History</span>
        </router-link>
        <button
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-primary/20 transition-colors w-full text-left"
        >
          <MapPin class="w-4 h-4 text-muted" />
          <span class="text-sm text-dark">Saved Addresses</span>
        </button>
        <button
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-red-50 transition-colors w-full text-left text-red-500"
          @click="handleLogout"
        >
          <LogOut class="w-4 h-4" />
          <span class="text-sm">Sign Out</span>
        </button>
      </div>
    </div>

    <!-- Saved Addresses Section -->
    <div class="bg-white rounded-[20px] p-6 shadow-[0_8px_30px_rgba(0,0,0,0.06)]">
      <div class="flex items-center justify-between mb-4">
        <h2 class="font-heading text-lg font-semibold text-dark">Saved Addresses</h2>
        <BaseButton size="sm" @click="openCreateModal">
          <Plus class="w-4 h-4 mr-1" /> Add Address
        </BaseButton>
      </div>

      <div v-if="loadingAddresses" class="text-center py-6 text-muted text-sm">Loading...</div>

      <div v-else-if="addresses.length === 0" class="text-center py-6 text-muted text-sm">
        No saved addresses yet. Add one to speed up your next checkout.
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="address in addresses"
          :key="address.id"
          class="p-4 border rounded-[14px] transition-colors"
          :class="address.is_default ? 'border-gold bg-gold/5' : 'border-primary/40'"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-1">
                <span class="text-sm font-medium text-dark">{{ address.street_address }}</span>
                <span
                  v-if="address.is_default"
                  class="inline-flex items-center gap-1 text-[10px] font-medium text-gold bg-gold/10 px-2 py-0.5 rounded-full"
                >
                  <Star class="w-2.5 h-2.5 fill-gold" /> Default
                </span>
              </div>
              <p class="text-xs text-muted">{{ address.town_name || address.town }}, {{ address.province_name || address.province }}</p>
              <p class="text-xs text-muted mt-0.5">Phone: {{ address.phone }}</p>
            </div>
            <div class="flex items-center gap-1">
              <button
                v-if="!address.is_default"
                class="p-1.5 hover:bg-primary/20 rounded-lg transition-colors text-xs text-muted"
                title="Set as default"
                @click="setDefault(address)"
              >
                <Star class="w-3.5 h-3.5" />
              </button>
              <button
                class="p-1.5 hover:bg-primary/20 rounded-lg transition-colors"
                title="Edit"
                @click="openEditModal(address)"
              >
                <Pencil class="w-3.5 h-3.5 text-muted" />
              </button>
              <button
                class="p-1.5 hover:bg-red-50 rounded-lg transition-colors"
                title="Delete"
                @click="deleteAddress(address)"
              >
                <Trash2 class="w-3.5 h-3.5 text-red-400" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Address Modal -->
    <BaseModal :open="showModal" :title="editingAddress ? 'Edit Address' : 'Add Address'" @close="showModal = false">
      <div class="space-y-4">
        <BaseSelect
          v-model="form.province"
          label="Province"
          :options="provinces.map(p => ({ value: p.id, label: p.name }))"
          required
          @update:modelValue="handleProvinceChange"
        />
        <BaseSelect
          v-model="form.town"
          label="Town / City"
          :options="towns.map(t => ({ value: t.id, label: t.name }))"
          required
          :disabled="!form.province"
        />
        <BaseInput v-model="form.street_address" label="Street Address" required placeholder="Street, building, landmark" />
        <BaseInput v-model="form.phone" label="Phone Number" type="tel" required placeholder="260xxxxxxxxx" />
        <p class="text-xs text-muted -mt-2">For delivery updates via SMS</p>
        <div class="flex items-center gap-2">
          <input id="is_default" v-model="form.is_default" type="checkbox" class="rounded" />
          <label for="is_default" class="text-sm text-gray-600">Set as default address</label>
        </div>
        <p v-if="formError" class="text-sm text-red-500">{{ formError }}</p>
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

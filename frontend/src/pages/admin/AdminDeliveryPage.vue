<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseModal from '@/components/base/BaseModal.vue'
import BaseTabs from '@/components/base/BaseTabs.vue'
import { adminService } from '@/services/admin.service'
import type { AdminProvince, AdminTown, AdminDeliveryMethod } from '@/types'
import { Plus, Pencil, Trash2 } from '@lucide/vue'

const activeTab = ref('provinces')

const tabs = [
  { value: 'provinces', label: 'Provinces' },
  { value: 'towns', label: 'Towns' },
  { value: 'methods', label: 'Delivery Methods' },
]

const provinces = ref<AdminProvince[]>([])
const towns = ref<AdminTown[]>([])
const methods = ref<AdminDeliveryMethod[]>([])

const loading = ref(false)
const showModal = ref(false)
const editing = ref(false)
const saving = ref(false)
const formError = ref('')

const provinceForm = ref({ name: '', slug: '', sort_order: 0 })
const townForm = ref({ province: '', name: '', slug: '' })
const methodForm = ref({ name: '', description: '', price: '', estimated_days: '', is_active: true, sort_order: 0 })
const editingId = ref<string | null>(null)

async function loadData() {
  loading.value = true
  try {
    const [p, t, m] = await Promise.all([
      adminService.getProvinces(),
      adminService.getTowns(),
      adminService.getDeliveryMethods(),
    ])
    provinces.value = p
    towns.value = t
    methods.value = m
  } finally {
    loading.value = false
  }
}

const provinceOptions = computed(() =>
  provinces.value.map(p => ({ value: p.id, label: p.name }))
)

function openCreate() {
  editing.value = false
  editingId.value = null
  formError.value = ''

  if (activeTab.value === 'provinces') {
    provinceForm.value = { name: '', slug: '', sort_order: 0 }
  } else if (activeTab.value === 'towns') {
    townForm.value = { province: provinceOptions.value[0]?.value || '', name: '', slug: '' }
  } else {
    methodForm.value = { name: '', description: '', price: '', estimated_days: '', is_active: true, sort_order: 0 }
  }
  showModal.value = true
}

function openEdit(item: any) {
  editing.value = true
  editingId.value = item.id
  formError.value = ''

  if (activeTab.value === 'provinces') {
    provinceForm.value = { name: item.name, slug: item.slug, sort_order: item.sort_order }
  } else if (activeTab.value === 'towns') {
    townForm.value = { province: item.province, name: item.name, slug: item.slug }
  } else {
    methodForm.value = {
      name: item.name,
      description: item.description,
      price: item.price,
      estimated_days: item.estimated_days,
      is_active: item.is_active,
      sort_order: item.sort_order,
    }
  }
  showModal.value = true
}

async function save() {
  saving.value = true
  formError.value = ''
  try {
    if (activeTab.value === 'provinces') {
      if (!provinceForm.value.name) { formError.value = 'Name is required'; saving.value = false; return }
      if (editing.value && editingId.value) {
        await adminService.updateProvince(editingId.value, provinceForm.value)
      } else {
        await adminService.createProvince(provinceForm.value)
      }
    } else if (activeTab.value === 'towns') {
      if (!townForm.value.name || !townForm.value.province) { formError.value = 'Name and province are required'; saving.value = false; return }
      if (editing.value && editingId.value) {
        await adminService.updateTown(editingId.value, townForm.value)
      } else {
        await adminService.createTown(townForm.value)
      }
    } else {
      if (!methodForm.value.name.trim() || !methodForm.value.price.trim()) { formError.value = 'Name and price are required'; saving.value = false; return }
      if (!Number.isFinite(Number(methodForm.value.price)) || Number(methodForm.value.price) < 0) { formError.value = 'Enter a valid price of zero or more'; saving.value = false; return }
      if (editing.value && editingId.value) {
        await adminService.updateDeliveryMethod(editingId.value, methodForm.value)
      } else {
        await adminService.createDeliveryMethod(methodForm.value)
      }
    }
    showModal.value = false
    await loadData()
  } catch (e: any) {
    formError.value = e.response?.data?.detail || e.response?.data?.name?.[0] || 'Failed to save'
  } finally {
    saving.value = false
  }
}

async function remove(item: any) {
  if (!confirm(`Delete "${item.name || item.title}"?`)) return
  try {
    if (activeTab.value === 'provinces') {
      await adminService.deleteProvince(item.id)
    } else if (activeTab.value === 'towns') {
      await adminService.deleteTown(item.id)
    } else {
      await adminService.deleteDeliveryMethod(item.id)
    }
    await loadData()
  } catch { /* ignore */ }
}

onMounted(loadData)
</script>

<template>
  <AdminLayout>
    <div>
      <div class="flex items-center justify-between mb-4">
        <h1 class="font-heading text-xl font-semibold">Delivery Management</h1>
        <BaseButton size="sm" @click="openCreate">
          <Plus class="w-4 h-4 mr-1" /> Add
        </BaseButton>
      </div>

      <BaseTabs v-model="activeTab" :tabs="tabs" />

      <div v-if="loading" class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <div class="p-8 text-center text-gray-600" role="status" aria-live="polite">Loading delivery settings…</div>
      </div>

      <div v-else class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <!-- Provinces Tab -->
        <table v-if="activeTab === 'provinces'" class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Name</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Slug</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Sort</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in provinces" :key="item.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-3 font-medium">{{ item.name }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ item.slug }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ item.sort_order }}</td>
              <td class="px-4 py-3 text-right">
                <button class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors" title="Edit" @click="openEdit(item)">
                  <Pencil class="w-4 h-4 text-gray-400" />
                </button>
                <button class="p-1.5 hover:bg-red-50 rounded-lg transition-colors ml-1" title="Delete" @click="remove(item)">
                  <Trash2 class="w-4 h-4 text-red-400" />
                </button>
              </td>
            </tr>
            <tr v-if="provinces.length === 0">
              <td colspan="4" class="px-4 py-8 text-center text-gray-400">No provinces yet.</td>
            </tr>
          </tbody>
        </table>

        <!-- Towns Tab -->
        <table v-if="activeTab === 'towns'" class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Name</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Province</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Slug</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in towns" :key="item.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-3 font-medium">{{ item.name }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ item.province_name }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ item.slug }}</td>
              <td class="px-4 py-3 text-right">
                <button class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors" title="Edit" @click="openEdit(item)">
                  <Pencil class="w-4 h-4 text-gray-400" />
                </button>
                <button class="p-1.5 hover:bg-red-50 rounded-lg transition-colors ml-1" title="Delete" @click="remove(item)">
                  <Trash2 class="w-4 h-4 text-red-400" />
                </button>
              </td>
            </tr>
            <tr v-if="towns.length === 0">
              <td colspan="4" class="px-4 py-8 text-center text-gray-400">No towns yet.</td>
            </tr>
          </tbody>
        </table>

        <!-- Delivery Methods Tab -->
        <table v-if="activeTab === 'methods'" class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Name</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Price</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Est. Days</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Active</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in methods" :key="item.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-3 font-medium">{{ item.name }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">K{{ item.price }}</td>
              <td class="px-4 py-3 text-gray-500 hidden md:table-cell">{{ item.estimated_days }}</td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="item.is_active ? 'text-green-600' : 'text-red-500'">{{ item.is_active ? 'Yes' : 'No' }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <button class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors" title="Edit" @click="openEdit(item)">
                  <Pencil class="w-4 h-4 text-gray-400" />
                </button>
                <button class="p-1.5 hover:bg-red-50 rounded-lg transition-colors ml-1" title="Delete" @click="remove(item)">
                  <Trash2 class="w-4 h-4 text-red-400" />
                </button>
              </td>
            </tr>
            <tr v-if="methods.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-gray-400">No delivery methods yet.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Create / Edit Modal -->
      <BaseModal
        :open="showModal"
        :title="editing ? 'Edit' : 'Add'"
        @close="showModal = false"
      >
        <div class="space-y-4">
          <!-- Province Form -->
          <template v-if="activeTab === 'provinces'">
            <BaseInput v-model="provinceForm.name" label="Name" required />
            <BaseInput v-model="provinceForm.slug" label="Slug" placeholder="leave blank to auto-generate" />
            <BaseInput :model-value="String(provinceForm.sort_order)" @update:model-value="provinceForm.sort_order = Number($event)" label="Sort Order" type="number" />
          </template>

          <!-- Town Form -->
          <template v-if="activeTab === 'towns'">
            <BaseSelect
              v-model="townForm.province"
              label="Province"
              :options="provinceOptions"
            />
            <BaseInput v-model="townForm.name" label="Name" required />
            <BaseInput v-model="townForm.slug" label="Slug" placeholder="leave blank to auto-generate" />
          </template>

          <!-- Delivery Method Form -->
          <template v-if="activeTab === 'methods'">
            <BaseInput v-model="methodForm.name" label="Name" required />
            <BaseInput v-model="methodForm.description" label="Description" />
            <div class="grid grid-cols-2 gap-4">
              <BaseInput v-model="methodForm.price" label="Price (ZMW)" type="number" required />
              <BaseInput v-model="methodForm.estimated_days" label="Est. Days" placeholder="e.g. 1-3 business days" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <BaseInput :model-value="String(methodForm.sort_order)" @update:model-value="methodForm.sort_order = Number($event)" label="Sort Order" type="number" />
              <div class="flex items-end pb-3">
                <label class="flex items-center gap-2 text-sm text-gray-600">
                  <input v-model="methodForm.is_active" type="checkbox" class="rounded" />
                  Active
                </label>
              </div>
            </div>
          </template>

          <p v-if="formError" role="alert" class="text-sm text-red-700">{{ formError }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <BaseButton variant="ghost" @click="showModal = false">Cancel</BaseButton>
            <BaseButton :loading="saving" @click="save">{{ editing ? 'Update' : 'Create' }}</BaseButton>
          </div>
        </div>
      </BaseModal>
    </div>
  </AdminLayout>
</template>

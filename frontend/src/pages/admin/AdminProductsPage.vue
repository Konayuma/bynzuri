<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import BaseButton from '@/components/base/BaseButton.vue'
import BaseInput from '@/components/base/BaseInput.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseModal from '@/components/base/BaseModal.vue'
import { productService } from '@/services/product.service'
import type { Product, Category, ProductCreateData, PaginatedResponse, ProductImage } from '@/types'
import { Plus, Pencil, Trash2, Upload, X, ImageIcon } from '@lucide/vue'

const products = ref<Product[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)
const showModal = ref(false)
const editingProduct = ref<Product | null>(null)
const saving = ref(false)
const page = ref(1)
const totalCount = ref(0)
const nextPage = ref(false)
const listError = ref('')
const importing = ref(false)
const categoryLoading = ref(false)
const categoryLoadError = ref('')
const addingCategory = ref(false)
const categoryName = ref('')
const categoryError = ref('')
const savingCategory = ref(false)
const importResult = ref<{ created: string[]; skipped: string[] } | null>(null)

const form = ref<ProductCreateData>({
  category: '',
  title: '',
  slug: '',
  description: '',
  price: '',
  stock: 0,
  is_active: true,
  is_featured: false,
})

const stockStr = ref('0')
const formError = ref('')
const imageFiles = ref<File[]>([])
const imagePreviews = ref<string[]>([])
const uploadingImages = ref(false)
const currentImages = ref<ProductImage[]>([])

async function importSignature() {
  if (!confirm('Import the eight existing signature products and prices? Existing products will be kept unchanged. New products will have zero stock.')) return
  importing.value = true
  listError.value = ''
  importResult.value = null
  try {
    importResult.value = await productService.importSignatureCatalog()
    page.value = 1
    await Promise.all([loadProducts(), loadCategories()])
  } catch {
    listError.value = 'The import could not be completed. Please try again.'
  } finally {
    importing.value = false
  }
}

async function loadProducts() {
  loading.value = true
  try {
    listError.value = ''
    const data = await productService.getManagedProducts(page.value)
    nextPage.value = !!data.next
    products.value = data.results
    totalCount.value = data.count
  } catch {
    listError.value = 'Could not load products. Please try again.'
    products.value = []
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  categoryLoading.value = true
  categoryLoadError.value = ''
  try {
    categories.value = await productService.getCategories()
  } catch {
    categoryLoadError.value = 'Could not load categories. Check your connection and try again.'
  } finally {
    categoryLoading.value = false
  }
}

async function createCategory() {
  if (savingCategory.value) return
  const name = categoryName.value.trim()
  if (!name) {
    categoryError.value = 'Enter a category name.'
    return
  }
  savingCategory.value = true
  categoryError.value = ''
  try {
    const category = await productService.createCategory(name)
    categories.value = [...categories.value.filter(c => c.id !== category.id), category]
    form.value.category = category.id
    categoryName.value = ''
    addingCategory.value = false
    categoryLoadError.value = ''
  } catch (error: any) {
    const data = error.response?.data
    categoryError.value = data?.name?.[0] || data?.slug?.[0] || data?.detail || 'Could not create the category. Please try again.'
  } finally {
    savingCategory.value = false
  }
}

function openCreateModal() {
  editingProduct.value = null
  form.value = {
    category: categories.value[0]?.id || '',
    title: '',
    slug: '',
    description: '',
    price: '',
    stock: 0,
    is_active: true,
    is_featured: false,
  }
  stockStr.value = '0'
  formError.value = ''
  addingCategory.value = false
  categoryName.value = ''
  categoryError.value = ''
  imageFiles.value = []
  imagePreviews.value = []
  currentImages.value = []
  showModal.value = true
}

function openEditModal(product: Product) {
  editingProduct.value = product
  form.value = {
    category: product.category,
    title: product.title,
    slug: product.slug,
    description: product.description,
    price: product.price,
    stock: product.stock,
    is_active: product.is_active ?? true,
    is_featured: product.is_featured ?? false,
  }
  stockStr.value = String(product.stock)
  formError.value = ''
  addingCategory.value = false
  categoryName.value = ''
  categoryError.value = ''
  imageFiles.value = []
  imagePreviews.value = []
  currentImages.value = [...product.images]
  showModal.value = true
}

function handleImageSelect(event: Event) {
  const input = event.target as HTMLInputElement
  if (!input.files) return
  for (const file of Array.from(input.files)) {
    imageFiles.value.push(file)
    imagePreviews.value.push(URL.createObjectURL(file))
  }
  input.value = ''
}

function removeNewImage(index: number) {
  URL.revokeObjectURL(imagePreviews.value[index])
  imageFiles.value.splice(index, 1)
  imagePreviews.value.splice(index, 1)
}

async function removeExistingImage(image: ProductImage) {
  if (!editingProduct.value) return
  try {
    await productService.deleteProductImage(editingProduct.value.slug, image.id)
    currentImages.value = currentImages.value.filter(i => i.id !== image.id)
  } catch {
    formError.value = 'Could not remove the image. Please try again.'
  }
}

async function uploadImages(slug: string) {
  if (imageFiles.value.length === 0) return
  uploadingImages.value = true
  try {
    for (let i = 0; i < imageFiles.value.length; i++) {
      const formData = new FormData()
      formData.append('image', imageFiles.value[i])
      formData.append('alt_text', form.value.title)
      formData.append('is_primary', i === 0 && currentImages.value.length === 0 ? 'true' : 'false')
      formData.append('sort_order', String(currentImages.value.length + i))
      await productService.uploadProductImage(slug, formData)
    }
  } finally {
    uploadingImages.value = false
  }
}

async function saveProduct() {
  if (!form.value.title.trim() || !form.value.category || !form.value.price.trim()) {
    formError.value = 'Enter a title, category and price.'
    return
  }
  if (!Number.isFinite(Number(form.value.price)) || Number(form.value.price) < 0) {
    formError.value = 'Enter a valid price of zero or more.'
    return
  }
  if (!/^\d+$/.test(stockStr.value) || !Number.isSafeInteger(Number(stockStr.value))) {
    formError.value = 'Stock must be a whole number of zero or more.'
    return
  }
  saving.value = true
  formError.value = ''
  form.value.stock = Number(stockStr.value)
  try {
    let slug: string
    if (editingProduct.value) {
      const updated = await productService.updateProduct(editingProduct.value.slug, form.value)
      slug = updated.slug
    } else {
      const created = await productService.createProduct(form.value)
      slug = created.slug
      editingProduct.value = created
    }
    await uploadImages(slug)
    showModal.value = false
    await loadProducts()
  } catch (e: any) {
    formError.value = e.response?.data?.detail || e.response?.data?.title?.[0] || 'Failed to save product'
  } finally {
    saving.value = false
  }
}

async function deleteProduct(product: Product) {
  if (!confirm(`Delete "${product.title}"?`)) return
  try {
    await productService.deleteProduct(product.slug)
    await loadProducts()
  } catch {
    listError.value = 'Could not delete the product. Please try again.'
  }
}

onMounted(async () => {
  await Promise.all([loadProducts(), loadCategories()])
})
</script>

<template>
  <AdminLayout>
    <div>
      <div class="flex flex-wrap gap-3 items-center justify-between mb-6">
        <h1 class="font-heading text-xl font-semibold">Products ({{ totalCount }})</h1>
        <div class="flex flex-wrap gap-2">
        <BaseButton size="sm" variant="secondary" :loading="importing" @click="importSignature">Import existing products</BaseButton>
        <BaseButton size="sm" @click="openCreateModal">
          <Plus class="w-4 h-4 mr-1" /> Add Product
        </BaseButton>
        </div>
      </div>

      <div v-if="importResult" role="status" class="mb-4 rounded-lg bg-green-50 p-4 text-sm text-green-900">
        <p>Imported {{ importResult.created.length }} products. Kept {{ importResult.skipped.length }} existing products unchanged.</p>
        <p v-if="importResult.created.length">Added: {{ importResult.created.join(', ') }}. Set stock after checking availability.</p>
        <p v-if="importResult.skipped.length">Already present: {{ importResult.skipped.join(', ') }}.</p>
      </div>
      <p v-if="listError" role="alert" class="mb-4 text-sm text-red-700">{{ listError }}</p>
      <div v-if="loading" class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <div class="p-8 text-center text-gray-400">Loading...</div>
      </div>

      <div v-else class="bg-white rounded-[16px] border border-gray-100 overflow-hidden">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-gray-100">
              <th class="text-left px-4 py-3 font-medium text-gray-500">Product</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Category</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500">Price</th>
              <th class="text-left px-4 py-3 font-medium text-gray-500 hidden md:table-cell">Stock</th>
              <th class="text-right px-4 py-3 font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="product in products" :key="product.id" class="border-b border-gray-50 hover:bg-gray-50">
              <td class="px-4 py-3">{{ product.title }}</td>
              <td class="px-4 py-3 hidden md:table-cell text-gray-500">{{ product.category_name }}</td>
              <td class="px-4 py-3">K{{ product.price }}</td>
              <td class="px-4 py-3 hidden md:table-cell">
                <span :class="product.stock <= 5 ? 'text-red-500 font-medium' : ''">
                  {{ product.stock }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button class="p-1.5 hover:bg-gray-100 rounded-lg transition-colors" title="Edit" @click="openEditModal(product)">
                  <Pencil class="w-4 h-4 text-gray-400" />
                </button>
                <button class="p-1.5 hover:bg-red-50 rounded-lg transition-colors ml-1" title="Delete" @click="deleteProduct(product)">
                  <Trash2 class="w-4 h-4 text-red-400" />
                </button>
              </td>
            </tr>
            <tr v-if="products.length === 0">
              <td colspan="5" class="px-4 py-8 text-center text-gray-400">
                No products yet. Add your first product.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex items-center justify-between mt-4 text-sm">
        <button :disabled="page === 1 || loading" @click="page--; loadProducts()">Previous</button>
        <span>Page {{ page }}</span>
        <button :disabled="!nextPage || loading" @click="page++; loadProducts()">Next</button>
      </div>

      <BaseModal :open="showModal" :title="editingProduct ? 'Edit Product' : 'Add Product'" @close="showModal = false">
        <div class="space-y-4">
          <BaseInput v-model="form.title" label="Title" required />
          <BaseInput v-model="form.slug" label="Slug" placeholder="leave blank to auto-generate" />
          <div class="space-y-2">
            <BaseSelect
              v-model="form.category"
              label="Category"
              required
              :disabled="categoryLoading || categories.length === 0"
              :options="categories.map(c => ({ value: c.id, label: c.name }))"
            />
            <p v-if="categoryLoading" class="text-sm text-gray-600">Loading categories…</p>
            <p v-else-if="categoryLoadError" role="alert" class="text-sm text-red-700">
              {{ categoryLoadError }} <button type="button" class="underline" @click="loadCategories">Retry</button>
            </p>
            <p v-else-if="categories.length === 0" class="text-sm text-gray-600">No categories yet. Add one below.</p>
            <button v-if="!addingCategory" type="button" class="text-sm font-medium underline" @click="addingCategory = true">Add a category</button>
            <div v-else class="space-y-2 rounded-xl border border-primary/40 p-3">
              <BaseInput v-model="categoryName" label="New category name" maxlength="100" :error="categoryError" />
              <div class="flex flex-wrap gap-2">
                <BaseButton size="sm" :loading="savingCategory" @click="createCategory">Create category</BaseButton>
                <BaseButton size="sm" variant="ghost" :disabled="savingCategory" @click="addingCategory = false; categoryError = ''">Cancel</BaseButton>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <BaseInput v-model="form.price" label="Price (ZMW)" type="number" required />
            <BaseInput v-model="stockStr" label="Stock" type="number" />
          </div>
          <div>
            <label class="block text-sm font-medium text-dark mb-1.5">Description</label>
            <textarea
              v-model="form.description"
              class="w-full px-4 py-3 bg-white border border-primary/40 rounded-[14px] text-sm text-dark placeholder:text-muted/60 focus:outline-none focus:border-gold transition-colors"
              rows="3"
            />
          </div>
          <div class="flex items-center gap-2">
            <input id="is_active" v-model="form.is_active" type="checkbox" class="rounded" />
            <label for="is_active" class="text-sm text-gray-600">Active</label>
          </div>

          <div>
            <label class="block text-sm font-medium text-dark mb-1.5">Product Images</label>
            <div v-if="currentImages.length > 0" class="flex flex-wrap gap-3 mb-3">
              <div
                v-for="img in currentImages"
                :key="img.id"
                class="relative group w-20 h-20 rounded-lg overflow-hidden border border-primary/40"
              >
                <img :src="img.image" :alt="img.alt_text" class="w-full h-full object-cover" />
                <button
                  type="button"
                  class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                  @click="removeExistingImage(img)"
                >
                  <X class="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
            <div v-if="imagePreviews.length > 0" class="flex flex-wrap gap-3 mb-3">
              <div
                v-for="(preview, i) in imagePreviews"
                :key="i"
                class="relative group w-20 h-20 rounded-lg overflow-hidden border border-primary/40"
              >
                <img :src="preview" class="w-full h-full object-cover" />
                <button
                  type="button"
                  class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
                  @click="removeNewImage(i)"
                >
                  <X class="w-4 h-4 text-white" />
                </button>
              </div>
            </div>
            <label class="flex items-center gap-2 px-4 py-3 border border-dashed border-primary/40 rounded-[14px] cursor-pointer hover:bg-primary/10 transition-colors">
              <Upload class="w-4 h-4 text-muted" />
              <span class="text-sm text-muted">Add images</span>
              <input type="file" multiple accept="image/*" class="hidden" @change="handleImageSelect" />
            </label>
          </div>

          <p v-if="formError" role="alert" class="text-sm text-red-700">{{ formError }}</p>
          <div class="flex justify-end gap-3 pt-2">
            <BaseButton variant="ghost" @click="showModal = false">Cancel</BaseButton>
            <BaseButton :loading="saving || uploadingImages" @click="saveProduct">
              {{ editingProduct ? 'Update' : 'Create' }}
            </BaseButton>
          </div>
        </div>
      </BaseModal>
    </div>
  </AdminLayout>
</template>

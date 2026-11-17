<script setup lang="ts">
import { computed, useId } from 'vue'
defineOptions({ inheritAttrs: false })
const props = defineProps<{
  modelValue: string
  label?: string
  options: { value: string; label: string }[]
  placeholder?: string
  error?: string
  required?: boolean
  disabled?: boolean
  id?: string
}>()
defineEmits<{ 'update:modelValue': [value: string] }>()
const generatedId = useId()
const inputId = computed(() => props.id || generatedId)
</script>

<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="inputId" class="block text-sm font-semibold text-dark">
      {{ label }} <span v-if="required" class="text-gold" aria-hidden="true">*</span>
    </label>
    <select v-bind="$attrs" :id="inputId" :value="modelValue" :required="required" :disabled="disabled"
      :aria-invalid="error ? 'true' : undefined" :aria-describedby="error ? `${inputId}-error` : undefined"
      class="w-full min-h-12 px-4 py-3 bg-white border rounded-[14px] text-base sm:text-sm text-dark appearance-none bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2216%22%20height%3D%2216%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22%2387575d%22%20stroke-width%3D%222%22%3E%3Cpath%20d%3D%22m6%209%206%206%206-6%22%2F%3E%3C%2Fsvg%3E')] bg-[length:16px] bg-[right_16px_center] bg-no-repeat shadow-sm focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 disabled:opacity-60 disabled:cursor-not-allowed disabled:bg-primary/10"
      :class="error ? 'border-red-600' : 'border-[#b9a8a8]'"
      @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)">
      <option value="" disabled>{{ placeholder || 'Select...' }}</option>
      <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
    </select>
    <p v-if="error" :id="`${inputId}-error`" role="alert" class="text-sm text-red-700">{{ error }}</p>
  </div>
</template>

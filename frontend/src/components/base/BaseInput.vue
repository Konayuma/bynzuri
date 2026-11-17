<script setup lang="ts">
import { computed, ref, useId } from 'vue'

defineOptions({ inheritAttrs: false })
const props = defineProps<{
  modelValue: string
  label?: string
  type?: string
  placeholder?: string
  error?: string
  hint?: string
  required?: boolean
  disabled?: boolean
  id?: string
}>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const generatedId = useId()
const inputId = computed(() => props.id || generatedId)
const showPassword = ref(false)
const descriptionId = computed(() => props.error ? `${inputId.value}-error` : props.hint ? `${inputId.value}-hint` : undefined)
function handleInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLInputElement).value)
}
</script>

<template>
  <div class="space-y-1.5">
    <label v-if="label" :for="inputId" class="block text-sm font-semibold text-dark">
      {{ label }} <span v-if="required" class="text-gold" aria-hidden="true">*</span>
    </label>
    <div class="relative">
      <input
        v-bind="$attrs" :id="inputId" :type="type === 'password' && showPassword ? 'text' : (type || 'text')"
        :value="modelValue" :placeholder="placeholder" :required="required" :disabled="disabled"
        :aria-invalid="error ? 'true' : undefined" :aria-describedby="descriptionId"
        class="w-full min-h-12 px-4 py-3 bg-white border rounded-[14px] text-base sm:text-sm text-dark placeholder:text-muted/70 shadow-sm focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 transition-[border-color,box-shadow] disabled:opacity-60 disabled:cursor-not-allowed disabled:bg-primary/10"
        :class="[error ? 'border-red-600' : 'border-[#b9a8a8]', type === 'password' ? 'pr-20' : '']"
        @input="handleInput"
      />
      <button v-if="type === 'password'" type="button" :disabled="disabled" :aria-controls="inputId"
        :aria-label="`${showPassword ? 'Hide' : 'Show'} ${label || 'password'}`"
        class="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg px-3 py-2 text-xs font-semibold text-gold hover:bg-primary/30 focus-visible:outline-2 focus-visible:outline-gold active:scale-95"
        @click="showPassword = !showPassword">{{ showPassword ? 'Hide' : 'Show' }}</button>
    </div>
    <p v-if="error" :id="`${inputId}-error`" class="text-sm text-red-700" role="alert">{{ error }}</p>
    <p v-else-if="hint" :id="`${inputId}-hint`" class="text-xs leading-relaxed text-muted">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  tabs: { value: string; label: string }[]
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <div class="border-b border-gray-100 mb-6">
    <nav class="flex gap-6 -mb-px">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        class="pb-3 text-sm font-medium transition-colors border-b-2"
        :class="modelValue === tab.value ? 'border-dark text-dark' : 'border-transparent text-gray-400 hover:text-gray-600'"
        @click="$emit('update:modelValue', tab.value)"
      >
        {{ tab.label }}
      </button>
    </nav>
  </div>
</template>

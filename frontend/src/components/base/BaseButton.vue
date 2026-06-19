<script setup lang="ts">
defineProps<{
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
  fullWidth?: boolean
  type?: 'button' | 'submit'
}>()

defineEmits<{
  click: [e: MouseEvent]
}>()
</script>

<template>
  <button
    :type="type || 'button'"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-gold/50 active:scale-[0.97]',
      {
        'bg-primary text-dark hover:bg-primary/80': variant === 'primary' || !variant,
        'bg-dark text-background hover:bg-dark/90': variant === 'secondary',
        'border-2 border-primary text-dark hover:bg-primary/20': variant === 'outline',
        'text-dark hover:bg-primary/30': variant === 'ghost',
        'px-6 py-2.5 text-sm rounded-[16px]': size === 'sm' || !size,
        'px-8 py-3 text-base rounded-[16px]': size === 'md',
        'px-10 py-4 text-lg rounded-[16px]': size === 'lg',
        'w-full': fullWidth,
        'opacity-50 cursor-not-allowed': disabled,
        'cursor-wait opacity-80': loading
      }
    ]"
    @click="$emit('click', $event)"
  >
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
    </svg>
    <slot />
  </button>
</template>

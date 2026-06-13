<script setup lang="ts">
import { watch, ref } from 'vue'
import { gsap } from 'gsap'

const props = defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{
  close: []
}>()

const overlayEl = ref<HTMLElement | null>(null)
const panelEl = ref<HTMLElement | null>(null)

watch(() => props.open, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => {
      if (overlayEl.value) {
        gsap.fromTo(overlayEl.value, { opacity: 0 }, { opacity: 1, duration: 0.25, ease: 'power2.out' })
      }
      if (panelEl.value) {
        gsap.fromTo(
          panelEl.value,
          { opacity: 0, scale: 0.92, y: 20 },
          { opacity: 1, scale: 1, y: 0, duration: 0.35, ease: 'back.out(1.4)' }
        )
      }
    })
  } else {
    document.body.style.overflow = ''
    if (overlayEl.value) {
      gsap.to(overlayEl.value, { opacity: 0, duration: 0.2 })
    }
    if (panelEl.value) {
      gsap.to(panelEl.value, { opacity: 0, scale: 0.95, y: 10, duration: 0.2, ease: 'power2.in' })
    }
  }
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div
        ref="overlayEl"
        class="absolute inset-0 bg-black/30"
        @click="emit('close')"
      />
      <div
        ref="panelEl"
        class="relative bg-background rounded-[24px] shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6"
      >
        <div v-if="title" class="flex items-center justify-between mb-4">
          <h2 class="font-heading text-xl font-semibold text-dark">{{ title }}</h2>
          <button
            class="p-1 hover:bg-primary/30 rounded-lg transition-colors"
            @click="emit('close')"
            aria-label="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <slot />
      </div>
    </div>
  </Teleport>
</template>

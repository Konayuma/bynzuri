<script setup lang="ts">
import { watch, ref } from 'vue'
import { gsap } from 'gsap'

const props = defineProps<{
  open: boolean
  title?: string
  position?: 'left' | 'right'
}>()

const emit = defineEmits<{
  close: []
}>()

const drawerEl = ref<HTMLElement | null>(null)
const overlayEl = ref<HTMLElement | null>(null)

watch(() => props.open, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
    requestAnimationFrame(() => {
      if (overlayEl.value) {
        gsap.fromTo(overlayEl.value, { opacity: 0 }, { opacity: 1, duration: 0.3, ease: 'power2.out' })
      }
      if (drawerEl.value) {
        const x = props.position === 'left' ? -100 : 100
        gsap.fromTo(drawerEl.value, { x: `${x}%` }, { x: '0%', duration: 0.35, ease: 'power3.out' })
      }
    })
  } else {
    document.body.style.overflow = ''
    if (overlayEl.value) {
      gsap.to(overlayEl.value, { opacity: 0, duration: 0.2 })
    }
    if (drawerEl.value) {
      const x = props.position === 'left' ? -100 : 100
      gsap.to(drawerEl.value, { x: `${x}%`, duration: 0.25, ease: 'power2.in' })
    }
  }
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50"
    >
      <div
        ref="overlayEl"
        class="absolute inset-0 bg-black/30"
        @click="emit('close')"
      />
      <div
        ref="drawerEl"
        :class="[
          'fixed top-0 bottom-0 w-full max-w-md bg-background shadow-xl flex flex-col',
          position === 'left' ? 'left-0' : 'right-0'
        ]"
      >
        <div class="flex items-center justify-between px-4 h-[72px] border-b border-primary/20 shrink-0">
          <h2 v-if="title" class="font-heading text-lg font-semibold text-dark">{{ title }}</h2>
          <div v-else />
          <button
            class="p-2 hover:bg-primary/30 rounded-lg transition-colors"
            @click="emit('close')"
            aria-label="Close drawer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="flex-1 overflow-y-auto">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>

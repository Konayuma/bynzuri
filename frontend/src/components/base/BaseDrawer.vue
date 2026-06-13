<script setup lang="ts">
import { watch } from 'vue'

const props = defineProps<{
  open: boolean
  title?: string
  position?: 'left' | 'right'
}>()

const emit = defineEmits<{
  close: []
}>()

watch(() => props.open, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-200"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50"
      >
        <div
          class="absolute inset-0 bg-black/30"
          @click="emit('close')"
        />
        <div
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
    </Transition>
  </Teleport>
</template>

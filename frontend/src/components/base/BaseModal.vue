<script setup lang="ts">
import { watch } from 'vue'

const props = defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{
  close: []
}>()

watch(() => props.open, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div
          class="absolute inset-0 bg-black/30"
          @click="emit('close')"
        />
        <div
          class="relative bg-background rounded-[24px] shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 modal-panel"
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
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active {
  transition: opacity 0.25s ease;
}
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-panel {
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease;
}
.modal-enter-from .modal-panel {
  transform: scale(0.92) translateY(20px);
  opacity: 0;
}
.modal-leave-to .modal-panel {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}
</style>

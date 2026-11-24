<script setup lang="ts">
import { ref } from 'vue'
import { useDialogFocus } from '@/composables/useDialogFocus'
import { X } from '@lucide/vue'

const props = defineProps<{
  open: boolean
  title?: string
}>()

const emit = defineEmits<{
  close: []
}>()

const panel = ref<HTMLElement | null>(null)
useDialogFocus(() => props.open, panel, () => emit('close'))
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        :aria-label="title || 'Dialog'"
      >
        <div
          class="absolute inset-0 bg-black/30"
          @click="emit('close')"
        />
        <div
          ref="panel" tabindex="-1"
          class="relative bg-background rounded-[24px] shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 modal-panel"
        >
          <div v-if="title" class="flex items-center justify-between mb-4">
            <h2 class="font-heading text-xl font-semibold text-dark">{{ title }}</h2>
            <button
              class="p-1.5 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
              @click="emit('close')"
              aria-label="Close"
            >
              <X class="w-5 h-5 text-dark" />
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

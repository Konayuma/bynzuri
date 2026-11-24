<script setup lang="ts">
import { ref } from 'vue'
import { useDialogFocus } from '@/composables/useDialogFocus'
import { X } from '@lucide/vue'

const props = defineProps<{
  open: boolean
  title?: string
  position?: 'left' | 'right'
}>()

const emit = defineEmits<{
  close: []
}>()

const panel = ref<HTMLElement | null>(null)
useDialogFocus(() => props.open, panel, () => emit('close'))
</script>

<template>
  <Teleport to="body">
    <Transition name="drawer-overlay">
      <div
        v-if="open"
        class="fixed inset-0 z-50"
        role="dialog"
        aria-modal="true"
        :aria-label="title || 'Drawer'"
      >
        <div
          class="absolute inset-0 bg-black/30"
          @click="emit('close')"
        />
        <div
          ref="panel" tabindex="-1"
          :class="[
            'fixed top-0 bottom-0 w-full max-w-md bg-background shadow-xl flex flex-col drawer-panel',
            position === 'left' ? 'left-0 drawer-panel-left' : 'right-0 drawer-panel-right'
          ]"
        >
          <div class="flex items-center justify-between px-4 h-[72px] border-b border-primary/20 shrink-0">
            <h2 v-if="title" class="font-heading text-lg font-semibold text-dark">{{ title }}</h2>
            <div v-else />
            <button
              class="p-2 hover:bg-primary/30 rounded-lg transition-colors active:scale-95"
              @click="emit('close')"
              aria-label="Close"
            >
              <X class="w-5 h-5 text-dark" />
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

<style scoped>
.drawer-overlay-enter-active {
  transition: opacity 0.3s ease;
}
.drawer-overlay-leave-active {
  transition: opacity 0.2s ease;
}
.drawer-overlay-enter-from,
.drawer-overlay-leave-to {
  opacity: 0;
}

.drawer-panel {
  transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.drawer-panel-right {
  transform: translateX(0);
}
.drawer-panel-left {
  transform: translateX(0);
}
.drawer-overlay-enter-from .drawer-panel-right {
  transform: translateX(100%);
}
.drawer-overlay-enter-from .drawer-panel-left {
  transform: translateX(-100%);
}
.drawer-overlay-leave-to .drawer-panel-right {
  transform: translateX(100%);
}
.drawer-overlay-leave-to .drawer-panel-left {
  transform: translateX(-100%);
}
</style>

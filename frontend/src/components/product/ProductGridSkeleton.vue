<script setup lang="ts">
withDefaults(defineProps<{ count?: number; message?: string; catalog?: boolean }>(), {
  count: 4,
  message: 'Loading products…',
})
</script>

<template>
  <div role="status" aria-live="polite" class="space-y-4">
    <p class="text-sm text-muted">{{ message }}</p>
    <div class="grid grid-cols-2 gap-4 md:grid-cols-3 sm:gap-6" :class="{ 'lg:grid-cols-4': !catalog }" aria-hidden="true">
      <div v-for="item in count" :key="item" class="space-y-3">
        <div class="aspect-[3/4] rounded-[20px] bg-primary/30 motion-safe:animate-pulse" />
        <div class="h-3 w-1/3 rounded bg-primary/30 motion-safe:animate-pulse" />
        <div class="h-4 w-3/4 rounded bg-primary/30 motion-safe:animate-pulse" />
        <div class="h-4 w-1/4 rounded bg-primary/30 motion-safe:animate-pulse" />
        <div class="flex items-center gap-2 pt-1">
          <div class="h-10 flex-1 rounded-full bg-primary/30 motion-safe:animate-pulse" />
          <div class="h-10 w-10 rounded-full bg-primary/30 motion-safe:animate-pulse shrink-0" />
        </div>
      </div>
    </div>
  </div>
</template>

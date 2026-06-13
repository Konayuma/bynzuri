<script setup lang="ts">
defineProps<{
  class?: string
}>()
</script>

<template>
  <div
    class="animate-pulse rounded-[14px] bg-primary/40"
    :class="$props.class || 'w-full h-4'"
  />
</template>

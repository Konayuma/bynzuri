<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ text: string }>()
type Part = { kind: 'text' | 'bold' | 'italic' | 'code' | 'link'; text: string; href?: string }
const parts = computed<Part[]>(() => {
  const result: Part[] = []
  const pattern = /\*\*(.+?)\*\*|__(.+?)__|\[([^\]]+)\]\(([^\s)]+)\)|`([^`]+)`|\*([^*\n]+)\*|_([^_\n]+)_/g
  let offset = 0
  for (const match of props.text.matchAll(pattern)) {
    const index = match.index
    if (index > offset) result.push({ kind: 'text', text: props.text.slice(offset, index) })
    if (match[1] || match[2]) result.push({ kind: 'bold', text: match[1] || match[2]! })
    else if (match[3]) {
      const href = match[4]!
      if (/^https?:\/\//i.test(href)) result.push({ kind: 'link', text: match[3], href })
      else result.push({ kind: 'text', text: match[0] })
    } else if (match[5]) result.push({ kind: 'code', text: match[5] })
    else result.push({ kind: 'italic', text: (match[6] || match[7])! })
    offset = index + match[0].length
  }
  if (offset < props.text.length) result.push({ kind: 'text', text: props.text.slice(offset) })
  return result
})
</script>

<template>
  <template v-for="(part, index) in parts" :key="index">
    <strong v-if="part.kind === 'bold'" class="font-semibold text-dark">{{ part.text }}</strong>
    <em v-else-if="part.kind === 'italic'">{{ part.text }}</em>
    <code v-else-if="part.kind === 'code'" class="rounded bg-primary/20 px-1">{{ part.text }}</code>
    <a v-else-if="part.kind === 'link'" :href="part.href" class="underline underline-offset-2 focus-visible:outline-2 focus-visible:outline-gold">{{ part.text }}</a>
    <template v-else>{{ part.text }}</template>
  </template>
</template>

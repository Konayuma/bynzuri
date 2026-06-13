<script setup lang="ts">
import { ref } from 'vue'
import type { ProductImage } from '@/types'
import { ChevronLeft, ChevronRight } from '@lucide/vue'

const props = defineProps<{
  images: ProductImage[]
}>()

const currentIndex = ref(0)

function previous() {
  currentIndex.value = currentIndex.value > 0 ? currentIndex.value - 1 : props.images.length - 1
}

function next() {
  currentIndex.value = currentIndex.value < props.images.length - 1 ? currentIndex.value + 1 : 0
}
</script>

<template>
  <div class="space-y-3">
    <div class="relative aspect-[3/4] rounded-[20px] overflow-hidden bg-primary/20">
      <img
        v-for="(img, index) in images"
        :key="img.id"
        :src="img.image"
        :alt="img.alt_text"
        class="absolute inset-0 w-full h-full object-cover transition-opacity duration-300"
        :class="index === currentIndex ? 'opacity-100' : 'opacity-0'"
      />

      <button
        v-if="images.length > 1"
        class="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-background/90 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-colors shadow-sm"
        @click="previous"
        aria-label="Previous image"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <button
        v-if="images.length > 1"
        class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-background/90 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-colors shadow-sm"
        @click="next"
        aria-label="Next image"
      >
        <ChevronRight class="w-4 h-4" />
      </button>

      <div v-if="images.length > 1" class="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5">
        <button
          v-for="(_, index) in images"
          :key="index"
          class="w-2 h-2 rounded-full transition-all"
          :class="index === currentIndex ? 'bg-dark w-4' : 'bg-dark/30'"
          @click="currentIndex = index"
          :aria-label="`Go to image ${index + 1}`"
        />
      </div>
    </div>

    <div v-if="images.length > 1" class="flex gap-2 overflow-x-auto pb-1">
      <button
        v-for="(img, index) in images"
        :key="img.id"
        class="w-16 h-20 rounded-[10px] overflow-hidden shrink-0 transition-all border-2"
        :class="index === currentIndex ? 'border-gold opacity-100' : 'border-transparent opacity-60 hover:opacity-100'"
        @click="currentIndex = index"
      >
        <img :src="img.image" :alt="img.alt_text" class="w-full h-full object-cover" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { ProductImage } from '@/types'
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from '@lucide/vue'

const props = defineProps<{
  images: ProductImage[]
}>()

const currentIndex = ref(0)
const isZooming = ref(false)
const zoomX = ref(50)
const zoomY = ref(50)
const imgRef = ref<HTMLElement | null>(null)
let touchStartX = 0
let touchStartY = 0

function previous() {
  isZooming.value = false
  currentIndex.value = currentIndex.value > 0 ? currentIndex.value - 1 : props.images.length - 1
}

function next() {
  isZooming.value = false
  currentIndex.value = currentIndex.value < props.images.length - 1 ? currentIndex.value + 1 : 0
}

function updateZoomFromPoint(clientX: number, clientY: number) {
  const rect = imgRef.value?.getBoundingClientRect()
  if (!rect) return
  zoomX.value = Math.max(0, Math.min(100, ((clientX - rect.left) / rect.width) * 100))
  zoomY.value = Math.max(0, Math.min(100, ((clientY - rect.top) / rect.height) * 100))
}

function handleMouseMove(e: MouseEvent) {
  if (!isZooming.value) return
  updateZoomFromPoint(e.clientX, e.clientY)
}

function handleTouchStart(e: TouchEvent) {
  const touch = e.touches[0]
  if (!touch) return
  touchStartX = touch.clientX
  touchStartY = touch.clientY
  if (isZooming.value) {
    updateZoomFromPoint(touch.clientX, touch.clientY)
  }
}

function handleTouchMove(e: TouchEvent) {
  if (!isZooming.value) return
  const touch = e.touches[0]
  if (!touch) return
  e.preventDefault()
  updateZoomFromPoint(touch.clientX, touch.clientY)
}

function handleTouchEnd(e: TouchEvent) {
  if (isZooming.value || props.images.length <= 1) return
  const touch = e.changedTouches[0]
  if (!touch) return
  const dx = touch.clientX - touchStartX
  const dy = touch.clientY - touchStartY
  if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) {
    if (dx < 0) next()
    else previous()
  }
}

</script>

<template>
  <div class="space-y-3">
    <div
      ref="imgRef"
      class="relative aspect-square rounded-[20px] overflow-hidden bg-primary/20"
      :class="isZooming ? 'cursor-crosshair touch-none' : 'touch-pan-y'"
      @mousemove="handleMouseMove"
      @touchstart.passive="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend.passive="handleTouchEnd"
    >
      <img
        v-for="(img, index) in images"
        :key="img.id"
        v-show="!isZooming"
        :src="img.image"
        :alt="img.alt_text"
        class="absolute inset-0 w-full h-full object-contain transition-opacity duration-300"
        :class="index === currentIndex ? 'opacity-100' : 'opacity-0'"
        :loading="index === currentIndex ? 'eager' : 'lazy'"
        :fetchpriority="index === currentIndex ? 'high' : 'low'"
      />

      <div
        v-if="isZooming && images[currentIndex]"
        class="absolute inset-0 pointer-events-none"
        role="img"
        :aria-label="images[currentIndex]?.alt_text"
        :style="{
          backgroundImage: `url(${images[currentIndex]?.image})`,
          backgroundPosition: `${zoomX}% ${zoomY}%`,
          backgroundSize: '200%',
          backgroundRepeat: 'no-repeat'
        }"
      />

      <button
        v-if="images[currentIndex]"
        type="button"
        class="absolute right-3 top-3 grid h-11 w-11 place-items-center rounded-full bg-white/95 text-dark shadow-sm transition-colors hover:bg-white focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-gold"
        :aria-label="isZooming ? 'Zoom out of product image' : 'Zoom in on product image'"
        :aria-pressed="isZooming"
        @click="isZooming = !isZooming; zoomX = 50; zoomY = 50"
      >
        <ZoomOut v-if="isZooming" class="h-5 w-5" />
        <ZoomIn v-else class="h-5 w-5" />
      </button>

      <button
        v-if="images.length > 1"
        class="absolute left-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-background/90 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-colors shadow-sm active:scale-90"
        @click="previous"
        aria-label="Previous image"
      >
        <ChevronLeft class="w-4 h-4" />
      </button>
      <button
        v-if="images.length > 1"
        class="absolute right-3 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-background/90 backdrop-blur-sm flex items-center justify-center hover:bg-background transition-colors shadow-sm active:scale-90"
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
          @click="currentIndex = index; isZooming = false"
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
        @click="currentIndex = index; isZooming = false"
      >
        <img :src="img.image" :alt="img.alt_text" class="w-full h-full object-cover" loading="lazy" />
      </button>
    </div>
  </div>
</template>

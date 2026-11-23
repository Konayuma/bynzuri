<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, useId, watch } from 'vue'
import { Check, ChevronDown } from '@lucide/vue'

export interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<{
  modelValue: string
  label?: string
  options: SelectOption[]
  placeholder?: string
  error?: string
  required?: boolean
  disabled?: boolean
  id?: string
  size?: 'sm' | 'md' | 'lg'
  align?: 'left' | 'right'
  ariaLabel?: string
}>(), {
  size: 'lg',
  align: 'left',
})

const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const generatedId = useId()
const inputId = computed(() => props.id || generatedId)
const labelId = computed(() => `${inputId.value}-label`)
const listboxId = computed(() => `${inputId.value}-listbox`)
const optionId = (index: number) => `${inputId.value}-option-${index}`

const isOpen = ref(false)
const activeIndex = ref(-1)
const openUpward = ref(false)
const triggerRef = ref<HTMLButtonElement | null>(null)
const menuRef = ref<HTMLDivElement | null>(null)
const menuStyle = ref<Record<string, string>>({})

let typeaheadBuffer = ''
let typeaheadTimer: ReturnType<typeof setTimeout> | null = null

const selectedOption = computed(() =>
  props.options.find(opt => opt.value === props.modelValue)
)

const displayText = computed(() =>
  selectedOption.value ? selectedOption.value.label : (props.placeholder || 'Select...')
)

const hasValue = computed(() => Boolean(selectedOption.value))

const triggerSizeClasses = computed(() => {
  if (props.size === 'sm') return 'min-h-9 px-3 py-1.5 text-xs rounded-lg gap-1.5'
  if (props.size === 'md') return 'min-h-11 px-3.5 py-2 text-sm rounded-xl gap-2'
  return 'min-h-12 px-4 py-3 text-base sm:text-sm rounded-[14px] gap-2'
})

const optionSizeClasses = computed(() => {
  if (props.size === 'sm') return 'px-3 py-2 text-xs'
  return 'px-3.5 py-2.5 text-sm'
})

function findNextEnabledIndex(start: number, step: 1 | -1): number {
  const len = props.options.length
  if (len === 0) return -1
  for (let i = 0; i < len; i++) {
    const idx = (start + step * i + len) % len
    if (!props.options[idx]?.disabled) return idx
  }
  return -1
}

function updatePosition() {
  const trigger = triggerRef.value
  if (!trigger) return
  const rect = trigger.getBoundingClientRect()
  const viewportHeight = window.innerHeight
  const viewportWidth = window.innerWidth
  const estimatedHeight = Math.min(props.options.length * 42 + 16, 264)
  const spaceBelow = viewportHeight - rect.bottom - 8
  const spaceAbove = rect.top - 8

  const shouldOpenUpward = spaceBelow < estimatedHeight && spaceAbove > spaceBelow
  openUpward.value = shouldOpenUpward

  const minWidth = Math.max(rect.width, props.size === 'sm' ? 168 : rect.width)
  const maxWidth = Math.min(Math.max(minWidth, 220), viewportWidth - 16)

  let left = props.align === 'right' ? rect.right - minWidth : rect.left
  if (left + minWidth > viewportWidth - 8) left = viewportWidth - minWidth - 8
  if (left < 8) left = 8

  const style: Record<string, string> = {
    position: 'fixed',
    left: `${left}px`,
    minWidth: `${minWidth}px`,
    maxWidth: `${maxWidth}px`,
  }

  if (shouldOpenUpward) {
    style.bottom = `${viewportHeight - rect.top + 6}px`
    style.maxHeight = `${Math.max(120, Math.min(256, spaceAbove - 6))}px`
  } else {
    style.top = `${rect.bottom + 6}px`
    style.maxHeight = `${Math.max(120, Math.min(256, spaceBelow - 6))}px`
  }

  menuStyle.value = style
}

function scrollActiveIntoView() {
  if (activeIndex.value < 0 || !menuRef.value) return
  const el = menuRef.value.querySelector<HTMLElement>(`#${CSS.escape(optionId(activeIndex.value))}`)
  el?.scrollIntoView?.({ block: 'nearest' })
}

function openMenu(initialFocus: 'selected' | 'first' | 'last' = 'selected') {
  if (props.disabled) return
  isOpen.value = true

  if (initialFocus === 'first') {
    activeIndex.value = findNextEnabledIndex(0, 1)
  } else if (initialFocus === 'last') {
    activeIndex.value = findNextEnabledIndex(props.options.length - 1, -1)
  } else {
    const selectedIdx = props.options.findIndex(opt => opt.value === props.modelValue && !opt.disabled)
    activeIndex.value = selectedIdx >= 0 ? selectedIdx : findNextEnabledIndex(0, 1)
  }

  nextTick(() => {
    updatePosition()
    scrollActiveIntoView()
  })
}

function closeMenu(returnFocus = false) {
  if (!isOpen.value) return
  isOpen.value = false
  activeIndex.value = -1
  if (returnFocus) {
    nextTick(() => triggerRef.value?.focus())
  }
}

function toggleMenu() {
  if (isOpen.value) closeMenu()
  else openMenu('selected')
}

function selectOption(option: SelectOption) {
  if (option.disabled) return
  emit('update:modelValue', option.value)
  closeMenu(true)
}

function handleTypeahead(char: string) {
  if (typeaheadTimer) clearTimeout(typeaheadTimer)
  typeaheadBuffer += char.toLowerCase()
  typeaheadTimer = setTimeout(() => {
    typeaheadBuffer = ''
  }, 500)

  const start = activeIndex.value >= 0 ? activeIndex.value : 0
  const len = props.options.length
  for (let i = 0; i < len; i++) {
    const idx = (start + i) % len
    const opt = props.options[idx]
    if (opt && !opt.disabled && opt.label.toLowerCase().startsWith(typeaheadBuffer)) {
      activeIndex.value = idx
      if (!isOpen.value) openMenu('selected')
      nextTick(scrollActiveIntoView)
      break
    }
  }
}

function handleKeydown(event: KeyboardEvent) {
  if (props.disabled) return

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      if (!isOpen.value) {
        openMenu('first')
      } else {
        activeIndex.value = findNextEnabledIndex(activeIndex.value + 1, 1)
        nextTick(scrollActiveIntoView)
      }
      break
    case 'ArrowUp':
      event.preventDefault()
      if (!isOpen.value) {
        openMenu('last')
      } else {
        activeIndex.value = findNextEnabledIndex(activeIndex.value - 1, -1)
        nextTick(scrollActiveIntoView)
      }
      break
    case 'Home':
      if (isOpen.value) {
        event.preventDefault()
        activeIndex.value = findNextEnabledIndex(0, 1)
        nextTick(scrollActiveIntoView)
      }
      break
    case 'End':
      if (isOpen.value) {
        event.preventDefault()
        activeIndex.value = findNextEnabledIndex(props.options.length - 1, -1)
        nextTick(scrollActiveIntoView)
      }
      break
    case 'Enter':
    case ' ':
      event.preventDefault()
      if (!isOpen.value) {
        openMenu('selected')
      } else if (activeIndex.value >= 0 && props.options[activeIndex.value]) {
        selectOption(props.options[activeIndex.value]!)
      }
      break
    case 'Escape':
      if (isOpen.value) {
        event.preventDefault()
        closeMenu(true)
      }
      break
    case 'Tab':
      if (isOpen.value) closeMenu(false)
      break
    default:
      if (event.key.length === 1 && !event.ctrlKey && !event.metaKey && !event.altKey) {
        handleTypeahead(event.key)
      }
  }
}

function handleDocumentPointerDown(event: MouseEvent) {
  const target = event.target as Node | null
  if (!target) return
  if (triggerRef.value?.contains(target) || menuRef.value?.contains(target)) return
  closeMenu(false)
}

function addGlobalListeners() {
  document.addEventListener('mousedown', handleDocumentPointerDown)
  window.addEventListener('resize', updatePosition)
  window.addEventListener('scroll', updatePosition, true)
}

function removeGlobalListeners() {
  document.removeEventListener('mousedown', handleDocumentPointerDown)
  window.removeEventListener('resize', updatePosition)
  window.removeEventListener('scroll', updatePosition, true)
}

watch(isOpen, (open) => {
  if (open) addGlobalListeners()
  else removeGlobalListeners()
})

watch(() => props.disabled, (disabled) => {
  if (disabled) closeMenu(false)
})

onBeforeUnmount(() => {
  removeGlobalListeners()
  if (typeaheadTimer) clearTimeout(typeaheadTimer)
})
</script>

<template>
  <div class="space-y-1.5" v-bind="$attrs">
    <label v-if="label" :id="labelId" :for="inputId" class="block text-sm font-semibold text-dark">
      {{ label }} <span v-if="required" class="text-gold" aria-hidden="true">*</span>
    </label>

    <button
      :id="inputId"
      ref="triggerRef"
      type="button"
      role="combobox"
      aria-haspopup="listbox"
      :aria-expanded="isOpen ? 'true' : 'false'"
      :aria-controls="listboxId"
      :aria-activedescendant="isOpen && activeIndex >= 0 ? optionId(activeIndex) : undefined"
      :aria-labelledby="label ? labelId : undefined"
      :aria-label="!label ? ariaLabel : undefined"
      :aria-invalid="error ? 'true' : undefined"
      :aria-describedby="error ? `${inputId}-error` : undefined"
      :aria-required="required ? 'true' : undefined"
      :disabled="disabled"
      class="w-full flex items-center justify-between bg-white border text-left shadow-sm transition-[border-color,box-shadow,background-color] focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 disabled:opacity-60 disabled:cursor-not-allowed disabled:bg-primary/10 cursor-pointer"
      :class="[
        triggerSizeClasses,
        error
          ? 'border-red-600'
          : isOpen
            ? 'border-gold ring-2 ring-gold/25'
            : 'border-[#b9a8a8] hover:border-gold/70',
      ]"
      @click="toggleMenu"
      @keydown="handleKeydown"
    >
      <span class="truncate" :class="hasValue ? 'text-dark' : 'text-muted/80'">
        {{ displayText }}
      </span>
      <ChevronDown
        class="h-4 w-4 shrink-0 text-gold transition-transform duration-200"
        :class="isOpen ? 'rotate-180' : ''"
        aria-hidden="true"
      />
    </button>

    <Teleport to="body">
      <Transition name="select-dropdown">
        <div
          v-if="isOpen"
          :id="listboxId"
          ref="menuRef"
          role="listbox"
          :aria-labelledby="label ? labelId : undefined"
          :aria-label="!label ? (ariaLabel || placeholder || 'Options') : undefined"
          :style="menuStyle"
          class="z-[70] overflow-y-auto rounded-[16px] border border-primary/80 bg-white p-1.5 shadow-[0_12px_32px_rgba(33,26,26,0.12)] focus:outline-none"
          :class="openUpward ? 'origin-bottom' : 'origin-top'"
        >
          <div v-if="options.length === 0" class="px-3.5 py-2.5 text-sm text-muted">
            No options available
          </div>
          <button
            v-for="(opt, index) in options"
            :key="opt.value"
            :id="optionId(index)"
            type="button"
            role="option"
            :aria-selected="opt.value === modelValue ? 'true' : 'false'"
            :aria-disabled="opt.disabled ? 'true' : undefined"
            :disabled="opt.disabled"
            class="flex w-full items-center justify-between gap-2 rounded-[10px] text-left transition-colors"
            :class="[
              optionSizeClasses,
              opt.disabled
                ? 'cursor-not-allowed opacity-45 text-muted'
                : opt.value === modelValue
                  ? 'bg-nzuri-blush/80 font-semibold text-dark cursor-pointer'
                  : activeIndex === index
                    ? 'bg-nzuri-blush/50 text-dark cursor-pointer'
                    : 'text-dark hover:bg-nzuri-blush/40 cursor-pointer',
            ]"
            @mouseenter="!opt.disabled && (activeIndex = index)"
            @mousedown.prevent
            @click="selectOption(opt)"
          >
            <span class="truncate">{{ opt.label }}</span>
            <Check
              v-if="opt.value === modelValue"
              class="h-4 w-4 shrink-0 text-gold"
              aria-hidden="true"
            />
          </button>
        </div>
      </Transition>
    </Teleport>

    <p v-if="error" :id="`${inputId}-error`" role="alert" class="text-sm text-red-700">{{ error }}</p>
  </div>
</template>

<style scoped>
.select-dropdown-enter-active {
  transition: opacity 0.14s ease, transform 0.14s cubic-bezier(0.16, 1, 0.3, 1);
}
.select-dropdown-leave-active {
  transition: opacity 0.1s ease, transform 0.1s ease;
}
.select-dropdown-enter-from,
.select-dropdown-leave-to {
  opacity: 0;
  transform: scale(0.97) translateY(-4px);
}
</style>

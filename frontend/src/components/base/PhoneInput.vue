<script setup lang="ts">
import { computed } from 'vue'
import { getCountries, getCountryCallingCode, parsePhoneNumberFromString, type CountryCode } from 'libphonenumber-js'

const props = defineProps<{ modelValue: string; country: CountryCode; error?: string; disabled?: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [string]; 'update:country': [CountryCode] }>()

const countryNames = new Intl.DisplayNames(['en'], { type: 'region' })
const countries = getCountries().map(code => ({
  code,
  name: countryNames.of(code) || code,
  dial: getCountryCallingCode(code),
  flag: String.fromCodePoint(...[...code].map(char => 127397 + char.charCodeAt(0))),
})).sort((a, b) => a.name.localeCompare(b.name))
const selected = computed(() => countries.find(country => country.code === props.country))

function collapsePhoneInput(raw: string): { value: string; country?: CountryCode } {
  const trimmed = raw.trim()
  if (!trimmed) return { value: raw }

  const compact = trimmed.replace(/[\s().-]/g, '')

  // International format with leading '+' or '00'
  if (compact.startsWith('+') || compact.startsWith('00')) {
    const intl = compact.startsWith('00') ? `+${compact.slice(2)}` : compact
    const parsed = parsePhoneNumberFromString(intl)
    if (parsed?.isValid() && parsed.nationalNumber) {
      return {
        value: parsed.nationalNumber,
        country: parsed.country,
      }
    }
    return { value: raw }
  }

  // Bare calling code pasted or autofilled without '+' (e.g. 260978734029 while +260 is selected)
  const dial = selected.value?.dial
  if (dial && /^\d+$/.test(compact) && compact.startsWith(dial) && compact.length > dial.length + 5) {
    const parsed = parsePhoneNumberFromString(`+${compact}`, props.country)
    if (parsed?.isValid() && (!parsed.country || parsed.country === props.country) && parsed.nationalNumber) {
      return { value: parsed.nationalNumber }
    }
  }

  return { value: raw }
}

function handleInput(event: Event) {
  const input = event.target as HTMLInputElement
  const collapsed = collapsePhoneInput(input.value)
  if (collapsed.country && collapsed.country !== props.country) {
    emit('update:country', collapsed.country)
  }
  if (collapsed.value !== input.value) {
    input.value = collapsed.value
  }
  emit('update:modelValue', collapsed.value)
}
</script>

<template>
  <div class="space-y-1.5">
    <label for="reg-phone" class="block text-sm font-semibold text-dark">Phone number <span class="text-gold" aria-hidden="true">*</span></label>
    <div class="flex gap-2">
      <div class="relative w-28 shrink-0">
        <span aria-hidden="true" class="pointer-events-none absolute inset-y-0 left-3 z-10 flex items-center gap-1.5 text-sm text-dark"><span class="text-lg">{{ selected?.flag }}</span> +{{ selected?.dial }}</span>
        <select
          :value="country" aria-label="Phone country code" :disabled="disabled"
          class="h-12 w-full appearance-none rounded-[14px] border border-[#b9a8a8] bg-white px-3 text-sm text-transparent shadow-sm focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 disabled:opacity-60"
          @change="emit('update:country', ($event.target as HTMLSelectElement).value as CountryCode)"
        >
          <option v-for="item in countries" :key="item.code" :value="item.code" class="text-dark">{{ item.flag }} {{ item.name }} (+{{ item.dial }})</option>
        </select>
        <span aria-hidden="true" class="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-muted">⌄</span>
      </div>
      <input id="reg-phone" :value="modelValue" type="tel" inputmode="tel" autocomplete="tel-national" required maxlength="30" :disabled="disabled"
        :aria-invalid="error ? 'true' : undefined" :aria-describedby="error ? 'reg-phone-error' : 'reg-phone-hint'"
        class="min-h-12 min-w-0 flex-1 rounded-[14px] border bg-white px-4 py-3 text-base text-dark shadow-sm focus:outline-none focus:border-gold focus:ring-2 focus:ring-gold/25 disabled:opacity-60"
        :class="error ? 'border-red-600' : 'border-[#b9a8a8]'" placeholder="Phone number"
        @input="handleInput" />
    </div>
    <p v-if="error" id="reg-phone-error" class="text-sm text-red-700" role="alert">{{ error }}</p>
    <p v-else id="reg-phone-hint" class="text-sm text-muted">Country code: +{{ selected?.dial }}. Enter your phone number.</p>
  </div>
</template>

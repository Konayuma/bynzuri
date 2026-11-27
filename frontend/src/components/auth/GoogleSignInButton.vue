<script setup lang="ts">
import { onMounted, ref } from 'vue'

interface GoogleCredentialResponse {
  credential?: string
}

interface GoogleAccountsId {
  initialize: (config: {
    client_id: string
    callback: (response: GoogleCredentialResponse) => void
  }) => void
  renderButton: (
    parent: HTMLElement,
    options: {
      theme?: 'outline' | 'filled_blue' | 'filled_black'
      size?: 'large' | 'medium' | 'small'
      shape?: 'rectangular' | 'pill' | 'circle' | 'square'
      text?: 'signin_with' | 'signup_with' | 'continue_with' | 'signin'
      width?: number
    }
  ) => void
}

declare global {
  interface Window {
    google?: {
      accounts?: {
        id?: GoogleAccountsId
      }
    }
  }
}

const props = withDefaults(defineProps<{
  mode?: 'signin' | 'signup'
  disabled?: boolean
  lastUsed?: boolean
}>(), {
  mode: 'signin',
  disabled: false,
  lastUsed: false,
})

const emit = defineEmits<{
  credential: [string]
  error: [string]
}>()

const clientId = (import.meta.env.VITE_GOOGLE_CLIENT_ID || '').trim()
const buttonContainer = ref<HTMLElement | null>(null)
const ready = ref(false)

let scriptPromise: Promise<void> | null = null

function loadGoogleScript(): Promise<void> {
  if (typeof window === 'undefined') return Promise.resolve()
  if (window.google?.accounts?.id) return Promise.resolve()
  if (scriptPromise) return scriptPromise

  scriptPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>('script[src="https://accounts.google.com/gsi/client"]')
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true })
      existing.addEventListener('error', () => reject(new Error('Failed to load Google Sign-In')), { once: true })
      return
    }
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('Failed to load Google Sign-In'))
    document.head.appendChild(script)
  })
  return scriptPromise
}

onMounted(async () => {
  if (!clientId || !buttonContainer.value) return
  try {
    await loadGoogleScript()
    const gsi = window.google?.accounts?.id
    if (!gsi || !buttonContainer.value) return
    gsi.initialize({
      client_id: clientId,
      callback: (response) => {
        if (props.disabled) return
        if (response.credential) {
          emit('credential', response.credential)
        } else {
          emit('error', 'Google sign-in was cancelled or could not be completed.')
        }
      },
    })
    const width = Math.min(Math.max(buttonContainer.value.offsetWidth || 320, 240), 400)
    gsi.renderButton(buttonContainer.value, {
      theme: 'outline',
      size: 'large',
      shape: 'pill',
      text: props.mode === 'signup' ? 'signup_with' : 'signin_with',
      width,
    })
    ready.value = true
  } catch {
    emit('error', 'Google sign-in is temporarily unavailable. Use email instead.')
  }
})
</script>

<template>
  <div v-if="clientId" class="space-y-4">
    <div class="relative">
      <span
        v-if="lastUsed"
        class="pointer-events-none absolute -top-2.5 right-2 z-10 rounded-full border border-gold/30 bg-nzuri-blush px-2.5 py-0.5 text-[11px] font-medium text-dark shadow-xs"
      >
        Last used
      </span>
      <div
        ref="buttonContainer"
        class="flex min-h-[44px] w-full items-center justify-center transition-opacity"
        :class="disabled ? 'pointer-events-none opacity-60' : ''"
      />
    </div>
    <div class="relative flex items-center" aria-hidden="true">
      <div class="flex-grow border-t border-primary/50" />
      <span class="mx-3 text-xs uppercase tracking-wider text-muted">or</span>
      <div class="flex-grow border-t border-primary/50" />
    </div>
  </div>
</template>

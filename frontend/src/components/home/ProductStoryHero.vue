<script setup lang="ts">
import { computed, ref } from 'vue'

interface HeroStep {
  number: string
  kicker: string
  headingLine: string
  headingAccent: string
  description: string
  ctaLabel: string
  to: string
  image: string
  imageAlt: string
  tabLabel: string
}

const steps: HeroStep[] = [
  {
    number: '01',
    kicker: 'THE GROWTH ELIXIR',
    headingLine: 'Step 1: Root &',
    headingAccent: 'Scalp Revival',
    description: 'A herbal hair oil created to nourish your scalp and support your hair care routine from the roots.',
    ctaLabel: 'Shop Elixir',
    to: '/product/growth-elixir',
    image: '/images/products/growthelixir.webp',
    imageAlt: 'By Nzuri Growth Elixir herbal hair oil',
    tabLabel: 'Growth Elixir',
  },
  {
    number: '02',
    kicker: 'NOURISHING OIL MIX',
    headingLine: 'Step 2: Length &',
    headingAccent: 'Softening Care',
    description: 'Give your lengths some love with a nourishing oil mix made for a softer-feeling finish.',
    ctaLabel: 'Shop Nourishing Oil',
    to: '/product/nourishing-oil-mix',
    image: '/images/products/nourishingoilmix.webp',
    imageAlt: 'By Nzuri Nourishing Oil Mix',
    tabLabel: 'Nourishing Oil',
  },
]

const activeStep = ref(0)
const current = computed(() => steps[activeStep.value]!)
</script>

<template>
  <section class="product-story" aria-label="Discover our hair care products">
    <div class="story-stage" :class="{ 'is-second': activeStep === 1 }">
      <div class="story-line" aria-hidden="true">BY NZURI <span> / </span> HAIR CARE</div>
      <div class="story-layout">
        <div class="story-copy">
          <Transition name="hero-copy" mode="out-in">
            <div :key="current.number">
              <p class="story-kicker"><span>{{ current.number }}</span> {{ current.kicker }}</p>
              <h1>{{ current.headingLine }}<br /><em>{{ current.headingAccent }}</em></h1>
              <p class="story-description">{{ current.description }}</p>
              <div class="story-actions">
                <RouterLink :to="current.to" class="story-button">
                  {{ current.ctaLabel }} <span aria-hidden="true">↗</span>
                </RouterLink>
                <RouterLink to="/catalog" class="story-secondary">
                  Shop all
                </RouterLink>
              </div>
            </div>
          </Transition>
        </div>

        <div class="story-product">
          <div class="story-orbit" aria-hidden="true"></div>
          <span class="story-watermark" aria-hidden="true">NZURI</span>
          <Transition name="hero-img" mode="out-in">
            <img
              :key="current.image"
              class="product-image"
              :src="current.image"
              :alt="current.imageAlt"
              fetchpriority="high"
              decoding="async"
            />
          </Transition>
          <span class="product-caption" aria-hidden="true">THOUGHTFULLY MADE<br />FOR YOUR HAIR</span>
        </div>
      </div>

      <div class="story-footer" role="group" aria-label="Featured routine steps">
        <div class="story-tabs">
          <button
            v-for="(step, idx) in steps"
            :key="step.number"
            type="button"
            class="story-tab"
            :class="{ 'is-active': activeStep === idx }"
            :aria-pressed="activeStep === idx"
            @click="activeStep = idx"
          >
            <span class="story-tab-num">{{ step.number }}</span>
            <span>{{ step.tabLabel }}</span>
          </button>
        </div>
        <span class="story-rule" aria-hidden="true"></span>
        <span class="story-counter" aria-hidden="true">{{ current.number }} / 02</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.product-story {
  position: relative;
  background: #f4e8e5;
}
.story-stage {
  position: relative;
  overflow: hidden;
  background: radial-gradient(ellipse at 70% 48%, #fffaf6 0%, #f3e4e1 48%, #e7d0d2 100%);
  transition: background 0.35s ease;
}
.story-stage.is-second {
  background: radial-gradient(ellipse at 70% 45%, #fffaf5 0%, #f5e8e2 48%, #ead4cf 100%);
}
.story-layout {
  position: relative;
  z-index: 1;
  max-width: 1280px;
  margin: auto;
  padding: 56px 48px 36px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 32px;
  min-height: min(74svh, 580px);
  color: #302324;
}
.story-copy {
  max-width: 520px;
}
.story-kicker {
  font: 600 10px 'Cinzel', serif;
  letter-spacing: 0.22em;
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 24px;
}
.story-kicker span {
  border: 1px solid currentColor;
  border-radius: 50%;
  height: 32px;
  width: 32px;
  display: grid;
  place-items: center;
  letter-spacing: 0;
}
.story-copy h1 {
  font: 400 clamp(2.2rem, 4vw, 4rem)/1.13 'Cinzel', serif;
  letter-spacing: -0.025em;
  margin: 0;
}
.story-copy em {
  display: block;
  font: 400 1.3em/1 'Great Vibes', cursive;
  letter-spacing: 0;
  margin-top: 8px;
}
.story-description {
  font-size: 14px;
  line-height: 1.75;
  max-width: 380px;
  opacity: 0.82;
  margin: 20px 0 28px;
}
.story-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 20px;
}
.story-button {
  display: inline-flex;
  align-items: center;
  gap: 28px;
  min-height: 48px;
  border-radius: 99px;
  background: #302324;
  color: #fff9f5;
  padding: 14px 22px;
  font: 600 10px 'Cinzel', serif;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s;
}
.story-button span {
  font: 18px sans-serif;
}
.story-button:focus-visible,
.story-secondary:focus-visible,
.story-tab:focus-visible {
  outline: 3px solid #87575d;
  outline-offset: 3px;
}
.story-secondary {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  font: 600 11px 'Cinzel', serif;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #302324;
  text-decoration: underline;
  text-underline-offset: 5px;
}
.story-product {
  height: min(56vh, 460px);
  position: relative;
  display: grid;
  place-items: center;
}
.story-orbit {
  position: absolute;
  width: min(88%, 410px);
  aspect-ratio: 1;
  border: 1px solid currentColor;
  opacity: 0.16;
  border-radius: 50%;
}
.story-watermark {
  position: absolute;
  font: 600 clamp(4.5rem, 10vw, 9rem) 'Cinzel', serif;
  letter-spacing: 0.1em;
  opacity: 0.09;
}
.product-image {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  filter: drop-shadow(0 26px 26px rgba(0, 0, 0, 0.2));
}
.product-caption {
  position: absolute;
  bottom: 2%;
  right: 0;
  font: 10px/1.7 'Cinzel', serif;
  letter-spacing: 0.12em;
  opacity: 0.65;
}
.story-line {
  position: absolute;
  top: 28px;
  right: 5%;
  z-index: 2;
  font: 10px 'Cinzel', serif;
  letter-spacing: 0.2em;
  color: #473438;
  opacity: 0.6;
}
.story-footer {
  max-width: 1280px;
  margin: auto;
  padding: 0 48px 28px;
  display: flex;
  align-items: center;
  gap: 18px;
  font: 10px 'Cinzel', serif;
  letter-spacing: 0.18em;
  color: #473438;
}
.story-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.story-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 6px 14px;
  border-radius: 999px;
  border: 1px solid rgba(48, 35, 36, 0.2);
  background: rgba(255, 255, 255, 0.45);
  color: #473438;
  font: 600 10px 'Cinzel', serif;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  transition: background 0.18s, border-color 0.18s, color 0.18s;
}
.story-tab:hover {
  background: rgba(255, 255, 255, 0.8);
}
.story-tab.is-active {
  background: #302324;
  border-color: #302324;
  color: #fff9f5;
}
.story-tab-num {
  opacity: 0.7;
}
.story-rule {
  height: 1px;
  background: currentColor;
  opacity: 0.25;
  flex: 1;
}
.story-counter {
  white-space: nowrap;
}
.hero-copy-enter-active,
.hero-copy-leave-active,
.hero-img-enter-active,
.hero-img-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.hero-copy-enter-from,
.hero-copy-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
.hero-img-enter-from,
.hero-img-leave-to {
  opacity: 0;
  transform: scale(0.97);
}

@media (hover: hover) and (pointer: fine) {
  .story-button:hover {
    transform: translateY(-2px);
    background: #584044;
  }
}

@media (max-width: 768px) {
  .story-layout {
    grid-template-columns: 1fr;
    padding: 28px 20px 20px;
    gap: 16px;
    min-height: 0;
  }
  .story-kicker {
    margin-bottom: 14px;
  }
  .story-copy h1 {
    font-size: clamp(1.75rem, 7.5vw, 2.35rem);
  }
  .story-description {
    margin: 14px 0 20px;
    font-size: 0.9375rem;
    line-height: 1.55;
  }
  .story-product {
    height: min(34svh, 280px);
  }
  .story-orbit {
    width: min(72%, 240px);
  }
  .story-line {
    display: none;
  }
  .product-caption {
    font-size: 9px;
  }
  .story-footer {
    padding: 0 20px 22px;
    gap: 12px;
  }
  .story-rule,
  .story-counter {
    display: none;
  }
}
</style>

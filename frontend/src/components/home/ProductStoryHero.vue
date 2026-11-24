<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

const story = ref<HTMLElement | null>(null)
const progress = ref(0)
const reducedMotion = ref(false)
let frame = 0
let media: MediaQueryList

const blend = computed(() => {
  const t = Math.max(0, Math.min(1, (progress.value - 0.22) / 0.5))
  return t * t * (3 - 2 * t)
})
const activeSecond = computed(() => blend.value >= 0.5)
const firstStyle = computed(() => ({ opacity: 1 - blend.value, transform: `translateX(${-55 * blend.value}%) scale(${1 - blend.value * 0.06})` }))
const secondStyle = computed(() => ({ opacity: blend.value, transform: `translateX(${55 * (1 - blend.value)}%) scale(${0.94 + blend.value * 0.06})` }))
function update() {
  frame = 0
  if (!story.value || reducedMotion.value) return
  const rect = story.value.getBoundingClientRect()
  progress.value = Math.max(0, Math.min(1, -rect.top / Math.max(1, rect.height - window.innerHeight)))
}
function schedule() { if (!frame) frame = requestAnimationFrame(update) }
function setMotion() { reducedMotion.value = media.matches; schedule() }
onMounted(() => {
  media = window.matchMedia('(prefers-reduced-motion: reduce), (max-width: 700px) and (max-height: 680px)')
  setMotion()
  media.addEventListener('change', setMotion)
  window.addEventListener('scroll', schedule, { passive: true })
  window.addEventListener('resize', schedule, { passive: true })
  update()
})
onUnmounted(() => {
  media?.removeEventListener('change', setMotion)
  window.removeEventListener('scroll', schedule)
  window.removeEventListener('resize', schedule)
  cancelAnimationFrame(frame)
})
</script>

<template>
  <section ref="story" class="product-story" aria-label="Discover our hair care products" :class="{ 'reduced-motion': reducedMotion }">
    <div class="story-stage">
      <div class="story-light" :style="{ opacity: reducedMotion ? 0 : blend }" aria-hidden="true"></div>
      <div class="story-line" aria-hidden="true">BY NZURI <span> / </span> HAIR CARE</div>
      <div class="story-layout" :class="{ 'is-light': activeSecond && !reducedMotion }">
        <div class="story-copy" :style="reducedMotion ? undefined : { opacity: 1 - blend, transform: `translateY(${-12 * blend}px)`, pointerEvents: activeSecond ? 'none' : 'auto' }" :aria-hidden="!reducedMotion && activeSecond" :inert="!reducedMotion && activeSecond">
          <p class="story-kicker"><span>01</span> THE GROWTH ELIXIR</p>
          <h1>Step 1: Root &amp;<br /><em>Scalp Revival</em></h1>
          <p class="story-description">A herbal hair oil created to nourish your scalp and support your hair care routine from the roots.</p>
          <RouterLink :to="{ path: '/catalog', query: { search: 'Growth Elixir' } }" class="story-button">Shop Elixir <span aria-hidden="true">↗</span></RouterLink>
        </div>
        <div v-if="!reducedMotion" class="story-copy story-copy--second" :style="{ opacity: blend, transform: `translateY(${12 * (1 - blend)}px)`, pointerEvents: activeSecond ? 'auto' : 'none' }" :aria-hidden="!activeSecond" :inert="!activeSecond">
          <p class="story-kicker"><span>02</span> NOURISHING OIL MIX</p>
          <h2>Step 2: Length &amp;<br /><em>Softening Care</em></h2>
          <p class="story-description">Give your lengths some love with a nourishing oil mix made for a softer-feeling finish.</p>
          <RouterLink :to="{ path: '/catalog', query: { search: 'Nourishing Oil Mix' } }" class="story-button">Shop Nourishing Oil <span aria-hidden="true">↗</span></RouterLink>
        </div>
        <div class="story-product" aria-hidden="true">
          <div class="story-orbit"></div>
          <span class="story-watermark">NZURI</span>
          <img class="product-image" src="/images/products/growthelixir.webp" alt="" :style="reducedMotion ? undefined : firstStyle" />
          <img v-if="!reducedMotion" class="product-image" src="/images/products/nourishingoilmix.webp" alt="" :style="secondStyle" />
          <span class="product-caption">THOUGHTFULLY MADE<br />FOR YOUR HAIR</span>
        </div>
      </div>
      <div v-if="!reducedMotion" class="story-footer" :class="{ 'is-light': activeSecond }"><span>SCROLL TO DISCOVER</span><span class="story-rule"></span><span>0{{ activeSecond ? '2' : '1' }} / 02</span></div>
    </div>
    <div v-if="reducedMotion" class="static-second">
      <div><p class="story-kicker"><span>02</span> NOURISHING OIL MIX</p><h2>Step 2: Length &amp;<br /><em>Softening Care</em></h2><p class="story-description">Give your lengths some love with a nourishing oil mix made for a softer-feeling finish.</p><RouterLink :to="{ path: '/catalog', query: { search: 'Nourishing Oil Mix' } }" class="story-button">Shop Nourishing Oil <span aria-hidden="true">↗</span></RouterLink></div><img src="/images/products/nourishingoilmix.webp" alt="Nourishing Oil Mix" />
    </div>
  </section>
</template>

<style scoped>
.product-story{height:300vh;position:relative;background:#f4e8e5}.story-stage{position:sticky;top:0;height:100vh;height:100svh;overflow:hidden;background:radial-gradient(ellipse at 70% 48%,#fffaf6 0%,#f3e4e1 48%,#e7d0d2 100%)}.story-light{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at 70% 45%,#fffaf5 0%,#f5e8e2 48%,#ead4cf 100%)}.story-layout{position:relative;z-index:1;max-width:1280px;margin:auto;height:100%;padding:115px 48px 80px;display:grid;grid-template-columns:1fr 1fr;align-items:center;color:#302324}.story-copy{max-width:520px}.story-kicker{font:600 10px 'Cinzel',serif;letter-spacing:.22em;display:flex;align-items:center;gap:15px;margin-bottom:28px}.story-kicker span{border:1px solid currentColor;border-radius:50%;height:32px;width:32px;display:grid;place-items:center;letter-spacing:0}.story-copy h1,.story-copy h2,.static-second h2{font:400 clamp(2.3rem,4vw,4.2rem)/1.13 'Cinzel',serif;letter-spacing:-.025em;margin:0}.story-copy em,.static-second em{display:block;font:400 1.3em/1 'Great Vibes',cursive;letter-spacing:0;margin-top:8px}.story-description{font-size:14px;line-height:1.8;max-width:360px;opacity:.8;margin:24px 0 30px}.story-button{display:inline-flex;align-items:center;gap:30px;border-radius:99px;background:#302324;color:#fff9f5;padding:16px 22px;font:600 10px 'Cinzel',serif;letter-spacing:.13em;text-transform:uppercase;transition:transform .25s cubic-bezier(.16,1,.3,1),background .25s}.story-button span{font:18px sans-serif}.story-button:focus-visible{outline:3px solid #d59fa9;outline-offset:4px}.is-light{color:#271e1e}.is-light .story-button,.static-second .story-button{background:#211a1a;color:#fff}.story-product{height:min(65vh,560px);position:relative;display:grid;place-items:center;overflow:visible}.story-orbit{position:absolute;width:min(90%,470px);aspect-ratio:1;border:1px solid currentColor;opacity:.16;border-radius:50%}.story-watermark{position:absolute;font:600 clamp(5rem,11vw,10rem) 'Cinzel',serif;letter-spacing:.1em;opacity:.09}.product-image{position:absolute;width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 30px 30px rgba(0,0,0,.22));pointer-events:none}.product-caption{position:absolute;bottom:3%;right:0;font:10px/1.7 'Cinzel',serif;letter-spacing:.12em;opacity:.65}.story-line,.story-footer{position:absolute;z-index:2;font:10px 'Cinzel',serif;letter-spacing:.2em;color:#473438}.story-line{top:125px;right:5%;opacity:.6}.story-footer{bottom:35px;left:50%;transform:translateX(-50%);width:min(calc(100% - 96px),1184px);display:flex;align-items:center;gap:18px}.story-footer.is-light{color:#392c2b}.story-rule{height:1px;background:currentColor;opacity:.3;flex:1}.reduced-motion{height:auto}.reduced-motion .story-stage{position:relative}.static-second{background:#f2e3e0;color:#271e1e;padding:80px max(24px,calc((100vw - 1184px)/2));display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:40px}.static-second img{width:100%;height:400px;object-fit:contain}@media(hover:hover) and (pointer:fine){.story-button:hover{transform:translateY(-2px);background:#584044}}@media(max-width:700px){.story-layout{padding:105px 24px 65px;grid-template-columns:1fr;grid-template-rows:auto minmax(0,1fr);gap:5px;align-content:center}.story-kicker{margin-bottom:12px;font-size:9px}.story-copy h1,.story-copy h2,.static-second h2{font-size:clamp(1.65rem,7vw,2.5rem)}.story-description{font-size:14px;line-height:1.5;margin:12px 0 16px}.story-button{padding:12px 18px}.story-product{height:100%;max-height:39vh;min-height:140px}.story-line{display:none}.product-caption{font-size:8px}.story-footer{bottom:18px;width:calc(100% - 48px);font-size:8px}.static-second{grid-template-columns:1fr;padding:64px 24px;gap:10px}.static-second img{height:280px}}
.story-copy{grid-column:1;grid-row:1}.story-product{grid-column:2;grid-row:1}@media(max-width:700px){.story-product{grid-column:1;grid-row:2}}

/* Keep the story within the space below the mobile navigation. */
@media (max-width: 700px) {
  .product-story { height: 250svh; }
  .story-stage { top: 72px; height: calc(100svh - 72px); }
  .story-layout { padding: 28px 24px 42px; grid-template-rows: auto minmax(0, 1fr); gap: 12px; align-content: stretch; }
  .story-copy h1, .story-copy h2, .static-second h2 { font-size: clamp(1.55rem, 7vw, 2.15rem); }
  .story-kicker { font-size: .625rem; letter-spacing: .16em; }
  .story-description { max-width: 32rem; font-size: .9375rem; line-height: 1.55; }
  .story-button { min-height: 48px; font-size: .6875rem; }
  .story-product { align-self: center; width: 100%; max-height: min(36svh, 340px); }
  .story-orbit { width: min(78%, 280px); }
  .story-watermark { font-size: clamp(4rem, 18vw, 6rem); }
  .product-caption { right: 0; bottom: 0; font-size: .5625rem; }
  .story-footer { font-size: .5625rem; }
  .reduced-motion { height: auto; }
  .reduced-motion .story-stage { top: auto; height: auto; min-height: 0; overflow: visible; }
  .reduced-motion .story-layout { height: auto; padding: 36px 24px 32px; grid-template-rows: auto auto; }
  .reduced-motion .story-product { height: 260px; max-height: none; }
  .static-second { padding: 40px 24px; }
}
</style>

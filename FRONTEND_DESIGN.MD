# FRONTEND DESIGN SYSTEM SPECIFICATION (FRONTEND_DESIGN.MD)
## Project: By Nzuri E-Commerce Storefront UI
**Framework Layer:** Vue.js 3 + Tailwind CSS  
**Design Philosophy:** Minimalist, Natural Elegance, Soft Floral Contrast, Mobile-Optimized Typography
**Source Inspiration:** Instagram Feed [@bynzuri.zm](https://www.instagram.com/bynzuri.zm/)

---

## 1. COLOR PALETTE CONFIGURATION

The color choices directly mirror the packaging and social media branding visible in the By Nzuri visual assets: soft background pastels, deep foliage contrasts, and clean text weights.

### 1.1 Tailwind v4 Theme Tokens

Add these custom definitions to your `main.css` `@theme` block:

```css
@theme {
  --color-nzuri-blush: #F3E1E5;
  --color-nzuri-accent: #E74C8C;
  --color-nzuri-cream: #FAF6F6;
  --color-nzuri-charcoal: #212121;
  --color-nzuri-slate: #6B6B6B;
  --color-nzuri-sage: #A3B899;
  --color-nzuri-pastel-pink: #FFD1E6;
  --color-nzuri-bubble-pink: #FBE7EE;
  --color-nzuri-star-yellow: #FFE600;
  --color-nzuri-dark-text: #212529;
}
```

### 1.2 Color Application Mapping

* **Primary Backgrounds:** `bg-nzuri-cream` or `bg-white` (to maximize whitespace readability).

* **Promo Components & Banners:** `bg-nzuri-blush` for hero cards, notification flags, and container backgrounds.

* **Core Text Headers & Bodies:** `text-nzuri-charcoal` or `text-nzuri-dark-text` to ensure a high contrast ratio passing accessibility checks.

* **Primary Buttons & Active States:** `bg-nzuri-charcoal text-white hover:bg-nzuri-accent` or an elegant reverse outline style.

---

## 2. TYPOGRAPHY MATRIX

The brand relies on a contrast between **expressive, high-elegance decorative script fonts** (used for accents like headers and banners) and **highly legible, structured sans-serif typography** for technical labels and product text.

### 2.1 Font Pairings

* **Accent/Display Font:** A fluid, signature-style, ultra-thin monoline calligraphic script typeface (e.g., *Brittany Signature*, *Herr Von Muellerhoff*, or *Pinyon Script*). Used explicitly for short design accents, testimonials, hero phrases, or price markers.

* **Interface & Copy Font:** A clean, crisp sans-serif typeface (e.g., *Inter*, *DM Sans*, or *Plus Jakarta Sans*). Used for all main UI components, inputs, buttons, navigation menus, and readable paragraph text.

### 2.2 System Typography Tokens

```css
/* Custom component utilities to attach to your CSS entry point (e.g., main.css) */
@layer utilities {
  .font-nzuri-signature {
    font-family: 'BrittanySignature', 'Herr Von Muellerhoff', cursive;
    font-weight: 300;
    letter-spacing: 0.05em;
    transform: rotate(-1deg);
  }

  .font-nzuri-interface {
    font-family: 'Inter', sans-serif;
    letter-spacing: -0.01em;
  }
}
```

---

## 3. CARD & CONTENT PACKAGING VISUAL PATTERNS

### 3.1 The Product Grid Card Component

Product cards follow a borderless, soft-shadow format that highlights the product imagery, avoiding heavy structural grids.

* **Image Wrapping Layer:** Aspect ratio fixed tightly at `aspect-[4/5]` or `aspect-square`. Images feature a very subtle rounded corner layout (`rounded-md` or `rounded-lg`).

* **Hover Interactions:** Implement a gentle scale transition (`hover:scale-[1.02] transition-transform duration-300`) to increase engagement when a user browses the storefront.

* **Information Stack:** Clean alignment to the left. The Title uses bold medium text (`font-medium text-base text-nzuri-charcoal`), immediately followed by an unadorned, readable price line (`text-sm font-semibold text-nzuri-slate`).

### 3.2 The Instagram Post Component (Text Overlay Panel)

By Nzuri frequently utilizes a rounded square white overlay container centered on top of an organic or product image backdrop to deliver text callouts.

#### Code Pattern Example:

```vue
<template>
  <div class="relative bg-cover bg-center h-96 w-full rounded-xl flex items-center justify-center p-6" style="background-image: url('/assets/hair-oils-bg.jpg')">
    <div class="bg-white/95 backdrop-blur-sm rounded-xl p-6 text-center max-w-sm border border-nzuri-blush/30 shadow-xl">
      <span class="text-xs font-semibold tracking-widest text-nzuri-slate block mb-2">@by.nzuri</span>
      <p class="text-sm uppercase tracking-wide leading-relaxed text-nzuri-charcoal font-medium">
        Sulphate free, silicon free and paraben free products that can be used by naturals, relaxed hair, locs and kids above 1 yr.
      </p>
    </div>
  </div>
</template>
```

---

## 4. UI ANIMATIONS & TRANSITIONS

To maintain a soothing, premium beauty aesthetic, UI element changes should feel lightweight and organic rather than snappy and mechanical.

* **Cart Drawer Transitions:** Slide movements from the right margin should employ ease-out curves (`transition-transform duration-500 ease-out`).

* **CTA Buttons (Add to Cart):** Use smooth background transitions paired with a minor scale effect upon clicking to confirm feedback.

```html
<button class="w-full bg-nzuri-charcoal text-white py-3 rounded-md uppercase tracking-wider text-xs font-semibold transition-all duration-300 hover:bg-nzuri-accent active:scale-95">
  Add To Cart
</button>
```

---

## 5. REUSABLE VUE.JS GLOBAL COMPONENT BLUEPRINTS

### 5.1 Hero Section Component (`HeroBanner.vue`)

```vue
<template>
  <section class="relative w-full bg-nzuri-cream overflow-hidden py-16 px-6 md:px-12 lg:px-24">
    <div class="absolute top-0 right-0 w-64 h-64 bg-nzuri-blush/30 rounded-full blur-3xl pointer-events-none"></div>

    <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
      <div class="space-y-6 text-center md:text-left z-10">
        <h1 class="text-4xl lg:text-6xl text-nzuri-charcoal tracking-tight font-light leading-tight font-nzuri-interface">
          Care for your hair, <br />
          <span class="font-nzuri-signature text-nzuri-accent text-5xl lg:text-7xl font-normal block mt-1">naturally.</span>
        </h1>
        <p class="text-nzuri-slate max-w-md mx-auto md:mx-0 text-sm md:text-base leading-relaxed font-nzuri-interface">
          100% natural, sulfate-free formulations designed purposefully for healthy texturized loops, locs, relaxed hair, and children.
        </p>
        <div class="pt-2">
          <router-link to="/shop" class="inline-block bg-nzuri-charcoal text-white px-8 py-3.5 text-xs font-medium uppercase tracking-widest rounded-md hover:bg-nzuri-accent transition-colors duration-300 shadow-md font-nzuri-interface">
            Explore Collection
          </router-link>
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-4">
          <img src="/assets/grid-hair-1.jpg" alt="By Nzuri Oil Product" class="rounded-2xl shadow-md w-full object-cover h-48 lg:h-64 aspect-[3/4]" />
          <div class="bg-nzuri-blush rounded-2xl p-6 flex flex-col justify-between h-32 lg:h-40">
            <span class="font-nzuri-signature text-nzuri-accent text-3xl">#nzurihair</span>
            <span class="text-xs uppercase font-semibold tracking-wider text-nzuri-charcoal font-nzuri-interface">100% Organic</span>
          </div>
        </div>
        <div class="pt-8 space-y-4">
          <img src="/assets/grid-hair-2.jpg" alt="By Nzuri Deep Conditioner" class="rounded-2xl shadow-md w-full object-cover h-64 lg:h-80 aspect-[3/4]" />
        </div>
      </div>
    </div>
  </section>
</template>
```

### 5.2 Customer Review Template (`CustomerReview.vue`)

This template reconstructs the exact layout matrix found in the brand's visual assets using the detected signature styling parameters:

```vue
<template>
  <div class="relative w-full max-w-4xl mx-auto my-12 p-8 bg-gradient-to-tr from-white to-nzuri-pastel-pink/30 rounded-3xl overflow-hidden flex flex-col md:flex-row items-center gap-8">

    <div class="w-full md:w-1/2 flex justify-center">
      <div class="relative bg-white p-4 rounded-3xl shadow-xl border border-nzuri-pastel-pink/20 max-w-[280px]">
        <img src="/assets/exfoliating-toner-bottles.jpg" alt="By Nzuri Exfoliating Toner" class="rounded-2xl w-full object-cover aspect-[3/4]" />
      </div>
    </div>

    <div class="w-full md:w-1/2 space-y-6">
      <div class="text-center md:text-left">
        <h3 class="font-nzuri-signature text-4xl lg:text-5xl text-nzuri-dark-text lowercase block leading-none">
          Exfoliating toner
        </h3>
        <span class="font-nzuri-interface font-light text-2xl tracking-wide text-nzuri-dark-text uppercase block mt-1">
          review
        </span>
      </div>

      <div class="space-y-4">
        <div class="bg-nzuri-bubble-pink rounded-2xl rounded-tl-none p-5 shadow-sm border border-nzuri-pastel-pink/10">
          <div class="flex items-center justify-between mb-2">
            <span class="font-nzuri-interface font-semibold text-sm text-nzuri-dark-text">Mainda</span>
            <span class="text-[10px] font-medium text-nzuri-slate">12:13 PM</span>
          </div>
          <p class="font-nzuri-interface text-xs text-nzuri-slate leading-relaxed">
            Luyando Luyando😭😭😭😭 How many times did I call your name? The toner?? Of course I'm using a good serum but the toner is already working wonders😭😭
          </p>
        </div>

        <div class="flex gap-1 justify-start pt-2">
          <svg v-for="i in 5" :key="i" class="w-5 h-5 text-nzuri-star-yellow fill-current" viewBox="0 0 24 24">
            <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>
```

---

## 6. ASSET CLEANUP & PACKAGING PIPELINE

* **Image Delivery Layout:** Ensure that background product images preserve their natural lighting. Use a slight warm tint or transparency layers on image placeholders to avoid stark white backgrounds that can detract from the brand's organic warmth.

* **Icon Selection:** Utilize fine, minimalist line icon sets (such as *Lucide Icons* or *Heroicons* set to `stroke-width="1.5"`) to maintain the delicate visual hierarchy across the shopping cart header, navigation bars, and searching rows.

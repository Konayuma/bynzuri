<script setup lang="ts">
const SUPPORT_EMAIL = 'hairskincare@bynzuri.com'
const EFFECTIVE_DATE = 'November 27, 2026'
</script>

<template>
  <div class="min-h-[80vh]">
    <section class="bg-nzuri-blush/40 py-12 px-4">
      <div class="max-w-3xl mx-auto text-center">
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-gold mb-2">Legal</p>
        <h1 class="font-heading text-3xl md:text-4xl font-semibold text-dark mb-3">Terms of Service</h1>
        <p class="text-muted text-sm md:text-base max-w-xl mx-auto">
          The terms and conditions governing your use of bynzuri.com and purchases made from By Nzuri.
        </p>
        <p class="text-xs text-muted mt-4">Last updated: {{ EFFECTIVE_DATE }}</p>
      </div>
    </section>

    <div class="max-w-3xl mx-auto px-4 py-10">
      <article class="bg-white rounded-[24px] p-6 sm:p-10 shadow-[0_8px_30px_rgba(0,0,0,0.06)] border border-primary/20 space-y-8 text-sm sm:text-base leading-relaxed text-dark">
        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">1. Acceptance of Terms</h2>
          <p class="text-muted">
            By accessing or purchasing from <strong class="text-dark">bynzuri.com</strong>, you agree to these Terms of Service and our
            <router-link to="/privacy-policy" class="text-dark font-medium underline underline-offset-4">Privacy Policy</router-link>.
            If you do not agree, please do not use our website.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">2. Accounts &amp; Security</h2>
          <p class="text-muted">
            To place an order, you must create an account with accurate contact information or sign in using Google. You are responsible
            for keeping your account credentials secure and for all activity under your account. Notify us immediately if you suspect
            unauthorized access.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">3. Products &amp; Pricing</h2>
          <p class="text-muted">
            All prices are listed in Zambian Kwacha (ZMW) unless stated otherwise and are subject to change without notice. We make every
            effort to display product descriptions, ingredients, and availability accurately, but we reserve the right to correct errors or
            cancel an order if an item is unavailable (with a full refund if payment was already collected).
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">4. Orders &amp; Payments</h2>
          <p class="text-muted">
            We accept MTN Mobile Money and Airtel Money. Orders are confirmed once payment is successfully verified. Unpaid orders may
            automatically expire after a holding period so stock can be returned to availability.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">5. Delivery</h2>
          <p class="text-muted">
            We deliver nationwide across Zambia, typically within 1–2 business days in Lusaka and 3–5 business days in other provinces.
            Delivery timelines are estimates and may vary due to courier schedules or circumstances beyond our control. Please ensure your
            delivery address and phone number are accurate at checkout.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">6. Returns, Exchanges &amp; Refunds</h2>
          <p class="text-muted">
            We accept returns within <strong class="text-dark">7 days of delivery</strong> for items that are unused, unopened, and in their
            original packaging. If you receive a damaged or incorrect item, contact us promptly with your order reference and we will arrange
            a replacement or refund. To initiate a return, email
            <a :href="`mailto:${SUPPORT_EMAIL}`" class="text-dark font-medium underline underline-offset-4">{{ SUPPORT_EMAIL }}</a>
            or submit an inquiry on our
            <router-link to="/help#contact-form" class="text-dark font-medium underline underline-offset-4">Help &amp; Support</router-link>
            page.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">7. Product Use</h2>
          <p class="text-muted">
            Our beauty and haircare products are for external use only. Please review product ingredient lists before use and perform a patch
            test if you have sensitive skin or known allergies. Product information on our website is not medical advice.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">8. Intellectual Property</h2>
          <p class="text-muted">
            All content on bynzuri.com—including the By Nzuri name, logos, product photography, text, and design—is owned by By Nzuri and
            may not be copied, reproduced, or used commercially without our prior written permission.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">9. Limitation of Liability</h2>
          <p class="text-muted">
            To the fullest extent permitted by law, By Nzuri is not liable for indirect, incidental, or consequential damages arising from
            your use of our website or products. Our total liability for any claim related to an order is limited to the amount you paid for
            that order.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">10. Governing Law &amp; Changes</h2>
          <p class="text-muted">
            These Terms of Service are governed by the laws of the Republic of Zambia. We may update these terms periodically; continued
            use of bynzuri.com after updates are posted constitutes acceptance of the revised terms.
          </p>
        </section>

        <section class="space-y-3 border-t border-primary/30 pt-6">
          <h2 class="font-heading text-xl font-semibold text-dark">11. Contact Us</h2>
          <p class="text-muted">
            Questions about these Terms of Service? Email us at
            <a :href="`mailto:${SUPPORT_EMAIL}`" class="text-dark font-medium underline underline-offset-4">{{ SUPPORT_EMAIL }}</a>
            or visit our
            <router-link to="/help#contact-form" class="text-dark font-medium underline underline-offset-4">Help &amp; Support</router-link>
            page.
          </p>
        </section>
      </article>
    </div>
  </div>
</template>

<script setup lang="ts">
const SUPPORT_EMAIL = 'hairskincare@bynzuri.com'
const EFFECTIVE_DATE = 'November 27, 2026'
</script>

<template>
  <div class="min-h-[80vh]">
    <section class="bg-nzuri-blush/40 py-12 px-4">
      <div class="max-w-3xl mx-auto text-center">
        <p class="text-xs font-semibold uppercase tracking-[0.18em] text-gold mb-2">Legal</p>
        <h1 class="font-heading text-3xl md:text-4xl font-semibold text-dark mb-3">Privacy Policy</h1>
        <p class="text-muted text-sm md:text-base max-w-xl mx-auto">
          How By Nzuri collects, uses, and protects your personal information when you shop with us or sign in to your account.
        </p>
        <p class="text-xs text-muted mt-4">Last updated: {{ EFFECTIVE_DATE }}</p>
      </div>
    </section>

    <div class="max-w-3xl mx-auto px-4 py-10">
      <article class="bg-white rounded-[24px] p-6 sm:p-10 shadow-[0_8px_30px_rgba(0,0,0,0.06)] border border-primary/20 space-y-8 text-sm sm:text-base leading-relaxed text-dark">
        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">1. Who We Are</h2>
          <p class="text-muted">
            By Nzuri (&ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;our&rdquo;) operates the online store at
            <strong class="text-dark">bynzuri.com</strong>, based in Lusaka, Zambia. This Privacy Policy explains how we handle
            personal data collected through our website, account registration, checkout, and customer support channels.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">2. Information We Collect</h2>
          <ul class="list-disc pl-5 space-y-2 text-muted">
            <li><strong class="text-dark">Account details:</strong> Your name, email address, phone number, and encrypted password when you create an account.</li>
            <li><strong class="text-dark">Google Sign-In data:</strong> If you choose to sign in with Google, we receive your verified email address and name from Google solely to create or authenticate your By Nzuri account. We do not access your Google contacts, Drive, or other Google services.</li>
            <li><strong class="text-dark">Order &amp; delivery details:</strong> Your shipping province, town, street address, contact phone number, and order history so we can fulfill and deliver your orders.</li>
            <li><strong class="text-dark">Payment information:</strong> Payments via MTN Mobile Money and Airtel Money are processed through our payment partner. We store transaction references and payment status, not your mobile money PIN.</li>
            <li><strong class="text-dark">Support inquiries &amp; reviews:</strong> Information you submit through our Help &amp; Support form, email, WhatsApp, or product reviews.</li>
          </ul>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">3. How We Use Your Information</h2>
          <ul class="list-disc pl-5 space-y-2 text-muted">
            <li>Create, verify, and secure your customer account (including sending one-time email verification and password reset codes).</li>
            <li>Process orders, confirm mobile money payments, and arrange nationwide delivery across Zambia.</li>
            <li>Send transactional emails such as order confirmations, payment receipts, and dispatch updates.</li>
            <li>Respond to customer support requests, returns, and exchanges.</li>
            <li>Prevent fraud, abuse, and unauthorized access to our platform.</li>
          </ul>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">4. Sharing Your Information</h2>
          <p class="text-muted">
            We do not sell or rent your personal information. We only share data with trusted service providers necessary to operate our store:
          </p>
          <ul class="list-disc pl-5 space-y-2 text-muted">
            <li><strong class="text-dark">Payment processing:</strong> To initiate and verify MTN Mobile Money and Airtel Money payments.</li>
            <li><strong class="text-dark">Delivery partners:</strong> Your name, delivery address, and phone number to complete delivery.</li>
            <li><strong class="text-dark">Transactional email &amp; hosting providers:</strong> To send account verification codes, order updates, and host our website securely.</li>
            <li><strong class="text-dark">Legal compliance:</strong> When required by applicable Zambian law or a valid legal request.</li>
          </ul>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">5. Cookies &amp; Session Storage</h2>
          <p class="text-muted">
            We use essential HttpOnly session cookies and browser storage to keep you signed in securely, protect against cross-site request forgery (CSRF), and preserve your shopping cart and wishlist. We do not use third-party advertising trackers.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">6. Data Security &amp; Retention</h2>
          <p class="text-muted">
            We protect your data using HTTPS encryption, hashed passwords, and access controls. We keep your account and order records for as long as your account is active or as needed to fulfill legal, accounting, and customer-service obligations.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">7. Your Rights</h2>
          <p class="text-muted">
            You may update your profile and saved addresses anytime from your account page. You may also contact us to request access to, correction of, or deletion of your personal data.
          </p>
        </section>

        <section class="space-y-3">
          <h2 class="font-heading text-xl font-semibold text-dark">8. Changes to This Policy</h2>
          <p class="text-muted">
            We may update this Privacy Policy from time to time. Any changes will be posted on this page with an updated effective date.
          </p>
        </section>

        <section class="space-y-3 border-t border-primary/30 pt-6">
          <h2 class="font-heading text-xl font-semibold text-dark">9. Contact Us</h2>
          <p class="text-muted">
            If you have questions about this Privacy Policy or your personal data, email us at
            <a :href="`mailto:${SUPPORT_EMAIL}`" class="text-dark font-medium underline underline-offset-4">{{ SUPPORT_EMAIL }}</a>
            or reach out via our
            <router-link to="/help#contact-form" class="text-dark font-medium underline underline-offset-4">Help &amp; Support</router-link>
            page.
          </p>
        </section>
      </article>
    </div>
  </div>
</template>

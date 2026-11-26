# By Nzuri implementation tracker

Last reviewed: 26 November 2026
Source of requirements: [Software Requirements Specification](By_Nzuri_Requirements_Specification.md)

This is a source-code baseline, not a release certification. **In progress** means some implementation exists but the complete requirement has not been verified. **To do** means work or evidence is still needed. Check an item only after its acceptance criteria have been demonstrated and the evidence recorded here. No tests or live integrations were run for this baseline.

## Recent implementation

- **In progress — search sitemap:** A dynamic sitemap lists public storefront pages and active products via the API and Cloudflare route, with `robots.txt` discovery. Local verification is required; live deployment, preferred hostname and Search Console submission remain to be checked.
- **In progress — account rendering and session recovery:** Account lists tolerate missing records, locally stored wishlist entries are validated, public delivery data no longer uses a session token, and late unauthorized responses reuse an already refreshed token. Frontend regression tests pass; confirm the deployed account page and investigate any remaining live 401 responses.
- **In progress — international account phone numbers:** Registration offers a country calling-code selector and saves international-format account numbers. Zambia-specific delivery and mobile-money number requirements remain in checkout. Focused tests and the production build pass; live and device verification remain outstanding.
- **In progress — checkout address reuse and verification recovery:** Signed-in customers can save a delivery address and phone at checkout, with a default address reused on future visits. Account address access is scoped to its owner, and the server validates province and town. Verification and location-loading failures offer recovery. Automated tests cover local behavior; browser and live deployment verification remain outstanding.
- **In progress — registration email verification:** New accounts require a six-digit email code before sign-in. Codes expire, limit guesses and use the existing scheduled Resend sender. Backend and frontend tests cover local behavior; deployment and live delivery verification remain outstanding. Existing accounts are unchanged; password reset email delivery remains unfinished.
- **In progress — branded order emails:** Order messages now have a responsive receipt-style HTML layout alongside plain text; payment status remains explicit. Focused email tests pass; verify delivery and rendering in real email clients after deployment.
- **In progress — admin analytics:** Sales history, top products and paginated orders are implemented. Sales use current paid/fulfilment statuses and the order creation date, include delivery, and are not a payment-date or refund ledger. Local API tests and frontend build validate the implementation; live data and browser verification remain outstanding.
- **In progress — transactional order email:** A durable Resend outbox queues unpaid order confirmations, owner order alerts, confirmed-payment receipts and alerts, and delivery-status updates. Duplicate events are guarded; retries use provider idempotency. Automated tests cover local behavior, but production requires verified DNS, a configured API key and a running scheduler; live delivery and bounce handling are not yet verified. See `DEPLOYMENT.md`.

## Immediate priorities

- [ ] **P0 — Secure and verify payments (FR-4.1–4.4):** Exercise Lenco in its test environment, including signed and invalid webhooks, repeated callbacks, failed payments, status verification and simultaneous requests. Confirm provider contract, amounts, ownership and state transitions before enabling real payments.
- [~] **P0 — Complete account email delivery:** Registration verification is implemented and requires live delivery verification; password reset email delivery remains a TODO in `backend/apps/users/views.py`.
- [ ] **P0 — Validate checkout and stock under concurrency:** Test guest cart merge, delivery pricing, order creation and inventory locking with PostgreSQL and concurrent buyers, including failure and retry paths.
- [ ] **P0 — Repair order creation lifecycle:** The order idempotency key is derived from the persistent cart ID, so a later purchase using the same cart can be rejected. Review stock rollback when a later cart item is unavailable and define recovery for unpaid orders before live use.
- [ ] **P1 — Address production security and deployment:** Review token storage, JWT signing, production CORS, HTTPS, secrets and cloud storage against the SRS; verify the deployed configuration.
- [ ] **P1 — Establish a clean quality baseline:** Run frontend type-checked build, lint and tests, backend tests and a browser checkout smoke test; record results and fix failures.

## Functional requirements

| ID | Requirement | Status and current evidence | Remaining acceptance work |
| --- | --- | --- | --- |
| FR-1.1 | Registration and authentication | In progress — user models, API, auth pages and tests exist. Email delivery has TODOs. | Verify unique email/phone, password hashing, registration, login and actual email delivery. |
| FR-1.2 | JWT pair and lifetimes | In progress — `backend/config/settings.py` configures 15-minute access and 7-day refresh tokens. | Verify signing is asymmetric as specified, token issuance, rotation, expiry and revocation. |
| FR-1.3 | Authenticated API client and secure token handling | In progress — `frontend/src/services/api.ts` injects and refreshes tokens; tokens are stored in localStorage. | Resolve the SRS token-storage security requirement and test refresh, expiry and logout. |
| FR-1.4 | Customer and staff permissions | In progress — customer and admin routes and backend endpoints exist. | Audit server-side authorization on every write and personal-data endpoint; test customer, staff and anonymous access. |
| FR-2.1 | Product gallery and details | In progress — home, catalog, product detail, gallery and product API exist. | Verify ZMW prices, categories, media, usage directions and mobile presentation with real data. |
| FR-2.2 | Search and filtering | In progress — product API declares search fields and category filtering; catalog UI exists. | Verify search/filter behavior and appropriate database indexes and query performance. |
| FR-2.3 | Stock tracking and out-of-stock behavior | In progress — order creation uses a transaction and `select_for_update()` on products. | Verify decrement and zero-stock API/UI behavior, concurrent purchases and stock recovery on failed/cancelled orders. |
| FR-3.1 | Persistent guest cart and merge | In progress — `frontend/src/stores/cart.ts` persists a guest cart and calls the merge API. | Test reload, login/register merge, duplicate items, invalid stock and merge failures end to end. |
| FR-3.2 | Province and town selection | In progress — delivery models/API and checkout page exist. | Verify all ten provinces, dependent towns, validation and persisted delivery address. |
| FR-3.3 | Delivery methods and dynamic pricing | In progress — delivery management and checkout code exist. | Verify zone/method eligibility and server-calculated totals for pickup, local and intercity delivery. |
| FR-4.1 | Payment aggregation | In progress — Lenco integration and mobile-money options exist. | Confirm supported methods and production credentials; test provider initiation and reconcile the SRS card requirement with actual provider support. |
| FR-4.2 | Payment idempotency | In progress — unique payment keys and order idempotency logic exist. | Test retries and concurrent requests against the provider; confirm key lifecycle and no duplicate charges. |
| FR-4.3 | Signed, atomic payment webhook | In progress — signature verification and an atomic webhook handler exist in `backend/apps/payments/`. | Validate the signature scheme against the provider, reject invalid events and prove duplicate/out-of-order callbacks cannot corrupt order state. |
| FR-4.4 | Server-side payment verification fallback | In progress — payment status code calls Lenco collection status. | Confirm verified provider responses update the correct order safely when a webhook is missing; test pending, success and failure. |
| FR-5.1 | Admin product management | In progress — admin product page and product endpoints exist. | Verify staff-only create/edit/archive, pricing and image uploads, including error handling. |
| FR-5.2 | Admin order pipeline | In progress — admin order page and order endpoints exist. | Verify all required milestones, permitted transitions, authorization and customer-visible status. |

## Non-functional requirements

| ID | Requirement | Status and current evidence | Remaining acceptance work |
| --- | --- | --- | --- |
| NFR-1.1 | Mobile performance | To do — responsive UI exists; no current measurements recorded. | Test mobile and in-app browser layouts; measure CLS < 0.1 and FCP < 1.5 s under agreed conditions. |
| NFR-1.2 | Optimize uploaded images | In progress — `backend/apps/products/signals.py` resizes and converts images to WebP. | Verify upload paths, image quality, file handling and cloud storage using representative images. |
| NFR-1.3 | Catalog API latency | To do — search configuration exists; performance is unmeasured. | Measure representative PostgreSQL catalog reads under normal load and demonstrate < 300 ms. |
| NFR-2.1 | TLS 1.3 | To do — deployment-level enforcement is unverified. | Verify HTTPS and TLS configuration for browser, API and payment-provider connections in production. |
| NFR-2.2 | CORS allowlist | In progress — allowed origins are configurable in Django settings. | Verify exact production origins and reject unauthorized origins in deployment tests. |
| NFR-2.3 | PostgreSQL row locking | In progress — checkout locks products during order creation. | Verify other relevant inventory writes and concurrency behavior against PostgreSQL; SQLite is insufficient for this check. |
| NFR-3.1 | Independent cloud media/static storage | In progress — Django storage configuration and R2 environment settings exist. | Verify production static and media storage, access permissions, delivery and persistence across deployments. |

## Additional project workflows

- [ ] Verify product reviews and permissions using `backend/apps/reviews/` and the product detail page.
- [ ] Verify WhatsApp webhook, messaging, task processing and failure recovery with configured credentials; code and tests exist under `backend/apps/whatsapp/`.
- [ ] Verify account/profile, addresses, order history, wishlist and help flows in the browser.
- [ ] Verify local start/stop scripts, migrations, seed data and Docker deployment on a clean environment; document any prerequisites or failures.
- [ ] Verify admin dashboard analytics and delivery configuration against real orders and zones.

## Verification log

| Date | Scope | Result | Evidence / follow-up |
| --- | --- | --- | --- |
| 2026-11-17 | Lenco MTN/Airtel scaffold | Implementation and mocked payment tests added; provider sandbox and PostgreSQL concurrency remain unverified. | See `backend/apps/payments/tests/test_lenco_flow.py` and README setup. |
| 2026-11-17 | Tracker baseline | Source and requirements reviewed; runtime verification not performed at baseline. | Run the quality baseline and record commands, results, environment and any issues here. |

## Maintenance

Update this tracker whenever a requirement changes or a task is completed. Record the test command or manual scenario, environment and result; link to the relevant code, issue or evidence. Split unresolved failures into actionable items and leave the parent requirement open until its acceptance criteria pass.

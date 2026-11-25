# Deploying By Nzuri

This setup builds the Vue storefront on **Cloudflare Pages**, runs Django on **Render**, and uses **Neon PostgreSQL**. It also uses a Cloudflare R2 bucket for persistent product uploads. No accounts, domains, credentials or cloud resources are created by this repository.

## 1. Create the database and storage

1. Create a Neon project and copy its PostgreSQL connection string into a secure place. Use the pooled connection string with `sslmode=require` and retain any additional parameters Neon supplies. Choose a region close to the Render service.
2. Create a Cloudflare R2 bucket, an R2 API token restricted to that bucket, and an HTTPS public custom domain (or an R2 public development URL for testing). Uploaded catalog images are public. `R2_PUBLIC_DOMAIN` is the hostname only, without `https://` or a trailing slash. Do not commit credentials.

## 2. Deploy the API on Render

Connect the repository to Render and create a Blueprint from the root `render.yaml`. It creates a Python web service rooted at `backend`. Choose a suitable service plan. Render generates `DJANGO_SECRET_KEY`; supply these values when prompted:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | The complete Neon PostgreSQL connection string, including `sslmode=require`. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated API hostnames without schemes, e.g. `api.example.com`. Render's own hostname is added automatically. |
| `CORS_ALLOWED_ORIGINS` | Exact storefront origins with scheme, e.g. `https://shop.example.com,https://project.pages.dev`. Include only origins you trust. |
| `CSRF_TRUSTED_ORIGINS` | Exact HTTPS storefront and API origins where applicable, e.g. `https://shop.example.com,https://api.example.com`. |
| `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` | Restricted R2 API credentials. |
| `R2_BUCKET_NAME` | The bucket name. |
| `R2_ENDPOINT_URL` | `https://<account-id>.r2.cloudflarestorage.com`. |
| `R2_PUBLIC_DOMAIN` | Public media hostname, e.g. `media.example.com` or the hostname of an R2 public development URL. |

`REQUIRE_PERSISTENT_MEDIA=true` in the Blueprint makes missing R2 configuration a startup error instead of silently losing uploads on Render's ephemeral filesystem. Configure DNS and public access for the R2 domain before relying on uploaded images. Use the provider's dashboard to set secret variables, and never add them to Vite or Git.

The build installs requirements and collects static files. The start script runs migrations and then starts Gunicorn; `/api/health/` checks the database. This works on a single instance, including plans without a pre-deploy command. For multiple instances, move migrations to a single paid Render pre-deploy command and remove them from the per-instance start command to avoid concurrent migrations. Test and back up the database before deploying schema changes.

The production database is separate from local SQLite. Initialize an empty production database deliberately from a Render shell (or a trusted environment with the same variables):

```bash
cd backend  # omit if the Render shell already starts in backend
python manage.py shell < scripts/seed_data.py
python manage.py import_signature_catalog
python manage.py createsuperuser
```

The signature import does not overwrite existing products and gives new items **zero stock** until an administrator verifies availability. Existing local SQLite data and uploaded files are not automatically migrated; migrate them separately if needed.

## 3. Deploy the storefront on Cloudflare Pages

Create a Pages project connected to this repository using:

- Root directory: `frontend`
- Build command: `npm run build`
- Build output directory: `dist`
- Node.js: 24 (`frontend/.nvmrc`)
- Build environment variable: `VITE_API_BASE_URL=https://<your-render-api-host>/api`

Set the API URL for every Pages environment you actually deploy; preview deployments need a backend that allows their exact origin. The Pages build fails if the variable is missing or is not an HTTPS API URL. Vite variables are public and must never contain credentials. After deploying, add the exact Pages/custom-domain origin to Render's `CORS_ALLOWED_ORIGINS` and redeploy the API. Add any custom domains in Pages before updating DNS. Pages serves the Vue SPA for deep links when there is no top-level `404.html`; do not add one without configuring equivalent routing.

## 4. Verify before serving customers

- Visit the Render `/api/health/` URL and Django `/admin/`; verify the admin's static assets load.
- Open a Pages deep link such as `/product/growth-elixir` directly and on refresh. Check the browser network panel for HTTPS API requests and CORS errors.
- Verify public catalog/search, admin login and roles, saved addresses, stock, checkout, and payment callbacks with test credentials before enabling live payments. Configure Lenco separately (`LENCO_API_KEY` and provider webhook settings); never put provider secrets in Pages.

### Optional Lenco relay on Neon

The `functions/lenco-relay.mjs` function can route mobile-money initiation and status requests through Neon. It accepts only those two Lenco paths and requires a high-entropy `LENCO_RELAY_SECRET`. The existing Django backend remains responsible for authentication, order totals, payment state and webhook verification. It sends the Lenco API token to the relay over HTTPS; the relay does not store it.

Deploy the function to the intended Neon project and branch with `neon functions deploy lencorelay --src functions/lenco-relay.mjs`. Configure `LENCO_RELAY_SECRET` on the function through an appropriately protected deployment workflow. Set the same secret and the function's invocation URL (without a path) as `LENCO_RELAY_SECRET` and `LENCO_RELAY_URL` on the Render backend, then deploy the backend. Keep `LENCO_API_KEY` configured on Render. Never place either secret in source control or the browser. Remove `LENCO_RELAY_URL` and redeploy to restore direct Lenco requests. A relay failure is treated as an uncertain payment, so check its status before retrying.

Verify the Neon project region supports Functions, test an unauthorized function request, and then test a real collection only after deployment. A working relay does not guarantee that Lenco will accept the payment.
- Upload a test product image, check its public R2 URL, and confirm it survives an API redeploy. Remove only your own disposable test data afterwards.

## Known launch work

- Registration verification and password reset email delivery are **not implemented** in the current backend; the API currently reports a link was sent but contains TODOs instead of sending it. Configure and implement real mail delivery before advertising those flows.
- WhatsApp notifications use Celery and Redis. Provision a Redis-compatible broker and a separate Celery worker with matching environment variables and `MICHOWAPI_API_KEY` if those notifications are required; the Blueprint defines only the web service. Without a worker, queued notifications are not delivered.
- Payment-provider credentials, webhook configuration, production domain ownership, transactional email, stock levels, and existing data migration must be handled in the relevant provider dashboards. These cannot be verified from repository configuration alone.

### Customer sessions and unpaid-order expiry

The browser keeps access tokens in memory and the API keeps rotating refresh tokens in an HttpOnly cookie. Deploy the frontend and backend together. Existing localStorage sessions are discarded, so customers must sign in again. Cloudflare Pages proxies session requests through `/api/auth/` so the cookies are first-party. Set `VITE_API_BASE_URL` to the HTTPS Render API URL ending in `/api` as both a Pages build variable and a Pages runtime environment variable, then redeploy Pages. The Pages project root must be `frontend` so its `functions` directory is deployed. Set `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` on Render to the exact HTTPS storefront origins, including any custom domain, and redeploy the API. Test sign-in, reload, sign-out, and account creation in a browser that blocks third-party cookies. Do not expose the refresh cookie to JavaScript.

Unpaid orders older than 24 hours are eligible for automatic cancellation and stock restoration only if there is no pending, processing, or successful payment. Orders with uncertain payments remain reserved for reconciliation. The hourly Celery beat schedule is configured in Django, but it only runs when an actual Celery worker, Celery beat, and broker are running. Provision and monitor those services in production, or schedule `python manage.py expire_unpaid_orders` hourly using a scheduler connected to the same database. This repository does not provision a production scheduler. Use `--hours` to choose an expiry of at least one hour for a manual invocation. A paid order cannot be cancelled through the status endpoint until a refund workflow is implemented.

### PostgreSQL locking checks

Run the checkout and payment concurrency checks against a **disposable local PostgreSQL database**, never production. The configured user must be able to create and drop Django's separate test database. For example, with a local test-only server on port 55439:

```bash
cd backend
env -u DATABASE_URL USE_SQLITE=false DB_HOST=127.0.0.1 DB_PORT=55439 DB_NAME=bynzuri_test DB_USER=bynzuri_test DB_PASSWORD='your-local-test-password' \
  ../.venv/bin/python -m pytest apps/orders/tests/test_postgres_concurrency.py -q
```

These tests intentionally skip on SQLite. They exercise competing purchases for the last item, concurrent initiation of one payment, and conflicting provider updates using separate PostgreSQL connections. They do not contact Lenco or verify production configuration.

### Order and payment emails through Resend

The order service writes an email outbox in the same database transaction as checkout, confirmed payment, and dispatch/delivery/cancellation changes. A new order queues an explicitly **payment-pending** confirmation and an owner notification. A matching, successful Lenco callback or verified status query queues a customer payment receipt and owner payment alert. Dispatch, delivery and cancellation create customer updates. Repeated callbacks and checkout retries do not create duplicate notifications. A provider-accepted message is not proof of delivery: monitor Resend for delivery, bounces and quota usage. Existing historical orders are not automatically backfilled. Registration, email verification and password reset remain separate unfinished work.

1. Verify `bynzuri.com` as a sending domain in Resend and add its **sending** DNS records without replacing Cloudflare Email Routing's root inbound MX records. Set up Cloudflare forwarding `hairskin@bynzuri.com` to `hairskinbynzuri@gmail.com` and test it separately. Customer messages set Reply-To to `hairskin@bynzuri.com`; replying from personal Gmail will still use the Gmail address unless a separate business sending solution is configured.
2. Deploy this backend and run Django migrations before activating the sender. On the web service set `ORDER_NOTIFICATION_EMAIL=hairskin@bynzuri.com` (the default). The sender also needs `RESEND_API_KEY`, `RESEND_FROM_EMAIL` (default `HairSkin by Nzuri <hairskin@bynzuri.com>`), `RESEND_REPLY_TO=hairskin@bynzuri.com`, `DATABASE_URL` pointing at exactly the web service's database, and a `DJANGO_SECRET_KEY`. Keep the API key server-side and never commit it. Sender and web must use the same owner address.
3. `render.yaml` defines `bynzuri-order-email-sender`, a separately billed Render cron service running `python manage.py process_order_emails --limit 100` every five minutes. Provision it in Render and supply its secret environment variables; verify service and database settings before enabling it. Render bills cron runtime and has a minimum monthly service charge; check current pricing. Without a running scheduler, queued mail does **not** send. A separately managed scheduler with the same command is also valid.
4. Send a test order with Lenco test credentials. Check the pending confirmation and owner alert, then confirm payment and check the receipt and payment alert. Test dispatch and delivery, and inspect `Order emails` in Django admin plus the Resend dashboard. Test the Cloudflare forward independently. No real Resend or Lenco delivery has been verified by repository tests.

Failures are retried with backoff while inside Resend's 24-hour idempotency window; a notification that cannot safely be retried or has a permanent error is marked `needs_review`. An operator must check the matching message in Resend before retrying, since provider acceptance may have occurred even if a response was lost. Once sure a resend is appropriate, run `python manage.py process_order_emails --retry-reviewed <id> --confirm-provider-checked` in the sender environment. Retrying after the provider's key expires may send a duplicate; never blindly reset all failed records. The admin outbox stores customer contact and order data, so restrict admin access and establish retention. Webhooks for delivered/bounced events, automatic alerting of failures, and automatic backfilling of historical orders are not implemented.

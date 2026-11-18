# By Nzuri

Premium beauty and haircare e-commerce platform for the Zambian market.

## Tech Stack

- **Frontend**: Vue 3, TypeScript, Vite 8, Tailwind CSS 4, Pinia, Vue Router
- **Backend**: Django 6, Django REST Framework, PostgreSQL 16, Redis, Celery
- **Infrastructure**: Docker Compose, Nginx reverse proxy, Cloudflare R2 (S3-compatible)

## Quick Start

```bash
# Clone and start
git clone https://github.com/bynzuri/bynzuri.git
cd bynzuri
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Development

To start the local backend and frontend together, install Python 3, Node.js and
npm, and configure `backend/.env` and `frontend/.env` using the examples. Then
run from the project root:

```bash
./scripts/start.sh
```

The script creates a Python virtual environment if needed, installs missing or
outdated dependencies, applies migrations, starts Django on `127.0.0.1:8001` and starts
Vite. Press Ctrl+C or run `./scripts/stop.sh` in another terminal to stop both
servers. The scripts require Linux and `flock`. Redis and Celery must be started
separately when working on features that require them.

To add the eight products shown in the signature collection to a new database, run:

```bash
cd backend
USE_SQLITE=true ../.venv/bin/python manage.py import_signature_catalog
```

The import is safe to repeat and leaves existing products untouched. New products
start with zero stock; confirm availability in the admin before selling them. Run
the command with your production environment configured and without `USE_SQLITE=true`
to import into PostgreSQL.

Local startup uses `backend/db.sqlite3` by default and preserves its existing
data. Production uses PostgreSQL by default. To use PostgreSQL with the local
startup script, start the configured database and run `USE_SQLITE=false
./scripts/start.sh`.

### Frontend

```bash
cd frontend
npm install
npm run dev          # Start dev server
npm run build        # Production build
npm run test         # Run tests
npm run lint         # Lint with ESLint
npm run format       # Format with Prettier
```

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 127.0.0.1:8001
python manage.py test  # Run tests
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Cloudflare Pages, Render, Neon, persistent media, setup and launch checks.

## Environment Variables

### Backend (`backend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | dev key (change in prod) |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_NAME` | Database name | `bynzuri` |
| `DB_USER` | Database user | `bynzuri` |
| `DB_PASSWORD` | Database password | `bynzuri` |
| `CELERY_BROKER_URL` | Redis URL | `redis://localhost:6379/0` |
| `R2_ACCESS_KEY_ID` | Cloudflare R2 key | - |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 secret | - |
| `R2_BUCKET_NAME` | R2 bucket name | `bynzuri` |
| `R2_ENDPOINT_URL` | R2 endpoint | - |
| `LENCO_API_KEY` | Lenco API secret key | - |
| `LENCO_API_BASE_URL` | Lenco v2 API base URL | `https://api.lenco.co/access/v2` |

### Frontend (`frontend/.env`)

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8001/api` for local development |

For local development, set `VITE_API_BASE_URL=http://localhost:8001/api` in `frontend/.env` and restart Vite. Port 8001 keeps the Bynzuri API separate from other local services; the Docker configuration retains its existing port mapping.

## API Endpoints

### Auth
- `POST /api/auth/token/` - Login (get JWT tokens)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/register/` - Register new account
- `GET /api/auth/profile/` - Get/update profile
- `POST /api/auth/forgot-password/` - Request password reset
- `POST /api/auth/reset-password/` - Reset password with token
- `GET /api/auth/verify-email/` - Verify email with token
- `POST /api/auth/resend-verification/` - Resend verification email

### Products
- `GET /api/products/` - List products
- `GET /api/products/<slug>/` - Product detail
- `GET /api/categories/` - List categories

### Cart
- `GET /api/cart/` - Get cart
- `POST /api/cart/add/` - Add to cart
- `PATCH /api/cart/items/<id>/` - Update item
- `DELETE /api/cart/items/<id>/` - Remove item

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET /api/orders/<id>/` - Order detail

### Payments
- `POST /api/payments/initiate/` - Initiate payment
- `POST /api/payments/webhook/` - Payment webhook (provider callbacks)
- `GET /api/payments/status/<order_id>/` - Payment status

### Other
- `GET /api/health/` - Health check
- `GET /api/reviews/` - Product reviews
- `GET /api/delivery/` - Delivery zones

## Project Structure

```
bynzuri/
├── backend/
│   ├── apps/
│   │   ├── users/          # Auth, profiles, addresses
│   │   ├── products/       # Products, images, categories
│   │   ├── cart/           # Shopping cart
│   │   ├── orders/         # Order management
│   │   ├── payments/       # MTN MoMo, Airtel Money, Visa/MC
│   │   ├── delivery/       # Delivery zones, pricing
│   │   ├── reviews/        # Product reviews
│   │   ├── dashboard/      # Admin dashboard analytics
│   │   └── whatsapp/       # WhatsApp Cloud API integration
│   ├── config/             # Django settings, URLs, WSGI
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Route-level page components
│   │   ├── stores/         # Pinia state stores
│   │   ├── services/       # API service layer
│   │   ├── layouts/        # Layout components (navbar, footer)
│   │   ├── styles/         # Global styles, fonts, tokens
│   │   ├── types/          # TypeScript type definitions
│   │   └── __tests__/      # Unit and component tests
│   └── package.json
├── nginx/                  # Nginx reverse proxy configs
├── docker-compose.yml
└── README.md
```

## Payment Methods

- **MTN Mobile Money** - Primary method for Zambian customers (via Lenco API)
- **Airtel Money** - Alternative mobile money (via Lenco API)
All payments are processed server-side via the Lenco API. The frontend never touches API keys.

Set `LENCO_API_KEY` in `backend/.env` to the token supplied by Lenco. Configure a publicly reachable HTTPS webhook URL ending in `/api/payments/webhook/` in the Lenco dashboard. Webhook signatures use the SHA-256 hash of the API token as the HMAC-SHA-512 key; no separate webhook secret is required. The API base URL may be overridden with `LENCO_API_BASE_URL` when Lenco supplies an environment-specific endpoint.

Use Lenco sandbox credentials and its [test mobile money accounts](https://lenco-api.readme.io/v2.0/reference/test-cards-and-accounts) to verify MTN and Airtel success, failure, callbacks, and status checks before accepting real payments. A pending or uncertain payment remains attached to its order; customers can check its status from order history. Retrying is allowed after a confirmed failure. Provider setup and real transactions have not been verified by the automated tests.

## License

Proprietary. All rights reserved.

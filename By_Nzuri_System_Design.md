# SYSTEM DESIGN SPECIFICATION (DESIGN.MD)
## Project: By Nzuri E-Commerce Platform
**Architecture:** Headless & Decoupled Framework (Vue.js 3 + Django REST Framework)  
**Database:** PostgreSQL with Row-Level Transaction Locking  
**Target Environment:** Mobile-First Consumer Platform (Zambia)

---

## 1. ARCHITECTURAL OVERVIEW

The By Nzuri system implements a decoupled, headless architecture designed to maximize mobile rendering speeds while maintaining strict data consistency at the data layer. 

By separating the user interface (**Vue.js 3 SPA**) from the business engine (**Django REST Framework**), the platform ensures that heavy browser rendering in Instagram's in-app viewport does not choke server operations. Media assets are fully offloaded to an external Object Storage CDN.

### 1.1 End-to-End Component Flow

```
+------------------------------------------------------------------------+
|                          CLIENT TIER (VUE.JS 3)                        |
|   +-----------------------+                    +-------------------+   |
|   |   Consumer SPA (Web)  |                    | Admin Portal UI   |   |
|   +-----------------------+                    +-------------------+   |
+------------------------------------------------------------------------+
            |                                              |
     HTTPS  | JSON (JWT Auth)                       HTTPS  | JSON (JWT Auth)
            v                                              v
+------------------------------------------------------------------------+
|                         APPLICATION TIER (DJANGO)                      |
|   +----------------------------------------------------------------+   |
|   |                     Django REST Framework                      |   |
|   |  [Auth Middleware] [Pydantic/Serializers] [Signal Observers]  |   |
|   +----------------------------------------------------------------+   |
+------------------------------------------------------------------------+
            |                                              |
      SQL   | (Pessimistic Locks)                  HTTPS   | REST (Webhooks)
            v                                              v
+-----------------------+                        +-----------------------+
|      DATA TIER        |                        |    EXTERNAL ROUTING   |
| +-------------------+ |                        | +-------------------+ |
| | PostgreSQL DB     | |                        | | Payment Gateway   | |
| +-------------------+ |                        | | (Paystack/DPO)    | |
|                       |                        | +-------------------+ |
| +-------------------+ |                        |                       |
| | AWS S3 / R2 Bucket| |                        |                       |
| +-------------------+ |                        |                       |
+-----------------------+                        +-----------------------+
```

---

## 2. COMPONENT DESIGN & TECH STACK

### 2.1 Frontend Client (Vue.js 3 Ecosystem)
* **Runtime Environment:** Vite (optimized for lightning-fast Hot Module Replacement and ultra-lean production bundling).
* **State Management:** Pinia. Two primary global stores are isolated:
  1. `CartStore`: Tracks item footprints, volumes, and calculates sub-totals. Persists state locally via browser storage synchronization.
  2. `UserStore`: Stores encrypted session structures and JWT access parameters.
* **UI Foundation:** Tailwind CSS paired with a strict Mobile-First design matrix, preventing layout shifting (CLS) inside Instagram's in-app webviews.
* **Network Client:** Axios, configured with automated request/response interceptors to securely handle token renewal sequences smoothly.

### 2.2 Backend API Engine (Django REST Framework)
* **Application Core:** Django WSGI/ASGI application architecture executing Python 3.
* **Authentication Engine:** `djangorestframework-simplejwt`. Validates stateless tokens via public/private validation keys without repetitive database performance penalties.
* **Validation Layer:** Django REST Serializers. Enforces aggressive type validation, escaping, and sanitization before writing payloads to the database tier.
* **Media Optimization Wrapper:** `Pillow` framework hooked into Django signals (`post_save`). Automatically decompresses, standardizes proportions, and transcodes raw admin uploads into highly portable `.webp` binaries.

---

## 3. DATA ARCHITECTURE (DATABASE MODELS)

The PostgreSQL data tier enforces strong consistency via explicit indexing strategies and relational constraints.

```
                  +-------------------+
                  |     Category      |
                  +-------------------+
                  | id (PK, UUID)     |
                  | name (VarChar)    |
                  | slug (SlugField)  |
                  +-------------------+
                            |
                            | 1:N
                            v
+-------------------+     +-------------------+     +-------------------+
|       User        |     |      Product      |     |    OrderItem      |
+-------------------+     +-------------------+     +-------------------+
| id (PK, UUID)     |     | id (PK, UUID)     |     | id (PK, UUID)     |
| email (EmailField)|     | category_id (FK)  |--N:1| order_id (FK)     |
| password (VarChar)|     | title (VarChar)   |     | product_id (FK)   |--N:1 (to Product)
| role (VarChar)    | 1:N | description (Text)|     | quantity (Integer)|
+-------------------+     | price (Decimal)   |     | price_at_purchase |
          |               | stock (Integer)   |     +-------------------+
          |               | image_url (URL)   |               ^
          | 1:N           +-------------------+               |
          v                                                   | 1:N
+-------------------+                                         |
|       Order       |                                         |
+-------------------+                                         |
| id (PK, UUID)     |                                         |
| user_id (FK)      |-----------------------------------------+
| total_amount (Dec)|
| province (VarChar)|
| city (VarChar)    |
| payment_status (S)|
| idempotency_key   |
+-------------------+
```

---

## 4. CRITICAL DATA FLOW & TRANSITION LOGIC

### 4.1 Race-Condition Proof Stock Reduction Sequence
To prevent double-selling products during flash sales triggered by Instagram promotions, the system skips standard loose reads and implements explicit **Pessimistic Row-Level Locking** (`select_for_update`) within an isolated ACID atomic database block.

```
[Customer Checkout Submit] 
            |
            v
   Start Atomic Block (transaction.atomic())
            |
            v
   Lock Row: Product.objects.select_for_update().get(id=product_id)
            |
    +-------+-------+
    |               |
[Stock >= Qty?]  [Stock < Qty]
    |               |
    v               v
 Deduct Stock   Raise ValidationError / Rollback Transaction
 Save Product
    |
    v
 Create Order & OrderItem Elements
    |
    v
 Close Block & Release Postgres Row Lock
```

### 4.2 Idempotent Payment & Webhook Integration Flow
To guarantee high partition tolerance, network dropouts must not corrupt financial records. The checkout sequence mandates an asynchronous validation loop:

```
[Vue App]                [Django Backend]             [Payment Gateway]
    |                            |                            |
    |---- 1. Submit Order ------>|                            |
    |     (Idempotency Key)      |                            |
    |                            |-- 2. Verify Key Unique --->|
    |                            |-- 3. Register Transaction ->|
    |<--- 4. Return Pay URL -----|                            |
    |                            |                            |
    |==================== User Completes Payment =============|
    |                            |                            |
    |                            |<--- 5. Signed Webhook -----|
    |                            |     (Payment Success)      |
    |                            |                            |
    |                            |-- 6. Atomic State Update ->|
    |                            |   (Order -> "Paid")        |
    |<--- 7. Order Confirmed ----|                            |
```

In the event that step 5 fails due to an internet drop or timeout, a background worker runs a **Two-Phase Status Verification Fallback** by calling the gateway's status endpoint directly to synchronize internal order structures.

---

## 5. INFRASTRUCTURE & DEPLOYMENT STRATEGY

### 5.1 Cloud Asset Decoupling
* **Compute Run-Time:** The Django container is decoupled from storage, running inside an isolated VM instance behind a reverse-proxy (Nginx) enforcing strictly automated Let's Encrypt TLS 1.3 encryption layers.
* **Object Store Bucket:** All dynamic media uploads processed by the backend are transmitted instantly out to an S3-compatible cloud object bucket (e.g., AWS S3 or Cloudflare R2) managed securely via the `django-storages` abstraction driver. This ensures asset delivery scales independently from system computing limitations.

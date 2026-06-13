# SOFTWARE REQUIREMENTS SPECIFICATION (SRS)
## Project: By Nzuri E-Commerce Automation Platform
**Author:** Technical Architecture Team  
**Tech Stack:** Vue.js 3 (Frontend SPA) + Django REST Framework (Backend API) + PostgreSQL (Database)  
**Target Market:** Zambia (Mobile Money & Localized Logistics Integration)

---

## 1. INTRODUCTION

### 1.1 Purpose
This document specifies the definitive functional, non-functional, and structural requirements for the **By Nzuri** e-commerce platform. The system is engineered to transition operations from manual Instagram direct message (DM) and WhatsApp sales coordination into a fully automated, scalable, secure, and highly consistent web application. 

### 1.2 Scope
The system encompasses a headless e-commerce ecosystem consisting of:
1. A highly responsive, mobile-first consumer-facing **Vue.js Single Page Application (SPA)**.
2. A decoupled administrative portal for inventory tracking and fulfillment tracking.
3. A robust **Django REST Framework (DRF)** web API processing business logic, state transitions, and identity management.
4. A persistent **PostgreSQL** relational database.
5. Third-party API integrations for **Zambian Mobile Money/Card networks** (e.g., Paystack, Flutterwave, or DPO Group).

### 1.3 Definitions, Acronyms, and Abbreviations
* **ZMW:** Zambian Kwacha.
* **SPA:** Single Page Application.
* **JWT:** JSON Web Token (consisting of Access and Refresh tokens).
* **DRF:** Django REST Framework.
* **CORS:** Cross-Origin Resource Sharing.
* **ACID:** Atomicity, Consistency, Isolation, Durability.
* **Idempotency:** An operational property where an API call can be made multiple times without changing the result beyond the initial application.

---

## 2. SYSTEM ARCHITECTURE & HIGH-LEVEL DESIGN

The platform strictly adheres to a headless, decoupled architectural pattern. Communication between the user interface and data tier is bound over secure HTTPS channels transmitting structured JSON payloads.

```
                  +-----------------------------------+
                  |          Vue.js 3 Client          |
                  |     (Consumer UI / Admin App)     |
                  +-----------------------------------+
                                    |
                           HTTPS JSON Payloads
                                    v
                  +-----------------------------------+
                  |      Django REST Framework        |
                  |      (Core Engine & Auth)         |
                  +-----------------------------------+
                     |                             |
         SQL Queries |                             | API Webhooks
                     v                             v
+--------------------------+             +--------------------------+
|   PostgreSQL Database    |             |  Zambian Payment Gateway |
|  (ACID Engine / Locks)   |             | (MTN, Airtel, Card APIs) |
+--------------------------+             +--------------------------+
```

---

## 3. FUNCTIONAL REQUIREMENTS

### 3.1 User Management, Identity, & Access Control (Auth)
* **FR-1.1: Registration & Authentication:** Customers must be able to register unique accounts via an email address, phone number, and a cryptographically hashed password (using Django's default PBKDF2 with a SHA256 implementation).
* **FR-1.2: Stateless Session Tokenization:** Upon successful validation of credentials, the backend must issue an asymmetric JWT pair (`access` token expiring in 15 minutes, `refresh` token expiring in 7 days).
* **FR-1.3: Client-Side Token Interception:** The Vue.js application must intercept outgoing API calls via an Axios client wrapper, injecting the active Bearer token into authorization headers. Tokens must be stored securely (HTTP-only cookies or sandboxed browser state) to mitigate Cross-Site Scripting (XSS) extraction risks.
* **FR-1.4: Role-Based Access Control (RBAC):** The system must compute and enforce explicit permission scopes:
  * `Customer`: Authorized to view catalog, modify local carts, trigger checkouts, and view personal historical data.
  * `Staff / Admin`: Authorized to modify system inventory matrices, adjust prices, edit descriptions, upload media assets, and change order shipment states.

### 3.2 Product Catalog & Inventory Engine
* **FR-2.1: Dynamic Catalog Display:** The user interface must serve an interactive gallery displaying product cards. Each card must clearly convey title, price denominated explicitly in **Zambian Kwacha (ZMW)**, product categorization, high-resolution media carousels, and explicit usage directions.
* **FR-2.2: Reactive Search & Filtering:** The system must feature client-side text filtering paired with indexed backend text query optimization, enabling rapid content lookups across distinct criteria (e.g., *Hair Care, Growth Oils, Brushes*).
* **FR-2.3: Deterministic Inventory Tracking:** The backend must decrement physical stock fields dynamically at checkout. If a product's available units hit absolute zero ($0$), the API must instantly return an `out_of_stock` state flag, prompting the Vue UI to disable the "Add to Cart" block and replace it with an explicit "Out of Stock" visual indicator.

### 3.3 Shopping Cart & Localized Checkout Pipeline
* **FR-3.1: State-Persistent Cart:** The application must maintain cart selections across browser reloads. Unauthenticated selections must be stored inside a Pinia store synchronized with local storage. Upon user authentication, the client cart must merge atomized items into a backend relational table.
* **FR-3.2: Zambian Delivery Matrix Routing:** To guarantee reliable delivery processing in the absence of structured regional postal codes, the checkout pipeline must mandate an explicit, hierarchical dropdown navigation component for geographic selection:
  * **Level 1 (Province):** (e.g., Lusaka, Copperbelt, Central, Southern, Eastern, Western, Muchinga, Northern, Luapula, North-Western).
  * **Level 2 (City/Town):** Contextually populated based on Level 1 (e.g., Lusaka, Kitwe, Ndola, Livingstone, Kabwe, Chipata).
* **FR-3.3: Dynamic Logistics Pricing Engine:** Shipping rates must calculate automatically based on the chosen city and specified delivery tiers (e.g., *Same-Day Lusaka Courier, Intercity Courier Bus Freight, Showroom Pick-Up Hub*).

### 3.4 Transaction Verification & Payment Webhooks
* **FR-4.1: Mobile Money Aggregator Pipelines:** The platform must hook directly into a verified local payment handler (e.g., Paystack, Flutterwave, or DPO Group) capable of dispatching local push notifications for Mobile Money processing (MTN MoMo, Airtel Money) alongside global settlement networks (Visa, Mastercard).
* **FR-4.2: Idempotent Payment Checks:** To survive network dropouts without double-billing mobile wallets, every order initialization must generate a unique `idempotency_key` (derived via a deterministic hash of User ID, timestamp, and Cart footprint). Django must reject processing attempts on any key already flagged as `Pending` or `Success`.
* **FR-4.3: Asynchronous Webhook Resolution:** The API must declare a dedicated webhook URL endpoint to receive cryptographically signed transaction reports from the payment aggregator. Receipt of a verified success signal must atomically update order objects from `Awaiting Payment` to `Paid`.
* **FR-4.4: Two-Phase Status Verification Fallback:** In the event of a network partition blocking the incoming webhook, the client request or cron task must trigger a direct server-to-server validation query (`/verify/transaction/{reference}`) against the payment aggregator API before processing shipment pipelines.

### 3.5 Business Intelligence & Admin Dashboard
* **FR-5.1: Content Editing UI:** Authenticated administrators must be provided with a protected, clean dashboard interface to create, read, update, or safely archive products, adjust pricing tiers, and attach creative product imagery.
* **FR-5.2: Order Pipeline Tracker:** Admins must be served a unified order processing interface partitioned explicitly by operational state milestones: `Awaiting Payment` -> `Paid / Processing` -> `Dispatched via Courier` -> `Fulfilled & Completed`.

---

## 4. NON-FUNCTIONAL REQUIREMENTS

### 4.1 Performance & Mobile Optimization
* **NFR-1.1: Mobile-First Core Web Vitals:** Since more than 80% of inbound sales pipelines route through Instagram’s internal in-app mobile browser, layouts must pass rigid responsive checks. The interface must sustain a Cumulative Layout Shift (CLS) score under $0.1$ and a First Contentful Paint (FCP) benchmark under $1.5$ seconds.
* **NFR-1.2: Backend Image Pipeline Optimization:** The server must explicitly intercept and optimize raw image uploads. The Django tier must use image manipulation engines (e.g., `Pillow`) to compress, scale, and format file blocks into lightweight next-gen formats (`.webp`) prior to permanent cloud storage.
* **NFR-1.3: API Latency SLA:** Read operations for product catalogs must resolve in less than $300	ext{ms}$ under normal system loads via optimized database indices and serialization layers.

### 4.2 Security Architecture
* **NFR-2.1: Mandatory Transport Encryption:** All data layers in transit between browser clients, backend APIs, and financial nodes must operate strictly under enforced TLS 1.3 (HTTPS) protocols.
* **NFR-2.2: CORS Whitelisting Protection:** The Django `django-cors-headers` middleware must be locked down to strictly block and discard requests originating from unverified or hostile foreign domains, permitting input solely from the assigned production frontend domain.
* **NFR-2.3: Pessimistic Concurrency Handling:** Database write requests altering active product configurations or executing order decrementing blocks must invoke strict PostgreSQL row-level locks via Django’s `.select_for_update()` mechanism. This ensures absolute sequential transactional consistency during high-volume flash sales.

### 4.3 Cloud Infrastructure & Media Assets
* **NFR-3.1: Decoupled Media Assets:** The production hosting layer must keep file storage completely separate from computational application runtimes. All static UI stylesheets, scripts, and product media blocks must be served through independent cloud bucket infrastructure (e.g., AWS S3 or Cloudflare R2) tied into Django via the `django-storages` driver framework.

---

## 5. DATABASE SCHEMA BLUEPRINT (ENTITY-RELATIONSHIP MODEL)

The data tier uses a strongly-typed relational model to guarantee strict cross-table data integrity.

```
+-------------------+       +-------------------+       +-------------------+
|     Category      |       |      Product      |       |    OrderItems     |
+-------------------+       +-------------------+       +-------------------+
| id (PK)           |       | id (PK)           |       | id (PK)           |
| name (VarChar)    | ----< | category_id (FK)  | ----< | order_id (FK)     |
| slug (SlugField)  |       | title (VarChar)   |       | product_id (FK)   |
+-------------------+       | description (Text)|       | quantity (Int)    |
                            | price (Decimal)   |       | price_at_purchase |
                            | stock (Integer)   |       +-------------------+
                            | image (URL/Str)   |                 ^
                            +-------------------+                 |
                                                                  |
+-------------------+       +-------------------+                 |
|       User        |       |       Order       |                 |
+-------------------+       +-------------------+                 |
| id (PK)           |       | id (PK)           |                 |
| email (EmailField)| ----< | user_id (FK)      | ----------------+
| password (VarChar)|       | total_amount (Dec)|
| role (VarChar)    |       | delivery_addr(Txt)|
+-------------------+       | payment_status(St)|
                            | reference_code(Str|
                            +-------------------+
```

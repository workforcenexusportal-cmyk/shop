# ATELIER — Clothing E-Commerce Platform

A full-stack clothing e-commerce website built with Flask.

## Features

1. **Product Catalog & Categorization**: Browse catalog across multiple categories (Men's Tops, Men's Bottoms, Women's Tops, Women's Bottoms, Outerwear, Accessories, Footwear) with filtering by price, size, color, and category, plus full-text search and sorting.
2. **Detailed Product Pages**: High-resolution image galleries, interactive size and color pickers, real-time stock availability badges, and customer reviews.
3. **Interactive Shopping Cart & Checkout**: Add/update/remove items with size/color options, persistent session or database-backed cart, subtotal, tax, and shipping calculations.
4. **Secure Stripe Payment Integration**: Seamless checkout processing using Stripe PaymentIntents and Checkout Sessions, complete with asynchronous webhook event handling (`checkout.session.completed`, `payment_intent.succeeded`).
5. **User Authentication & Management**: Registration, secure password hashing (Werkzeug/Bcrypt), session management (Flask-Login / JWT), profile management, and saved shipping addresses.
6. **Customer Order History**: Detailed view of past orders, order status tracking (Pending, Processing, Shipped, Completed, Cancelled), and order summary receipts.
7. **Product Reviews & Ratings**: Authenticated customers can rate products on a 1–5 star scale and post detailed reviews; view average product ratings.
8. **Inventory & Stock Management**: Real-time stock decrementing upon order completion, low-stock warnings (<5 remaining), and out-of-stock badges (0 remaining).
9. **Admin Dashboard**: Full administrative interface to create, edit, and archive products, update category hierarchies, manage customer orders and statuses, and monitor inventory levels.
10. **Responsive & Modern UI**: Built with a mobile-first responsive layout, elegant Tailwind CSS / Bootstrap components, interactive modals, slide-over cart drawers, and clean design aesthetics.

## Tech Stack

- **Backend**: Python 3.10+, Flask 3.x, Flask-SQLAlchemy (ORM), Flask-Migrate (Alembic), Flask-Login / PyJWT
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Frontend**: HTML5, Jinja2 Templates, Tailwind CSS / Bootstrap 5, JavaScript (ES6+), Alpine.js / Vanilla JS
- **Payment Processing**: Stripe API (Stripe Checkout & Webhooks)
- **Deployment & Production**: PythonAnywhere (uWSGI, free HTTPS), Gunicorn for self-hosting, Docker (optional)

## Project Structure

```
shop/                          # repo root
├── app/
│   ├── __init__.py           # App factory (create_app)
│   ├── config.py             # Configuration classes (Dev, Prod, Test)
│   ├── extensions.py         # Extension instances (db, login_manager, csrf, mail, migrate)
│   ├── models/               # SQLAlchemy Models
│   │   ├── __init__.py
│   │   ├── user.py           # User & Wishlist models
│   │   ├── product.py        # Category, Product, Review models
│   │   ├── cart.py           # Cart & CartItem models
│   │   └── order.py          # Order & OrderItem models
│   ├── routes/               # Route Blueprints
│   │   ├── __init__.py       # register_blueprints(app)
│   │   ├── auth.py           # Auth pages + /api/auth endpoints
│   │   ├── catalog.py        # Home, shop, product detail + /api/products, /api/reviews
│   │   ├── cart.py           # Cart page + /api/cart, /api/wishlist
│   │   ├── orders.py         # Checkout + /api/checkout, /api/orders, Stripe webhook
│   │   └── admin.py          # Admin dashboard + /api/admin endpoints
│   ├── forms/                # Flask-WTF Forms
│   │   ├── login.py          # LoginForm
│   │   ├── register.py       # RegistrationForm
│   │   └── checkout.py       # CheckoutForm
│   ├── utils/
│   │   └── helpers.py        # Cart helpers, serializers
│   ├── static/               # Static assets (mapped in PythonAnywhere Web tab)
│   │   ├── css/style.css
│   │   ├── js/               # main.js, cart.js, product.js
│   │   └── images/products/  # Product images (.gitkeep)
│   └── templates/            # Jinja2 Templates (all extend base.html)
│       ├── base.html         # Layout: navbar, footer, toasts, CSRF meta
│       ├── index.html        # Home / hero / featured
│       ├── shop.html         # Listing + filters + pagination
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       ├── login.html / register.html / account.html
│       └── admin_dashboard.html
├── .env.example              # Template environment variables
├── .gitignore                # Git ignore configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Local development entry point
├── seed.py                   # Standalone database seed script
└── README.md                 # Setup and documentation
``````

## Prerequisites

- Python 3.10+
- pip (Python package installer)
- SQLite (for local development) or PostgreSQL (for production)
- Stripe account (for processing payments and webhook testing)

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/workforcenexusportal-cmyk/shop.git
   cd shop
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in configuration values:
   ```bash
   cp .env.example .env
   ```

5. Initialize the Database:
   ```bash
   flask db init     # If first time initializing migrations
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. Seed sample database records (Categories, Products, Users, Reviews, Sample Order):
   ```bash
   python seed.py
   ```

7. Run the development server:
   ```bash
   python run.py
   ```

8. Open your browser and visit:
   `http://localhost:5000`

## Database Migrations

Database schema changes are managed via Flask-Migrate (Alembic).

- **Create a new migration after model changes:**
  ```bash
  flask db migrate -m "Describe your schema change"
  ```

- **Apply pending migrations to the database:**
  ```bash
  flask db upgrade
  ```

- **Revert the last applied migration:**
  ```bash
  flask db downgrade
  ```

- **Show current migration status:**
  ```bash
  flask db current
  ```

## API Documentation

### Authentication Endpoints

- **`POST /api/auth/register`**
  - **Params / Body**: `{"email": "user@example.com", "password": "password123", "full_name": "John Doe"}`
  - **Response**: `201 Created` — `{"message": "User registered successfully", "user": {"id": 1, "email": "user@example.com", "full_name": "John Doe"}}`

- **`POST /api/auth/login`**
  - **Params / Body**: `{"email": "user@example.com", "password": "password123"}`
  - **Response**: `200 OK` — `{"message": "Login successful", "user": {"id": 1, "email": "user@example.com", "is_admin": false}}`

- **`POST /api/auth/logout`**
  - **Response**: `200 OK` — `{"message": "Logged out successfully"}`

- **`GET /api/auth/me`**
  - **Response**: `200 OK` — `{"user": {"id": 1, "email": "user@example.com", "full_name": "John Doe", "is_admin": false}}`

### Product & Category Endpoints

- **`GET /api/products`**
  - **Query Params**: `category` (slug), `min_price`, `max_price`, `size`, `color`, `sort` (`price_asc`, `price_desc`, `newest`), `q` (search query)
  - **Response**: `200 OK` — `{"products": [{"id": 1, "name": "Classic Oxford Shirt", "price": 69.99, "category_id": 1, "stock": 25, "images": [...]}]}`

- **`GET /api/products/<id>`**
  - **Response**: `200 OK` — `{"product": {"id": 1, "name": "Classic Oxford Shirt", "description": "...", "price": 69.99, "sizes": ["S","M","L"], "colors": ["White","Navy"], "stock": 25, "reviews": [...]}}`

- **`GET /api/categories`**
  - **Response**: `200 OK` — `{"categories": [{"id": 1, "name": "Men's Tops", "slug": "mens-tops"}]}`

- **`POST /api/products/<id>/reviews`** (Auth Required)
  - **Params / Body**: `{"rating": 5, "comment": "Excellent quality!"}`
  - **Response**: `201 Created` — `{"message": "Review added successfully", "review": {"id": 1, "rating": 5, "comment": "..."}}`

### Cart Endpoints

- **`GET /api/cart`**
  - **Response**: `200 OK` — `{"cart": {"items": [{"id": 1, "product_id": 1, "name": "Classic Oxford Shirt", "quantity": 2, "size": "M", "color": "White", "price": 69.99}], "total": 139.98}}`

- **`POST /api/cart/items`**
  - **Params / Body**: `{"product_id": 1, "quantity": 1, "size": "M", "color": "White"}`
  - **Response**: `200 OK` — `{"message": "Item added to cart", "cart_count": 1}`

- **`PUT /api/cart/items/<id>`**
  - **Params / Body**: `{"quantity": 3}`
  - **Response**: `200 OK` — `{"message": "Cart item updated", "total": 209.97}`

- **`DELETE /api/cart/items/<id>`**
  - **Response**: `200 OK` — `{"message": "Item removed from cart"}`

### Order & Checkout Endpoints

- **`POST /api/checkout/create-session`** (Auth Required)
  - **Params / Body**: `{"shipping_address": {"street": "123 Main St", "city": "New York", "state": "NY", "zip": "10001", "country": "USA"}}`
  - **Response**: `200 OK` — `{"checkout_url": "https://checkout.stripe.com/c/pay/cs_test_...", "session_id": "cs_test_..."}`

- **`GET /api/orders`** (Auth Required)
  - **Response**: `200 OK` — `{"orders": [{"id": 1, "total_amount": 279.96, "status": "completed", "created_at": "2026-09-02T15:00:00Z"}]}`

- **`GET /api/orders/<id>`** (Auth Required)
  - **Response**: `200 OK` — `{"order": {"id": 1, "status": "completed", "total_amount": 279.96, "items": [...], "shipping_address": {...}}}`

- **`POST /api/webhook/stripe`**
  - **Headers**: `Stripe-Signature: t=...,v1=...`
  - **Response**: `200 OK` — `{"status": "success"}`

### Admin Endpoints (Admin Auth Required)

- **`POST /api/admin/products`**
  - **Params / Body**: `{"name": "New Jacket", "description": "...", "price": 199.99, "category_id": 5, "stock": 10, "images": [...], "sizes": [...], "colors": [...]}`
  - **Response**: `201 Created` — `{"message": "Product created", "product": {...}}`

- **`PUT /api/admin/products/<id>`**
  - **Params / Body**: `{"price": 179.99, "stock": 15}`
  - **Response**: `200 OK` — `{"message": "Product updated"}`

- **`DELETE /api/admin/products/<id>`**
  - **Response**: `200 OK` — `{"message": "Product deleted"}`

- **`GET /api/admin/orders`**
  - **Response**: `200 OK` — `{"orders": [...]}`

- **`PUT /api/admin/orders/<id>/status`**
  - **Params / Body**: `{"status": "shipped"}`
  - **Response**: `200 OK` — `{"message": "Order status updated to shipped"}`

## Admin Access

Initial admin credentials created by `python seed.py`:

- **Email**: `admin@atelier.com`
- **Password**: `adminpass123`

## Deployment on PythonAnywhere

PythonAnywhere is the recommended host for this project — it supports Flask out of the box,
handles HTTPS automatically, and has a free tier that works for development/staging.

### 1. Pull the code into your account

Open a **Bash console** on PythonAnywhere and clone the repo:

```bash
git clone https://github.com/workforcenexusportal-cmyk/shop.git ~/shop
cd ~/shop
```

(If you already cloned it before, just `cd ~/shop && git pull` to get updates.)

### 2. Create a virtualenv and install dependencies

Still in the Bash console:

```bash
mkvirtualenv atelier --python=python3.10
pip install -r ~/shop/requirements.txt
```

> Note: `gunicorn` is in requirements.txt but is not needed on PythonAnywhere —
> the platform serves WSGI apps with uWSGI itself. It does no harm to keep it installed.

### 3. Set up environment variables

PythonAnywhere consoles don't load `.env` automatically for the web app, so set
the variables inside the WSGI file (step 5) instead, or keep a `.env` in `~/shop`
for console work:

```bash
cp ~/shop/.env.example ~/shop/.env
nano ~/shop/.env   # fill in SECRET_KEY, Stripe keys, mail settings
```

### 4. Initialize the database

```bash
cd ~/shop
flask db init          # only if the migrations/ folder doesn't exist yet
flask db migrate -m "Initial migration"
flask db upgrade
python seed.py         # loads categories, 28 products, users, reviews
```

SQLite is fine on PythonAnywhere — the database will live at `~/shop/instance/shop.db`.
(The `instance/` folder is already in `.gitignore`.)

### 5. Configure the Web app

In the PythonAnywhere **Web** tab:

1. **Add a new web app** → choose your domain (e.g. `yourusername.pythonanywhere.com`)
   → **Manual configuration** → pick **Python 3.10** (do NOT choose the "Flask" wizard —
   we want manual control).

2. **Code section → WSGI file**: click the WSGI file link and replace its contents with:

   ```python
   import os
   import sys

   # Add the project root to the path
   path = '/home/YOURUSERNAME/shop'
   if path not in sys.path:
       sys.path.insert(0, path)

   # Environment variables (or set these in the PythonAnywhere "Environment variables" section)
   os.environ['FLASK_CONFIG'] = 'production'
   os.environ['SECRET_KEY'] = 'your-strong-production-secret-key'
   # os.environ['STRIPE_SECRET_KEY'] = 'sk_live_...'
   # os.environ['STRIPE_PUBLISHABLE_KEY'] = 'pk_live_...'
   # os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
   # ... remaining keys from .env.example

   from app import create_app
   application = create_app()
   ```

   Replace `YOURUSERNAME` with your PythonAnywhere username, then save.

3. **Virtualenv section**: set the path to your virtualenv, e.g.
   `/home/YOURUSERNAME/.virtualenvs/atelier`

4. **Static files section**: add this mapping so `/static/` is served directly by
   PythonAnywhere's web servers (much faster than going through Flask):

   | URL | Directory |
   |---|---|
   | `/static/` | `/home/YOURUSERNAME/shop/app/static/` |

5. **Reload**: click the green **Reload** button, then visit
   `https://yourusername.pythonanywhere.com`.

### 6. Updating after code changes

Whenever you push new commits to GitHub:

```bash
cd ~/shop
git pull
flask db upgrade        # if there are new migrations
```

Then hit **Reload** in the Web tab.

### 7. Stripe webhooks in production

Point your Stripe webhook endpoint at your live PythonAnywhere URL:

```
https://yourusername.pythonanywhere.com/api/stripe/webhook
```

Add the webhook signing secret (`whsec_...`) to your environment variables, then reload.
HTTPS is provisioned automatically by PythonAnywhere — no certificate setup needed.

### Troubleshooting tips

- **Error log**: Web tab → **Error log** link (e.g. `/var/log/yourusername.pythonanywhere.com.error.log`)
  — this is the first place to look if the app shows a 500.
- **ModuleNotFoundError**: your virtualenv isn't selected in the Web tab, or the WSGI
  file's `path` doesn't point at `~/shop`.
- **Static files 404**: check the static files mapping table — URL must be `/static/`
  and the directory must end with `/app/static/`.

## Stripe Configuration

1. Log in to your [Stripe Dashboard](https://dashboard.stripe.com/).
2. Navigate to **Developers API keys** to retrieve your `Publishable key` (`pk_test_...`) and `Secret key` (`sk_test_...`).
3. Add these keys to your `.env` file:
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```
4. For local testing of Stripe Webhooks:
   - Download the [Stripe CLI](https://stripe.com/docs/stripe-cli).
   - Authenticate with `stripe login`.
   - Forward webhooks to your local Flask app:
     ```bash
     stripe listen --forward-to localhost:5000/api/webhook/stripe
     ```
   - Copy the outputted Webhook signing secret (`whsec_...`) into your `.env`:
     ```env
     STRIPE_WEBHOOK_SECRET=whsec_...
     ```

## License

MIT License. See `LICENSE` for details.

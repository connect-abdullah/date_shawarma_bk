# Date Shawarma Backend

FastAPI backend with the same structure as WhenWeWork_bk. Uses PostgreSQL, SQLAlchemy, Alembic, and JWT auth.

## Tables

- **users** – name, email, password, phone_no, address, user_role (ADMIN | CUSTOMER)
- **categories** – category_name, picture
- **products** – name, description, category_id, price, photo, is_featured, is_trending, is_available
- **orders** – customer_id, order_status, order_date, total_price
- **order_items** – order_id, product_id, quantity, unit_price
- **reviews** – product_id, user_id, rating, comment, is_approved (by ADMIN)
- **complaint_boxes** – user_name, user_email, phone, comment

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials (database URL, optional SMTP/Supabase).

### Supabase `DATABASE_URL` (fix "Tenant or user not found")

- In **Supabase Dashboard** → your project → **Project Settings** (gear) → **Database**.
- Under **Connection string**, choose **URI**.
- Use the **Transaction** pooler string (recommended for migrations) or the **Direct** connection (port **5432**). Session pooler can sometimes cause this error for migrations.
- The username **must** be `postgres.[PROJECT-REF]` (e.g. if your project URL is `https://abcdefgh.supabase.co`, use `postgres.abcdefgh`). Do not use plain `postgres`.
- Replace `[YOUR-PASSWORD]` with your database password (the one you set when creating the project).
- Example:
  ```env
  DATABASE_URL=postgresql://postgres.abcdefgh:YOUR_PASSWORD@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
  ```
- **If pooler still gives "Tenant or user not found"**, switch to **Direct** connection. In Dashboard → Project Settings → Database, copy the **Direct** URI, or use this format (username is plain `postgres`, host `db.[PROJECT-REF].supabase.co`, port **5432**):
  ```env
  DATABASE_URL=postgresql://postgres:YOUR_DATABASE_PASSWORD@db.PROJECT_REF.supabase.co:5432/postgres
  ```
  Replace `PROJECT_REF` with your project ref (e.g. from `https://qkdhmygnklvagghjbnkd.supabase.co` → `qkdhmygnklvagghjbnkd`). Then restart containers and run migrations again.

2. Create a virtualenv and install deps:
   ```bash
   poetry install
   ```
3. Run migrations:
   ```bash
   poetry run alembic upgrade head
   ```
4. Start the server:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

API base: `http://localhost:8000`, docs: `http://localhost:8000/docs`.

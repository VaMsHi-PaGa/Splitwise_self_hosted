# SplitSmart India

A production-ready expense sharing application tailored for Indian users. Built with FastAPI, Next.js, PostgreSQL, and Docker.

## Features

- **User Management**: JWT-based authentication with secure password hashing
- **Groups**: Create groups (trips, flatmates, family, office teams)
- **Expenses**: Add expenses with multiple split types:
  - Equal split
  - Exact amounts
  - Percentage-based
- **Smart Settlement**: Minimize transactions using debt simplification algorithm
- **Indian Features**:
  - INR currency formatting
  - India-themed categories (groceries, rent, electricity, WiFi, maid, cook, petrol, etc.)
  - UPI payment references
- **Additional Features**:
  - Bill image upload
  - Dark mode
  - CSV export
  - Recurring expenses

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Running the Application

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Splitwise_self_hosted
   ```

2. **Start the application**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Demo Credentials

The application comes with pre-seeded demo data:

| Email | Password | Notes |
|-------|----------|-------|
| `test@test.com` | `test123` | Quick test login |
| `aarav@example.com` | `password123` | Has sample expenses |
| `priya@example.com` | `password123` | Has sample expenses |

All three users are members of the **Flatmates** group with pre-populated expenses (₹1200 groceries, ₹2400 electricity bill).

### Creating Additional Users

**Via the UI**: Go to `/register` and fill out the form.

**Via CLI** (after `docker compose up`):
```bash
docker compose exec backend python create_user.py myemail@example.com mypassword "My Name"
```

**Via API**:
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name": "My Name", "email": "me@example.com", "password": "secret123"}'
```

## Architecture

### Backend (FastAPI)

- **Framework**: FastAPI with Uvicorn
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt hashing
- **Migrations**: Alembic for database schema versioning
- **Scheduling**: APScheduler for recurring expense tasks

**Key Endpoints**:
- POST `/auth/register` - User registration
- POST `/auth/login` - User login
- GET `/groups` - List user's groups
- POST `/groups` - Create group
- POST `/expenses` - Add expense
- GET `/balances` - Dashboard balances
- GET `/groups/{id}/simplify` - Debt simplification
- POST `/settle` - Record settlement

### Frontend (Next.js)

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State**: Jotai for state management
- **Theme**: next-themes for dark mode

**Key Pages**:
- `/login` - User login
- `/register` - User registration
- `/dashboard` - Balance overview
- `/groups` - List and create groups
- `/groups/[id]` - Group detail with expenses
- `/settings` - User profile

### Database Schema

**Users**
- id, name, email (unique), phone, upi_id, password_hash, created_at

**Groups**
- id, name, category, created_by, created_at
- GroupMembers: composite key on (group_id, user_id)

**Expenses**
- id, group_id, description, amount, category, split_type, created_by, bill_path, created_at
- ExpensePayers: (expense_id, user_id, amount_paid)
- ExpenseSplits: (expense_id, user_id, share_amount, share_percent)

**Settlements**
- id, group_id, from_user_id, to_user_id, amount, method, settled_at

**RecurringExpenses**
- id, group_id, description, amount, category, split_config (JSON), frequency, day_of_month, next_run_at, active

## API Examples

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "password": "password123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "password123"
  }'
```

### Create Group
```bash
curl -X POST http://localhost:8000/groups \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "Flatmates",
    "category": "flatmates",
    "member_emails": ["friend@example.com"]
  }'
```

### Add Expense
```bash
curl -X POST http://localhost:8000/expenses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "group_id": "group-uuid",
    "description": "Groceries",
    "amount": 1200,
    "category": "groceries",
    "split_type": "equal",
    "payers": [{"user_id": "user-uuid", "amount_paid": 1200}],
    "splits": [
      {"user_id": "user1-uuid"},
      {"user_id": "user2-uuid"}
    ]
  }'
```

## Configuration

Environment variables can be set in `docker-compose.yml`:

- `JWT_SECRET`: Secret key for JWT tokens (change in production)
- `JWT_EXPIRE_MINUTES`: Token expiry time (default: 1440 = 24 hours)
- `SEED_DEMO`: Set to false to skip demo data seeding
- `NEXT_PUBLIC_API_URL`: Backend API URL for frontend

## Development

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Production Deployment

### Architecture for Netlify Hosting

Netlify only hosts the **frontend** (Next.js). The backend (FastAPI + PostgreSQL) needs a separate host. Recommended setup:

| Component | Host | Cost |
|-----------|------|------|
| Frontend (Next.js) | **Netlify** | Free |
| Backend (FastAPI) | **Render** / Railway / Fly.io | Free tier |
| Database (PostgreSQL) | **Neon** / Supabase / Render | Free tier |
| Bill uploads | Render disk / S3 / Cloudinary | Free tier |

---

### Step 1: Deploy Backend (Render — Recommended)

The repo includes `render.yaml` for one-click deployment.

1. Push this repo to GitHub
2. Go to https://render.com → "New" → "Blueprint"
3. Connect your GitHub repo, select this project
4. Render auto-detects `render.yaml` and creates:
   - Web service `splitsmart-backend` (FastAPI in Docker)
   - PostgreSQL database `splitsmart-db`
5. After deploy, note your backend URL (e.g. `https://splitsmart-backend.onrender.com`)
6. In Render dashboard, update `CORS_ORIGINS` env var to your Netlify URL

**Manual Render setup (alternative)**:
- New → Web Service → Connect repo
- Root directory: `backend`
- Runtime: Docker
- Add env vars: `DATABASE_URL`, `JWT_SECRET` (random 64-char string), `SEED_DEMO=false`, `CORS_ORIGINS=https://your-app.netlify.app`
- Add a PostgreSQL database, copy connection string to `DATABASE_URL`

**Alternative hosts**:
- **Railway**: `railway up` from `backend/` directory
- **Fly.io**: `fly launch` from `backend/`, add Postgres with `fly postgres create`

---

### Step 2: Deploy Frontend to Netlify

The repo includes `netlify.toml` with Next.js plugin pre-configured.

#### Option A — Netlify UI (Easiest)

1. Push repo to GitHub
2. Go to https://app.netlify.com → "Add new site" → "Import an existing project"
3. Connect your GitHub repo
4. Netlify auto-detects `netlify.toml`. Confirm:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
5. **Environment variables** (Site settings → Environment variables):
   ```
   NEXT_PUBLIC_API_URL = https://splitsmart-backend.onrender.com
   ```
6. Click "Deploy site"

#### Option B — Netlify CLI

```bash
npm install -g netlify-cli
cd frontend
netlify init
netlify env:set NEXT_PUBLIC_API_URL https://splitsmart-backend.onrender.com
netlify deploy --prod
```

---

### Step 3: Connect Frontend ↔ Backend

After both are deployed:

1. Note your Netlify URL (e.g. `https://splitsmart-app.netlify.app`)
2. Update backend CORS in Render dashboard:
   - `CORS_ORIGINS` → `https://splitsmart-app.netlify.app`
3. Restart backend service
4. Visit your Netlify URL — login with seeded users or register new ones

---

### Required Environment Variables Summary

**Backend (Render / Railway / Fly.io):**
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
JWT_SECRET=<generate-strong-random-64-char-string>
JWT_EXPIRE_MINUTES=1440
SEED_DEMO=false
CORS_ORIGINS=https://your-app.netlify.app
```

**Frontend (Netlify):**
```
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

### Self-Hosting Locally (Docker)

For full local stack (no Netlify):
```bash
docker-compose up --build
```

## Troubleshooting

### Database connection error
- Ensure PostgreSQL is running and healthy: `docker-compose logs db`
- Check `DATABASE_URL` environment variable

### API not accessible
- Check if backend container is running: `docker-compose ps`
- View backend logs: `docker-compose logs backend`

### Frontend can't reach API
- Verify `NEXT_PUBLIC_API_URL` environment variable
- Check CORS settings in `backend/app/main.py`

## Support

For issues and questions, please refer to the API documentation at http://localhost:8000/docs

## License

MIT License - See LICENSE file for details

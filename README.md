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

- **User 1**: aarav@example.com / password123
- **User 2**: priya@example.com / password123
- **Group**: Flatmates (with sample expenses)

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

1. Change `JWT_SECRET` to a strong random value
2. Update database connection string for production database
3. Set `SEED_DEMO=false` to prevent demo data in production
4. Enable HTTPS and CORS restrictions
5. Use environment-specific `.env` files

Example:
```bash
docker-compose -f docker-compose.prod.yml up -d
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

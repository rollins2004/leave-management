# Leave Management System

A full-stack web app where employees apply for leave and employers approve or reject requests.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue.js 3, Tailwind CSS, Vite, Axios |
| Backend | Django REST Framework (Python) |
| Database | **MongoDB Atlas** (via pymongo) |
| Auth | Custom JWT (PyJWT + bcrypt) |

> **Architecture note:** Django is used only for its REST framework and middleware.
> All application data (users, leaves) is stored directly in **MongoDB Atlas** using `pymongo`.
> This approach is fully compatible with Python 3.13+.

---

## Project Structure

```
leave_management_project/
├── backend/
│   ├── leave_management/       # Django project config
│   │   ├── settings.py         # SQLite for Django internals only
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                    # Main application
│   │   ├── db_mongo.py         # pymongo connection to MongoDB Atlas
│   │   ├── auth.py             # JWT creation, validation, MongoUser class
│   │   ├── views.py            # All API logic using pymongo
│   │   ├── urls.py             # URL routing
│   │   └── models.py           # (minimal, ORM not used)
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── Login.vue
    │   │   ├── Register.vue
    │   │   ├── EmployeeDashboard.vue
    │   │   └── EmployerDashboard.vue
    │   ├── router/index.js     # Vue Router with navigation guards
    │   ├── services/api.js     # Axios instance with JWT interceptors
    │   ├── App.vue
    │   └── main.js
    ├── vite.config.js          # Proxies /api to Django
    ├── tailwind.config.js
    └── package.json
```

---

## Local Setup

### Prerequisites
- Python 3.9+ (including 3.13)
- Node.js 16+
- A free MongoDB Atlas account at https://cloud.mongodb.com

### Step 1 — Get your MongoDB Atlas URI
1. Sign up at cloud.mongodb.com (free)
2. Create a cluster → Connect → Drivers → copy the URI
3. It looks like: `mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/`

### Step 2 — Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env       # Windows
cp .env.example .env         # Mac/Linux
```

Edit `.env` with your values:
```
DJANGO_SECRET_KEY=any-long-random-string-here
DEBUG=True
MONGODB_URI=mongodb+srv://youruser:yourpass@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=leave_management
```

```bash
# Run migrations (only for Django internals, not MongoDB)
python manage.py migrate

# Start server
python manage.py runserver
```

✅ Backend at `http://127.0.0.1:8000`

### Step 3 — Frontend

```bash
cd frontend
npm install
npm run dev
```

✅ Frontend at `http://localhost:8080`

---

## API Endpoints

### Public

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register (role: employee or employer) |
| POST | `/api/auth/login/` | Login → returns JWT tokens |
| POST | `/api/auth/refresh/` | Refresh access token |

**Register body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secret123",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee"
}
```

**Login response:**
```json
{
  "access": "<jwt_token>",
  "refresh": "<refresh_token>",
  "user": { "id": "...", "username": "johndoe", "role": "employee" }
}
```

### Employee (JWT required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leaves/` | View own leave requests |
| POST | `/api/leaves/` | Apply for leave |

**Apply body:**
```json
{
  "leave_type": "sick",
  "start_date": "2025-03-15",
  "end_date": "2025-03-16",
  "reason": "Fever"
}
```

### Employer (JWT + employer role required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employer/leaves/` | View all leave requests |
| GET | `/api/employer/leaves/?status=pending` | Filter by status |
| PATCH | `/api/employer/leaves/<id>/` | Approve or reject |

**Approve:** `{ "status": "approved" }`

**Reject:** `{ "status": "rejected", "comments": "Team coverage needed" }`

---

## Features

- **Role-based access control** — employees cannot access employer endpoints (403 Forbidden)
- **JWT authentication** — access token (1 day) + refresh token (7 days), auto-refreshed on expiry
- **MongoDB Atlas** — all users and leaves stored in cloud NoSQL database
- **Input validation** — required fields, date logic, password length checked both frontend and backend
- **Navigation guards** — Vue Router blocks unauthenticated access and role mismatches

---

## Deployment

### Backend on Render (free)
1. Push to GitHub
2. Create Web Service on render.com → connect repo
3. Set environment variables (DJANGO_SECRET_KEY, MONGODB_URI, DB_NAME, DEBUG=False)
4. Build command: `pip install -r requirements.txt`
5. Start command: `gunicorn leave_management.wsgi` (add `gunicorn` to requirements.txt)

### Frontend on Vercel (free)
1. Push frontend folder to GitHub
2. Import on vercel.com
3. Set `VITE_API_URL=https://your-backend.onrender.com/api`
4. Build: `npm run build`, Output: `dist`

# Project Pulse AI

AI-driven engineering metrics dashboard.

## Quick Start

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Start services:
```bash
docker compose up --build -d
```

3. Run migrations:
```bash
docker compose exec backend alembic upgrade head
```

4. Seed database:
```bash
docker compose exec backend python scripts/seed.py
```

5. Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- Login: admin@pulse.ai / password

## Architecture

- Frontend: Next.js 14 (App Router) + TypeScript + Tailwind
- Backend: FastAPI + PostgreSQL + Redis + RQ Worker
- Auth: JWT with RBAC (ADMIN/ANALYST/READER)

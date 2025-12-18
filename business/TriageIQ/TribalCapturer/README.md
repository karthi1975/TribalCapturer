# Tribal Knowledge Capture Portal

A web application for Medical Assistants (MAs) to capture and share tribal knowledge about clinic operations, with a dedicated interface for Creators to view, search, and filter entries.

## 🎯 Purpose

This portal enables healthcare organizations to:
- **Capture** tribal knowledge from Medical Assistants
- **Organize** knowledge by facility and specialty service
- **Search** and retrieve knowledge efficiently
- **Preserve** institutional knowledge for training and operations

## ✨ Features

### For Medical Assistants (MA)
- Submit tribal knowledge entries with facility, specialty, and detailed descriptions
- Save drafts or publish entries
- View all your submitted entries
- Edit and delete your own entries

### For Creators (Admins)
- View all published tribal knowledge entries
- Filter by facility and specialty service
- Full-text search across all knowledge descriptions
- View detailed entry information

## 🚀 Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15+ with full-text search
- SQLAlchemy 2.0 (async)
- JWT authentication
- Alembic migrations

**Frontend:**
- React 18 with TypeScript
- Material-UI 5.14+ (Material Design 3)
- React Router 6
- Axios
- Vite

## 📋 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL)

### 1. Setup

```bash
# Clone and navigate to project
cd /path/to/TribalCapturer

# Start PostgreSQL
docker-compose up -d postgres

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set a strong JWT_SECRET

# Run migrations and seed data
alembic upgrade head
python -m src.database.seed

# Frontend setup (new terminal)
cd ../frontend
npm install
cp .env.example .env.local
```

### 2. Run

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn src.api.main:app --reload --port 8777

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 3. Access

- **Frontend**: http://localhost:5777
- **API Docs**: http://localhost:8777/docs

### 4. Login

```
MA User:
  Email: ma1@tribaliq.com
  Password: TestPassword123!

Creator User:
  Email: creator1@tribaliq.com
  Password: TestPassword123!
```

## 📁 Project Structure

```
TribalCapturer/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API routes and schemas
│   │   ├── database/       # Models and migrations
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── config.py       # Configuration
│   └── requirements.txt
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # Material-UI components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context
│   │   ├── services/      # API client
│   │   └── theme/         # Material Design theme
│   └── package.json
│
└── docker-compose.yml     # PostgreSQL service
```

## 📚 Documentation

- **Implementation Guide**: [`IMPLEMENTATION_GUIDE.md`](./IMPLEMENTATION_GUIDE.md)
- **Implementation Summary**: [`IMPLEMENTATION_SUMMARY.md`](./IMPLEMENTATION_SUMMARY.md)
- **Specification**: [`/specs/001-knowledge-portal/spec.md`](/Users/karthi/specs/001-knowledge-portal/spec.md)
- **API Documentation**: http://localhost:8777/docs (when running)

## 🔐 Security

- JWT authentication with HTTPOnly cookies
- Password hashing with bcrypt
- Role-based access control (MA and Creator roles)
- Input validation on frontend and backend
- Audit logging for compliance

## 🚢 Deployment

Ready to deploy to Railway:
1. Connect Railway to your GitHub repository
2. Configure backend and frontend services
3. Add PostgreSQL database
4. Set environment variables
5. Deploy!

See [`IMPLEMENTATION_GUIDE.md`](./IMPLEMENTATION_GUIDE.md) for detailed deployment instructions.

## 📝 License

Proprietary - TribalIQ

## 🤝 Contributing

This is an internal project. For questions or issues, contact the development team.

---

**Status**: ✅ Implemented and ready for testing
**Last Updated**: December 17, 2025

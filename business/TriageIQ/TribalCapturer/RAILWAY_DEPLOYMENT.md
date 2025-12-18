# Railway Deployment Guide - Tribal Knowledge Capture Portal

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected (already done: https://github.com/karthi1975/TribalCapturer)
- OpenAI API key for semantic search

---

## Step 1: Create New Railway Project

1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose: `karthi1975/TribalCapturer`
5. Railway will auto-detect the project

---

## Step 2: Add PostgreSQL Database

1. In your Railway project, click **"+ New"**
2. Select **"Database" → "PostgreSQL"**
3. Railway will provision a PostgreSQL database
4. **Copy the connection string** (we'll use this in environment variables)

**Note the following from PostgreSQL service**:
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`
- `PGDATABASE`

---

## Step 3: Configure Backend Environment Variables

In your Railway **backend service**, add these environment variables:

### Required Variables

```bash
# Database (use values from Railway PostgreSQL service)
DATABASE_URL=postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}

# JWT Authentication
JWT_SECRET=your-production-secret-min-32-characters-change-this-to-random-value
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend-domain.railway.app","https://tribalcapturer.railway.app"]

# Logging
LOG_LEVEL=INFO

# OpenAI API (for semantic search)
OPENAI_API_KEY=sk-proj-your-openai-api-key-here
```

### Important Notes:

1. **DATABASE_URL**: Railway automatically injects PostgreSQL variables
   - Use: `postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}`
   - Railway will auto-populate `Postgres.*` values

2. **JWT_SECRET**: Generate a strong random secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **CORS_ORIGINS**: Update with your actual Railway frontend URL
   - Format: `["https://your-frontend.railway.app"]`
   - Must be a JSON array

4. **OPENAI_API_KEY**: Your actual OpenAI API key
   - Get from: https://platform.openai.com/api-keys

---

## Step 4: Configure Backend Build

Railway should auto-detect Python. If needed, create/verify these files:

### `backend/nixpacks.toml` (Optional - for custom build)

```toml
[phases.setup]
nixPkgs = ["python311", "postgresql"]

[phases.install]
cmds = ["pip install -r requirements.txt"]

[start]
cmd = "alembic upgrade head && python -m src.database.seed && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
```

### What the start command does:
1. `alembic upgrade head` - Runs database migrations
2. `python -m src.database.seed` - Seeds 4 test users
3. `uvicorn src.api.main:app` - Starts the API server

---

## Step 5: Deploy Backend

1. Railway will automatically deploy after detecting the repository
2. Wait for the build to complete (2-3 minutes)
3. Check logs for any errors
4. **Copy the backend URL** (e.g., `https://tribalcapturer-backend.railway.app`)

### Verify Backend Deployment:

Visit:
- Health check: `https://your-backend.railway.app/health`
- API docs: `https://your-backend.railway.app/docs`

Should see:
```json
{"status":"healthy","version":"1.0.0"}
```

---

## Step 6: Seed Knowledge Data (Optional)

After backend is deployed, you can seed the 27 sample knowledge entries.

### Option A: Run Seed Script via Railway Shell

1. Open Railway backend service
2. Click **"Shell"** tab
3. Run:
   ```bash
   chmod +x seed_all_knowledge.sh
   ./seed_all_knowledge.sh
   ```

### Option B: Create a One-Time Job

Create a Python script to seed via API:

```python
# seed_railway.py
import requests
import json

BASE_URL = "https://your-backend.railway.app/api/v1"

# Login as MA
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"username": "ma1@tribaliq.com", "password": "TestPassword123!"}
)
cookies = response.cookies

# Create entries (copy from seed_all_knowledge.sh logic)
# ... rest of entries
```

Run locally: `python seed_railway.py`

### Option C: Manual Entry via Frontend

After frontend is deployed, login as MA and manually create entries.

---

## Step 7: Deploy Frontend

### Create New Service for Frontend

1. In Railway project, click **"+ New"**
2. Select **"GitHub Repo"** (same repo)
3. Configure **Root Directory**: `/frontend`
4. Configure **Build Command**: `npm install && npm run build`
5. Configure **Start Command**: `npm run preview -- --host 0.0.0.0 --port $PORT`

### Frontend Environment Variables

```bash
VITE_API_URL=https://your-backend.railway.app
```

**Important**: Replace `your-backend.railway.app` with actual backend URL from Step 5.

### Alternative: Use Vercel/Netlify for Frontend

If you prefer, deploy frontend separately:

**Vercel:**
```bash
cd frontend
vercel --prod
```

**Netlify:**
```bash
cd frontend
npm run build
netlify deploy --prod --dir=dist
```

Then update backend `CORS_ORIGINS` with the frontend URL.

---

## Step 8: Update CORS Origins

After frontend is deployed:

1. Copy frontend URL (e.g., `https://tribalcapturer-frontend.railway.app`)
2. Go to backend service → Variables
3. Update `CORS_ORIGINS`:
   ```json
   ["https://tribalcapturer-frontend.railway.app"]
   ```
4. Redeploy backend service

---

## Step 9: Test the Deployment

### Test Backend API

1. Visit: `https://your-backend.railway.app/docs`
2. Try the health check endpoint
3. Test login with test credentials

### Test Frontend

1. Visit: `https://your-frontend.railway.app`
2. Login as MA: `ma1@tribaliq.com` / `TestPassword123!`
3. Create a knowledge entry
4. Login as Creator: `creator1@tribaliq.com` / `TestPassword123!`
5. Test semantic search

### Test Database

1. Check Railway PostgreSQL service
2. View tables (should have users, knowledge_entries)
3. Verify 4 users exist (2 MAs, 2 Creators)

---

## Step 10: Seed All 27 Knowledge Entries

After deployment is working, add the sample data:

### Method 1: Via Railway Shell

```bash
# Connect to Railway backend shell
cd /app/backend
./seed_all_knowledge.sh
```

### Method 2: Via API (using Postman or curl)

Run the seed script from your local machine pointing to Railway backend:

```bash
# Update BASE_URL in seed script
sed -i 's|http://localhost:8777|https://your-backend.railway.app|g' seed_all_knowledge.sh
./seed_all_knowledge.sh
```

### Method 3: Create Python Seed Job

```python
# deploy_seed.py
import os
os.environ['DATABASE_URL'] = 'your-railway-postgres-url'

from backend.src.database.seed import seed_all_knowledge_types
seed_all_knowledge_types()
```

---

## Environment Variables Summary

### Backend Service

| Variable | Value | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql://${{Postgres.PGUSER}}:...` | Auto from Railway |
| `JWT_SECRET` | Random 32+ char string | Generate new |
| `JWT_ALGORITHM` | `HS256` | Fixed |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Fixed |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Fixed |
| `ENVIRONMENT` | `production` | Fixed |
| `CORS_ORIGINS` | `["https://your-frontend.railway.app"]` | Update with actual URL |
| `LOG_LEVEL` | `INFO` | Fixed |
| `OPENAI_API_KEY` | `sk-proj-...` | Your API key |

### Frontend Service

| Variable | Value | Notes |
|---|---|---|
| `VITE_API_URL` | `https://your-backend.railway.app` | Backend URL |

---

## Test Users (Pre-seeded)

After deployment and migration, these users will be available:

### Medical Assistants (Can Create Entries)
```
ma1@tribaliq.com / TestPassword123!
ma2@tribaliq.com / TestPassword123!
```

### Creators (Can Search/View Entries)
```
creator1@tribaliq.com / TestPassword123!
creator2@tribaliq.com / TestPassword123!
```

---

## Troubleshooting

### Build Fails

**Error**: `Module not found`
- **Fix**: Ensure `requirements.txt` includes all dependencies
- Check Railway logs for specific missing package

**Error**: `Database connection failed`
- **Fix**: Verify DATABASE_URL is correctly set
- Check PostgreSQL service is running

### Migration Fails

**Error**: `Alembic migration failed`
- **Fix**: Check migration files in `backend/src/database/migrations/versions/`
- View Railway logs for specific error
- May need to run: `alembic downgrade -1` then `alembic upgrade head`

### CORS Errors

**Error**: `CORS policy blocked`
- **Fix**: Update `CORS_ORIGINS` in backend environment variables
- Format must be JSON array: `["https://frontend.railway.app"]`
- Redeploy backend after changing

### Semantic Search Not Working

**Error**: `OpenAI API error`
- **Fix**: Verify `OPENAI_API_KEY` is set correctly
- Check OpenAI account has credits
- Semantic search auto-falls back to keyword search if OpenAI fails

---

## Production Recommendations

### Security

1. **Change JWT_SECRET** to a strong random value
2. **Rotate OpenAI API key** regularly
3. **Enable Railway's IP allowlist** for database
4. **Use environment-specific secrets** (don't commit .env)

### Performance

1. **Enable Railway's auto-scaling** for backend
2. **Add database connection pooling** (SQLAlchemy default is 5)
3. **Consider Redis cache** for search results
4. **Monitor OpenAI API usage** (costs per embedding)

### Monitoring

1. **Enable Railway logs** aggregation
2. **Set up alerts** for failures
3. **Monitor database size** (knowledge entries grow over time)
4. **Track API response times** via Railway metrics

### Backups

1. **Enable Railway PostgreSQL backups** (automatic)
2. **Export knowledge entries** periodically
3. **Version control migrations** (already done via Git)

---

## Deployment Checklist

- [ ] Create Railway project
- [ ] Add PostgreSQL database
- [ ] Configure backend environment variables
- [ ] Deploy backend service
- [ ] Verify backend health check
- [ ] Run database migrations (auto in start command)
- [ ] Verify 4 test users created
- [ ] Deploy frontend service
- [ ] Configure frontend VITE_API_URL
- [ ] Update backend CORS_ORIGINS
- [ ] Test login (MA and Creator)
- [ ] Seed 27 knowledge entries (optional)
- [ ] Test semantic search
- [ ] Test all 6 knowledge types
- [ ] Verify OpenAI integration working
- [ ] Check HTTPS certificates (auto via Railway)
- [ ] Test on mobile devices
- [ ] Share URLs with team

---

## URLs After Deployment

**Backend API**:
- Production: `https://tribalcapturer-backend.railway.app`
- API Docs: `https://tribalcapturer-backend.railway.app/docs`
- Health: `https://tribalcapturer-backend.railway.app/health`

**Frontend**:
- Production: `https://tribalcapturer-frontend.railway.app`

**Database**:
- Managed by Railway (internal access only)
- Can connect via Railway shell or local tools

---

## Post-Deployment

### Adding Real Users

Replace test users with real MA/Creator accounts:

```sql
-- Connect to Railway PostgreSQL
-- Delete test users (keep if needed for demo)
DELETE FROM users WHERE username LIKE '%@tribaliq.com';

-- Add real users
INSERT INTO users (id, username, full_name, role, hashed_password, is_active)
VALUES
  (gen_random_uuid(), 'sarah.johnson@hospital.com', 'Sarah Johnson', 'MA', '$2b$12$hashed_password', true),
  (gen_random_uuid(), 'john.smith@hospital.com', 'John Smith', 'Creator', '$2b$12$hashed_password', true);
```

Or create via API: `POST /api/v1/auth/register` (if you add registration endpoint)

---

**Deployment Time**: ~10-15 minutes
**Cost**: Railway free tier includes 500 hours/month (enough for testing)

Good luck with your deployment! 🚀

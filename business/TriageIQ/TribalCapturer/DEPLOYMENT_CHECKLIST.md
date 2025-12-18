# Railway Deployment Checklist

Copy this checklist and check off items as you complete them:

## Pre-Deployment

- [ ] Railway account created at https://railway.app
- [ ] GitHub repository accessible: https://github.com/karthi1975/TribalCapturer
- [ ] OpenAI API key ready (for semantic search)
- [ ] Reviewed RAILWAY_DEPLOYMENT.md documentation

## Railway Project Setup

- [ ] Created new Railway project
- [ ] Selected "Deploy from GitHub repo"
- [ ] Connected to karthi1975/TribalCapturer repository
- [ ] Railway detected the project successfully

## Database Configuration

- [ ] Added PostgreSQL database to project (+ New → Database → PostgreSQL)
- [ ] Noted down database connection details
- [ ] Database status shows "Active"

## Backend Environment Variables

Set these in Railway backend service → Variables:

- [ ] `DATABASE_URL` = `postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/${{Postgres.PGDATABASE}}`
- [ ] `JWT_SECRET` = (generated random 32+ char string)
- [ ] `JWT_ALGORITHM` = `HS256`
- [ ] `ACCESS_TOKEN_EXPIRE_MINUTES` = `15`
- [ ] `REFRESH_TOKEN_EXPIRE_DAYS` = `7`
- [ ] `ENVIRONMENT` = `production`
- [ ] `CORS_ORIGINS` = `["https://your-frontend-url.railway.app"]` (update after frontend deployed)
- [ ] `LOG_LEVEL` = `INFO`
- [ ] `OPENAI_API_KEY` = (your actual OpenAI API key)

### Generate JWT_SECRET

Run this command locally:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Backend Deployment

- [ ] Railway auto-detected Python/Nixpacks
- [ ] Build started successfully
- [ ] Migrations ran (check logs for "alembic upgrade head")
- [ ] Seed script ran (check logs for "Created test users")
- [ ] Deployment completed (status: Active)
- [ ] Backend URL copied (e.g., `https://tribalcapturer-backend.railway.app`)

## Backend Verification

- [ ] Health endpoint works: `https://your-backend.railway.app/health`
  - Should return: `{"status":"healthy","version":"1.0.0"}`
- [ ] API docs accessible: `https://your-backend.railway.app/docs`
- [ ] Can login via API docs with test credentials
- [ ] Database has 4 users (2 MAs, 2 Creators)

### Test Backend API

```bash
# Health check
curl https://your-backend.railway.app/health

# Test login
curl -X POST https://your-backend.railway.app/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ma1@tribaliq.com","password":"TestPassword123!"}'
```

## Frontend Deployment

**Option A: Railway**

- [ ] Created new service in same Railway project
- [ ] Set root directory to `/frontend`
- [ ] Set build command: `npm install && npm run build`
- [ ] Set start command: `npm run preview -- --host 0.0.0.0 --port $PORT`
- [ ] Set environment variable: `VITE_API_URL` = (backend URL from above)
- [ ] Frontend deployed successfully
- [ ] Frontend URL copied

**Option B: Vercel** (alternative)

- [ ] Installed Vercel CLI: `npm i -g vercel`
- [ ] Ran `cd frontend && vercel --prod`
- [ ] Set `VITE_API_URL` environment variable in Vercel dashboard
- [ ] Frontend deployed successfully
- [ ] Frontend URL copied

## CORS Configuration

- [ ] Updated backend `CORS_ORIGINS` with actual frontend URL
- [ ] Format verified: `["https://actual-frontend-url.com"]`
- [ ] Redeployed backend service
- [ ] CORS working (no errors in browser console)

## Seed Knowledge Data

**Option A: Via Railway Shell**

- [ ] Opened Railway backend service
- [ ] Clicked "Shell" tab
- [ ] Ran: `chmod +x seed_all_knowledge.sh`
- [ ] Ran: `./seed_all_knowledge.sh`
- [ ] Verified 18 entries created

**Option B: From Local Machine**

- [ ] Ran: `python backend/seed_railway_data.py https://your-backend.railway.app`
- [ ] All 27 entries created successfully

## End-to-End Testing

### Test as MA

- [ ] Visited frontend URL
- [ ] Logged in as: `ma1@tribaliq.com` / `TestPassword123!`
- [ ] Created a new knowledge entry
- [ ] Selected knowledge type from dropdown
- [ ] Published entry successfully
- [ ] Viewed "My Entries" list

### Test as Creator

- [ ] Logged out from MA account
- [ ] Logged in as: `creator1@tribaliq.com` / `TestPassword123!`
- [ ] Viewed "Browse All" tab
- [ ] Saw entries (including newly created one)
- [ ] Switched to "Intelligent Search" tab
- [ ] Tested semantic search with query: "heart failure labs"
- [ ] Saw results with relevance scores
- [ ] Clicked entry to view details

### Test All 6 Knowledge Types

- [ ] Diagnosis → Specialty entries visible
- [ ] Provider Preference entries visible
- [ ] Continuity of Care entries visible
- [ ] Pre-Visit Requirement entries visible
- [ ] Scheduling Workflow entries visible
- [ ] General Knowledge entries visible

### Test Intelligent Features

- [ ] Semantic search returns relevant results
- [ ] Relevance scores displayed (61-68% range)
- [ ] Match type shown (semantic vs keyword)
- [ ] Autocomplete working for providers
- [ ] Autocomplete working for specialties
- [ ] Autocomplete working for facilities

## Production Readiness

### Security

- [ ] Changed JWT_SECRET to production value (not the test one)
- [ ] HTTPS working (Railway provides automatically)
- [ ] HTTPOnly cookies enabled (secure attribute set)
- [ ] Test user passwords changed or accounts disabled
- [ ] OpenAI API key secured (not in public repos)

### Performance

- [ ] Database connection pooling enabled (SQLAlchemy default)
- [ ] Railway auto-scaling configured (if needed)
- [ ] Monitoring enabled in Railway dashboard
- [ ] Logs accessible and readable

### Monitoring

- [ ] Railway logs showing healthy requests
- [ ] No error messages in production logs
- [ ] Database queries performing well
- [ ] OpenAI API calls succeeding

### Backups

- [ ] Railway PostgreSQL automatic backups enabled
- [ ] Noted backup retention policy
- [ ] Tested database restoration (if needed)

## Documentation

- [ ] Updated README with production URLs
- [ ] Shared frontend URL with team
- [ ] Shared test credentials with team
- [ ] Documented any deployment-specific changes

## Optional: Custom Domain

- [ ] Added custom domain in Railway
- [ ] DNS records configured
- [ ] SSL certificate issued
- [ ] Updated CORS_ORIGINS with custom domain

## Post-Deployment

- [ ] Sent deployment announcement to team
- [ ] Scheduled follow-up to add real user accounts
- [ ] Planned knowledge entry migration from test to production
- [ ] Set up monitoring alerts (Railway integrations)

---

## Quick Reference

### URLs

- **Backend**: https://_____________________.railway.app
- **Frontend**: https://_____________________.railway.app
- **API Docs**: https://_____________________.railway.app/docs
- **Health Check**: https://_____________________.railway.app/health

### Test Credentials

**Medical Assistants:**
- ma1@tribaliq.com / TestPassword123!
- ma2@tribaliq.com / TestPassword123!

**Creators:**
- creator1@tribaliq.com / TestPassword123!
- creator2@tribaliq.com / TestPassword123!

### Support

- Railway Docs: https://docs.railway.app
- Project README: RAILWAY_DEPLOYMENT.md
- Issues: https://github.com/karthi1975/TribalCapturer/issues

---

**Deployment Date**: ___________________
**Deployed By**: ___________________
**Notes**: ___________________

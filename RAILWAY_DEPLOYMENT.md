# 🚂 Railway Deployment Guide for TreeBeard

This guide will walk you through deploying TreeBeard to Railway in under 15 minutes.

---

## 📋 Prerequisites

Before you begin, make sure you have:

- [ ] GitHub account with TreeBeard repository pushed
- [ ] Railway account (sign up at [railway.app](https://railway.app))
- [ ] OpenAI API key (get one at [platform.openai.com](https://platform.openai.com))
- [ ] All your local changes committed and pushed to GitHub

---

## 🚀 Step 1: Create Railway Project (2 minutes)

1. **Sign in to Railway**
   - Go to [railway.app](https://railway.app)
   - Click "Login" and connect with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your `TreeBeard` repository
   - Railway will automatically detect your project

---

## 🗄️ Step 2: Add PostgreSQL Database (1 minute)

1. **In your Railway project dashboard:**
   - Click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Railway will provision a PostgreSQL database automatically

2. **Get the Database URL:**
   - Click on the PostgreSQL service
   - Go to "Variables" tab
   - Copy the `DATABASE_URL` value (you'll need this)

---

## ⚙️ Step 3: Configure Backend Service (5 minutes)

1. **Select the Backend Service:**
   - In your Railway dashboard, you should see a service for your repo
   - Click on it

2. **Configure Root Directory:**
   - Go to "Settings" tab
   - Scroll to "Service" section
   - Set **Root Directory** to: `src/backend`
   - Click "Save"

3. **Set Environment Variables:**
   - Go to "Variables" tab
   - Click "Raw Editor" for easier editing
   - Paste the following (update values in ALL CAPS):

   ```env
   # Application
   ENVIRONMENT=production
   DEBUG=false
   APP_NAME=TreeBeard Energy Recommendation API

   # Database (Railway provides this automatically)
   # DATABASE_URL is already set by Railway - don't override it!

   # Security - GENERATE A NEW SECRET KEY!
   # Run: python -c "import secrets; print(secrets.token_urlsafe(32))"
   SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_MINUTES=1440

   # CORS - UPDATE AFTER DEPLOYING FRONTEND
   CORS_ORIGINS=["https://YOUR-FRONTEND-URL.railway.app"]

   # OpenAI - REQUIRED FOR AI EXPLANATIONS
   OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-OPENAI-KEY
   OPENAI_MODEL=gpt-4o-mini

   # Optional: Redis (add if you add Redis service)
   # REDIS_URL=redis://...

   # Monitoring
   MONITORING_ENABLED=false
   LOG_LEVEL=INFO

   # Rate Limiting
   RATE_LIMIT_PER_USER=1000/minute
   RATE_LIMIT_PER_IP=10000/hour
   ```

4. **Set Python Version (if needed):**
   - Still in "Settings" tab
   - Find "Build" section
   - Add this custom build command if needed:
   ```
   pip install -r requirements.txt
   ```

5. **Deploy Backend:**
   - Click "Deploy" or wait for auto-deploy
   - Watch the build logs to ensure success

---

## 🗃️ Step 4: Initialize Database (2 minutes)

After the backend deploys successfully, you need to run database migrations.

### Option A: Using Railway CLI (Recommended)

1. **Install Railway CLI locally** (if not already installed):
   ```bash
   # macOS/Linux
   brew install railway

   # Or using npm
   npm install -g @railway/cli

   # Or using curl
   bash <(curl -fsSL cli.new)
   ```

2. **Login and link to your project:**
   ```bash
   railway login
   railway link
   ```
   - Select your TreeBeard project when prompted

3. **Run migrations:**
   ```bash
   railway run --service backend alembic upgrade head
   ```

   Or if you're in the backend directory:
   ```bash
   cd src/backend
   railway run --service backend python -m alembic upgrade head
   ```

4. **Verify database is initialized:**
   - Check your Railway logs for success messages
   - You should see "Running upgrade" messages

### Option B: Automatic Migrations via Start Command

Alternatively, you can have migrations run automatically on deploy by updating your start command:

1. Go to your backend service → **Settings** → **Deploy**
2. Change **Start Command** to:
   ```bash
   alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port $PORT
   ```
3. **Redeploy** the service

This will run migrations before starting the server on every deploy.

### Option C: One-Time Job (Manual)

1. In Railway dashboard, go to your backend service
2. Click **"Run Command"** button (if available)
3. Enter: `alembic upgrade head`
4. Click **"Run"**

**Note:** If you see migration errors, check that your `DATABASE_URL` environment variable is properly set (Railway should set this automatically when you add PostgreSQL).

---

## 🌐 Step 5: Deploy Frontend (5 minutes)

Now let's deploy the React frontend:

### Option A: Deploy Frontend on Railway (Recommended)

1. **Add Frontend Service:**
   - In your Railway project, click "+ New"
   - Select "GitHub Repo" → same `TreeBeard` repository
   - Railway will create a second service

2. **Configure Frontend:**
   - Click on the new service
   - Go to "Settings" tab
   - Set **Root Directory** to: `src/frontend`
   - Set **Build Command** to: `npm run build`
   - Set **Start Command** to: `npm run preview`

3. **Set Frontend Environment Variables:**
   - Go to "Variables" tab
   - Add this variable:
   ```env
   VITE_API_BASE_URL=https://YOUR-BACKEND-URL.railway.app
   ```
   - Get your backend URL from the backend service's "Settings" → "Domains"

4. **Generate Frontend Domain:**
   - Go to "Settings" tab → "Networking"
   - Click "Generate Domain"
   - Copy the generated URL (e.g., `your-app.railway.app`)

5. **Update Backend CORS:**
   - Go back to your **backend service**
   - Update the `CORS_ORIGINS` variable to include your frontend URL:
   ```env
   CORS_ORIGINS=["https://your-frontend-url.railway.app"]
   ```

6. **Deploy Frontend:**
   - Click "Deploy"
   - Wait for the build to complete

### Option B: Deploy Frontend on Vercel (Alternative - Simpler)

If you prefer Vercel for the frontend:

1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repo
3. Set **Root Directory** to: `src/frontend`
4. Add environment variable:
   ```
   VITE_API_BASE_URL=https://YOUR-BACKEND-URL.railway.app
   ```
5. Deploy
6. Update backend CORS with Vercel URL

---

## ✅ Step 6: Verify Deployment (2 minutes)

1. **Test Backend:**
   - Open: `https://your-backend.railway.app/health`
   - Should return: `{"status":"healthy"}`
   - Check API docs: `https://your-backend.railway.app/docs`

2. **Test Frontend:**
   - Open: `https://your-frontend.railway.app`
   - Go through the onboarding flow
   - Generate recommendations to verify end-to-end functionality

3. **Check Logs:**
   - In Railway, click on each service
   - Go to "Deployments" tab
   - Click "View Logs" to see real-time logs
   - Look for any errors

---

## 🔧 Troubleshooting

### Backend Won't Start

**Issue:** Build fails or service crashes

**Solutions:**
1. Check that `ROOT_DIRECTORY` is set to `src/backend`
2. Verify `DATABASE_URL` is set (should be automatic from PostgreSQL service)
3. Check logs for missing dependencies
4. Ensure `requirements.txt` is in `src/backend/`

### Database Connection Errors

**Issue:** Backend can't connect to PostgreSQL

**Solutions:**
1. Make sure PostgreSQL service is running
2. Verify `DATABASE_URL` variable is present
3. Check if migrations have been run: `alembic upgrade head`
4. Restart the backend service

### Frontend Can't Reach Backend

**Issue:** API calls fail with CORS errors

**Solutions:**
1. Check `VITE_API_BASE_URL` is set correctly in frontend
2. Verify backend's `CORS_ORIGINS` includes your frontend URL
3. Make sure both URLs use HTTPS (not HTTP)
4. Restart both services after changing environment variables

### 500 Errors on Recommendations

**Issue:** Generating recommendations fails

**Solutions:**
1. Check `OPENAI_API_KEY` is set correctly
2. Verify database has plan data (may need to seed database)
3. Check backend logs for specific error messages
4. Verify user is being created properly (check database)

---

## 📊 Monitoring & Logs

### View Logs
- Click on any service
- Go to "Deployments" tab
- Click "View Logs"
- Use filter to search for errors: `level:error`

### Check Resource Usage
- Click on service
- Go to "Metrics" tab
- Monitor CPU, Memory, and Network usage

### Set Up Alerts
- Go to project "Settings"
- Set up notification webhooks for deployment failures

---

## 💰 Cost Estimate

Railway pricing (as of 2024):

- **Free tier:** $5 credit/month
- **PostgreSQL:** ~$5/month
- **Backend service:** ~$5-10/month (depends on usage)
- **Frontend service:** ~$5/month (or $0 on Vercel)

**Total estimated cost:** $15-20/month

---

## 🔒 Security Checklist

Before going live, make sure:

- [ ] `SECRET_KEY` is a strong random string (not the default)
- [ ] `DEBUG` is set to `false`
- [ ] `ENVIRONMENT` is set to `production`
- [ ] `OPENAI_API_KEY` is kept secret (never commit to git)
- [ ] CORS is configured correctly (only allow your frontend domains)
- [ ] Database has strong password (Railway provides this)
- [ ] SSL/HTTPS is enabled (Railway provides this by default)

---

## 🚀 Going Further

### Add Custom Domain

1. In Railway project, go to service "Settings"
2. Scroll to "Networking" → "Domains"
3. Click "Custom Domain"
4. Add your domain (e.g., `api.yourdomain.com`)
5. Configure DNS records as shown

### Add Redis Caching

1. In Railway project, click "+ New"
2. Select "Database" → "Redis"
3. Railway provisions Redis automatically
4. Copy `REDIS_URL` from Redis service variables
5. Add `REDIS_URL` to your backend service variables
6. Restart backend service

### Set Up Database Backups

1. Click on PostgreSQL service
2. Go to "Data" tab
3. Click "Backup Now" to create manual backup
4. Railway automatically creates daily backups

### Enable Monitoring

1. Add Sentry for error tracking:
   ```env
   SENTRY_DSN=your-sentry-dsn
   MONITORING_ENABLED=true
   ```

2. Add DataDog for metrics (optional):
   ```env
   DATADOG_AGENT_HOST=your-dd-host
   ```

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [FastAPI Deployment Best Practices](https://fastapi.tiangolo.com/deployment/)
- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [PostgreSQL on Railway](https://docs.railway.app/databases/postgresql)

---

## 🎉 You're Done!

Your TreeBeard application is now live on Railway!

**Next steps:**
1. Share the URL with users
2. Monitor logs and usage
3. Set up custom domain (optional)
4. Enable monitoring (recommended for production)

Need help? Check the logs or reach out to Railway support.

---

**Pro tip:** Railway automatically deploys on every git push to main. Make sure to test changes locally before pushing!

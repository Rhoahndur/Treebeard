# ✅ Railway Deployment Checklist

Use this checklist while deploying TreeBeard to Railway.

---

## 🔧 Pre-Deployment

- [ ] All code committed and pushed to GitHub
- [ ] OpenAI API key ready
- [ ] Railway account created
- [ ] Generated a secure `SECRET_KEY`:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

---

## 🚂 Railway Setup

### Create Project
- [ ] Created new Railway project from GitHub repo
- [ ] PostgreSQL database added to project

### Backend Configuration
- [ ] Backend service created
- [ ] Root directory set to: `src/backend`
- [ ] Environment variables configured:
  - [ ] `SECRET_KEY` (generated)
  - [ ] `OPENAI_API_KEY` (your key)
  - [ ] `ENVIRONMENT=production`
  - [ ] `DEBUG=false`
  - [ ] `CORS_ORIGINS` (will update after frontend deploy)
- [ ] Backend deployed successfully
- [ ] Backend health check passes: `/health`

### Database Setup
- [ ] Database migrations run: `alembic upgrade head`
- [ ] Database connection verified in logs

### Frontend Configuration
- [ ] Frontend service created
- [ ] Root directory set to: `src/frontend`
- [ ] `VITE_API_BASE_URL` set to backend URL
- [ ] Frontend domain generated
- [ ] Backend `CORS_ORIGINS` updated with frontend URL
- [ ] Frontend deployed successfully
- [ ] Frontend loads in browser

---

## ✅ Verification

- [ ] Backend health endpoint works: `https://your-backend.railway.app/health`
- [ ] API docs accessible: `https://your-backend.railway.app/docs`
- [ ] Frontend loads: `https://your-frontend.railway.app`
- [ ] Can complete full onboarding flow
- [ ] Can generate recommendations successfully
- [ ] No CORS errors in browser console
- [ ] No errors in Railway logs

---

## 🔒 Security

- [ ] `SECRET_KEY` is not the default value
- [ ] `DEBUG` is set to `false`
- [ ] `OPENAI_API_KEY` not committed to git
- [ ] CORS only allows your frontend domain
- [ ] HTTPS working on both services

---

## 📝 Post-Deployment

- [ ] Save backend URL for reference
- [ ] Save frontend URL for reference
- [ ] Test all major features
- [ ] Share URL with stakeholders
- [ ] (Optional) Set up custom domain
- [ ] (Optional) Enable monitoring

---

## 🆘 If Something Goes Wrong

**Backend won't start?**
→ Check logs in Railway dashboard → Deployments → View Logs

**Database errors?**
→ Verify migrations ran: `alembic upgrade head`

**CORS errors?**
→ Double-check `CORS_ORIGINS` includes frontend URL with https://

**500 errors?**
→ Check OpenAI API key is valid and has credits

---

## 🎉 Success!

When all boxes are checked, your app is live! 🚀

**Your URLs:**
- Backend: `https://_______________`
- Frontend: `https://_______________`

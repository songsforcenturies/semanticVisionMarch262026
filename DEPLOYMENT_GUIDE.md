# Semantic Vision — Deployment Guide (Scalable Cloud Architecture)

## Architecture Overview

Designed to start free/cheap and scale to billions of users without re-architecting.

```
Users → Vercel CDN (100+ edge locations) → React Frontend
                                              ↓ /api/*
                                    Railway / Cloud Run (auto-scaling backend)
                                              ↓
                                    MongoDB Atlas (auto-scaling database)
                                              ↓
                                    OpenRouter (AI/LLM via API)
```

| Layer | Service | Cost Now | At Scale |
|-------|---------|----------|----------|
| Frontend | Vercel | FREE | FREE (100GB bandwidth, then $20/mo) |
| Backend | Railway | $5/mo | Pay per use, auto-scales |
| Database | MongoDB Atlas | FREE (512MB) | Pay per use, auto-shards |
| AI/LLM | OpenRouter | Pay per use | Pay per use + free models |
| **Total** | | **~$5/mo** | **Scales proportionally** |

---

## Step 1: Set Up MongoDB Atlas (Free Tier)

1. Go to https://www.mongodb.com/atlas and create a free account
2. Click "Build a Database" → choose **M0 FREE** (512MB)
3. Choose cloud provider: **AWS**, region: **us-east-1** (or closest to users)
4. Cluster name: `semantic-vision`
5. Click "Create Deployment"

### Configure access:
6. **Database Access** → Add Database User:
   - Username: `semanticvision`
   - Password: generate a strong one — **save this**
   - Role: "Read and write to any database"
7. **Network Access** → Add IP Address:
   - Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - This is required for Railway/Cloud Run (dynamic IPs)
8. Click **"Connect"** → "Drivers" → Copy the connection string:
   ```
   mongodb+srv://semanticvision:<password>@semantic-vision.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=semantic-vision
   ```
   Replace `<password>` with your actual password.

### Scaling path:
- M0 (Free): 512MB, shared — good for development and early users
- M10 ($57/mo): 10GB, dedicated — thousands of users
- M30+ ($340+/mo): auto-scaling, replication — millions of users
- Atlas scales seamlessly — no code changes needed

---

## Step 2: Deploy Backend on Railway

Railway auto-scales, deploys from GitHub, and costs ~$5/mo to start.

1. Go to https://railway.app and sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select your repo: `songsforcenturies/semanticVisionMarch262026`
4. Railway will detect the repo — click on the service and configure:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### Set environment variables:
In the Railway dashboard → Variables tab, add:

```
MONGO_URL=mongodb+srv://semanticvision:<password>@semantic-vision.xxxxx.mongodb.net/?retryWrites=true&w=majority&appName=semantic-vision
DB_NAME=leximaster_db
CORS_ORIGINS=https://semanticvision.ai,http://localhost:3000
JWT_SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
OPENROUTER_API_KEY=sk-or-v1-your-key-here
RESEND_API_KEY=re_your_key_here
SENDER_EMAIL=Semantic Vision <hello@semanticvision.ai>
STRIPE_SECRET_KEY=sk_test_your_key_here
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_SECRET=your_paypal_secret
DAILY_CO_API_KEY=your_daily_co_key
FRONTEND_URL=https://semanticvision.ai
```

5. Railway will auto-deploy. Note the generated URL (e.g., `sv-backend-production.up.railway.app`)
6. Optionally add a custom domain in Settings → Domains → `api.semanticvision.ai`

### Scaling path:
- Railway: auto-scales containers, pay per usage
- Google Cloud Run: even more scalable (scales to zero, handles millions of requests)
- AWS ECS/Fargate: enterprise-grade, Kubernetes-compatible

---

## Step 3: Deploy Frontend on Vercel

Vercel serves your React app from 100+ global edge locations — handles billions of page loads.

1. Go to https://vercel.com and sign up with GitHub
2. Click **"Add New Project"** → Import `songsforcenturies/semanticVisionMarch262026`
3. Configure:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `yarn build` (or `npm run build`)
   - **Output Directory**: `build`
4. Add environment variable:
   ```
   REACT_APP_BACKEND_URL=https://sv-backend-production.up.railway.app
   ```
   (Use your Railway URL, or `https://api.semanticvision.ai` if you set a custom domain)
5. Click **Deploy**

### Scaling path:
- Vercel free tier: 100GB bandwidth/mo — enough for millions of users
- Vercel Pro ($20/mo): 1TB bandwidth, more builds
- Frontend is static files served from CDN — scales infinitely

---

## Step 4: Connect Your Domain

### For semanticvision.ai:

**Option A: Vercel handles everything (recommended)**
1. In Vercel → Project Settings → Domains → Add `semanticvision.ai`
2. Vercel will give you nameservers or DNS records
3. In your domain registrar, update DNS as instructed
4. Vercel handles SSL automatically

**Option B: Use Cloudflare (more control)**
1. Move DNS to Cloudflare (free)
2. Add records:
   - `semanticvision.ai` → CNAME to `cname.vercel-dns.com`
   - `api.semanticvision.ai` → CNAME to your Railway domain
3. Cloudflare adds CDN caching + DDoS protection for free

---

## Step 5: Verify Everything Works

```bash
# Test backend health
curl https://api.semanticvision.ai/api/ping

# Test database connection
curl https://api.semanticvision.ai/api/diagnostics

# Test frontend
open https://semanticvision.ai
```

---

## Hosting Multiple Apps

Both Vercel and Railway support multiple projects under one account:

| App | Frontend (Vercel) | Backend (Railway) |
|-----|-------------------|-------------------|
| Semantic Vision | semanticvision.ai | api.semanticvision.ai |
| App #2 | app2.com | api.app2.com |
| App #3 | app3.com | api.app3.com |

Each app has its own deployment — no interference between them.
Vercel free tier supports unlimited projects.
Railway charges per usage across all projects.

---

## Updating the App

Push to GitHub → both Vercel and Railway auto-deploy:
```bash
git add -A
git commit -m "Update feature"
git push origin main
# Both frontend and backend redeploy automatically
```

---

## Backup

MongoDB Atlas provides:
- **Automatic daily snapshots** (free tier)
- **Point-in-time recovery** (paid tiers)
- **Manual export**: `mongodump --uri="your_uri"`
- The `seed_backup.json` in the repo auto-restores if the DB is empty

---

## Cost Comparison

| Item | Emergent AI | GoDaddy | New Setup |
|------|------------|---------|-----------|
| Hosting | Credits (~$50+/mo) | $51/mo | FREE - $5/mo |
| Database | Included (wiped your data) | N/A | FREE (MongoDB Atlas) |
| SSL/HTTPS | Included | Extra | FREE (Vercel/Cloudflare) |
| CDN | None | None | FREE (Vercel, 100+ locations) |
| AI/LLM | Emergent credits | N/A | OpenRouter (pay per use) |
| Auto-scaling | No | No | YES (all layers) |
| **Total** | **$100+/mo** | **$51/mo** | **~$5/mo to start** |

---

## Alternative: VPS Approach (Docker Compose)

If you prefer full control over a single server, the repo also includes:
- `docker-compose.yml` — runs frontend + backend together
- `backend/Dockerfile` + `frontend/Dockerfile`
- See the docker-compose setup for VPS deployment (DigitalOcean $6/mo, Hetzner $4.50/mo)

This is simpler but doesn't auto-scale. Good for development or low-traffic apps.

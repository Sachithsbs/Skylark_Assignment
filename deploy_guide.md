# 10-Minute Deployment Guide (100% Free Hosting)

Follow these steps to deploy the Skylark BI Agent live on your custom `.xyz` domain.

---

## Step 1: Push Code to GitHub

1. Create a new repository on your GitHub account called `skylark-bi`.
2. Open a terminal in the root workspace folder `d:\Skylark` and run:
   ```bash
   git init
   git add .
   git commit -m "Configure deployment and DB adapters"
   git branch -M main
   git remote add origin https://github.com/your-username/skylark-bi.git
   git push -u origin main
   ```

---

## Step 2: Create a Free PostgreSQL Database on Supabase

1. Go to **[supabase.com](https://supabase.com/)** and sign up for a free account.
2. Click **New Project** and select the Free Tier ($0/month).
3. Set your database password and choose a region close to you.
4. Go to **Project Settings** → **Database** → **Connection Strings** (choose the "URI" or "Transaction" tab).
5. Copy the connection string. It will look like this:
   `postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres`
6. Save this connection string (you will paste it into Render).

---

## Step 3: Deploy Backend on Render (Free Web Service)

1. Go to **[render.com](https://render.com/)** and sign up for a free account.
2. Click **New +** → **Web Service**.
3. Connect your GitHub repository (`skylark-bi`).
4. Set the configuration values:
   - **Name**: `skylark-backend`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `python backend/run.py` (or `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`)
   - **Instance Type**: `Free`
5. Click **Advanced** and add the following Environment Variables:
   - `DATABASE_URL`: *Paste the connection string you copied from Supabase in Step 2*
   - `SECRET_KEY`: *Type a long random string*
   - `FRONTEND_URL`: `https://app.yourdomain.xyz` *(replace with your custom domain)*
   - `USE_MOCK_MONDAY`: `false`
   - `MONDAY_API_KEY`: *Your monday.com API Key*
   - `DEALS_BOARD_ID`: `5030219755`
   - `WORK_ORDERS_BOARD_ID`: `5030220085`
   - `GEMINI_API_KEY`: `AQ.Ab8RN6L2LQwtv0EIt1al6mnq8XuYsizn78RcmzWQXyOqLTANOg`
   - `GEMINI_MODEL`: `gemini-flash-latest`
6. Click **Deploy Web Service**.
7. Once deployed, copy your Render URL (e.g. `https://skylark-backend.onrender.com`).
8. Go to **Settings** in Render, find **Custom Domains**, and add `api.yourdomain.xyz`.

---

## Step 4: Configure & Deploy Frontend on Vercel (Free Tier)

Before deploying the frontend, update the API URL in the code to point to your live backend.

1. Open `frontend/src/services/api.ts`.
2. Update line 4:
   ```typescript
   const API_BASE_URL = 'https://api.yourdomain.xyz/api';
   ```
3. Commit and push this change to GitHub:
   ```bash
   git add frontend/src/services/api.ts
   git commit -m "Update API URL for production"
   git push
   ```
4. Go to **[vercel.com](https://vercel.com/)** and sign up for a free account.
5. Click **Add New** → **Project** and import your `skylark-bi` repository.
6. Configure the Vercel project:
   - **Root Directory**: Select `frontend` (crucial so Vercel builds the React app instead of the backend).
   - **Framework Preset**: `Vite`.
7. Click **Deploy**.
8. Once built, go to **Settings** → **Domains** in Vercel and add `app.yourdomain.xyz`.

---

## Step 5: Configure Domain DNS Settings

Go to your domain registrar where you own your `.xyz` domain and add these 2 DNS records:

1. **For the Frontend (Vercel)**:
   - **Type**: `CNAME`
   - **Host**: `app`
   - **Value**: `cname.vercel-dns.com`
2. **For the Backend (Render)**:
   - **Type**: `CNAME`
   - **Host**: `api`
   - **Value**: `skylark-backend.onrender.com` *(replace with your Render URL)*

---

### That's it! 
Your application will be live at `https://app.yourdomain.xyz` communicating securely with your backend database on Supabase Postgres and pulling data dynamically from monday.com!

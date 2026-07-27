# Setup & Execution Instructions

This guide explains how to import the CSV spreadsheets into monday.com, configure the environment variables, and run both backend and frontend servers.

---

## 1. Importing CSV Data to Monday.com

To populate your boards with the assignments messy spreadsheets:

1. Log in to your **monday.com** account.
2. In your workspace, click **Add (+)** → **Import data** → **Excel / CSV**.
3. Upload the sample spreadsheets:
   - **Deals**: [Download Deal Funnel Sheet](https://docs.google.com/spreadsheets/d/1jghv-FiZ_bmWtEtB7IyaKYlwT5omEwSl/edit?usp=sharing)
   - **Work Orders**: [Download Work Order Tracker Sheet](https://docs.google.com/spreadsheets/d/1mL0GsxyhIYrUSHfkhbQ--SFfxrG1AE2j/edit?usp=sharing)
4. Verify column types:
   - Set monetary values (e.g. `Masked Deal value` and `Amount in Rupees`) as **Numbers**.
   - Set dates (e.g. `Close Date (A)` and `Probable End Date`) as **Date** columns.
   - Set status labels as **Status** or **Dropdown** columns.
5. Note the Board IDs from your browser URL:
   `https://yourcompany.monday.com/boards/`**`5030219755`**

---

## 2. Environment Configuration (`backend/.env`)

Create a `.env` file in the `backend/` directory using the following variables:

```env
# Authentication
SECRET_KEY=skylark-secret-key-for-dev-only-32chars
ACCESS_TOKEN_EXPIRE_MINUTES=480
FOUNDER_USERNAME=founder
FOUNDER_PASSWORD=skylark2026

# Database
# Local development defaults to SQLite. 
# For production, set to your Supabase PostgreSQL URL.
DATABASE_URL=sqlite:///./skylark.db

# monday.com Integration
USE_MOCK_MONDAY=false
MONDAY_API_KEY=your-monday-personal-access-token
DEALS_BOARD_ID=5030219755
WORK_ORDERS_BOARD_ID=5030220085

# Gemini Integration
GEMINI_API_KEY=AQ.Ab8RN6L2LQwtv0EIt1al6mnq8XuYsizn78RcmzWQXyOqLTANOg
GEMINI_MODEL=gemini-flash-latest

# CORS Configuration
FRONTEND_URL=http://localhost:5173
```

---

## 3. Running the Servers Locally

### 🅰️ Backend (FastAPI)
Navigate to the `backend/` directory and run:
```bash
pip install -r requirements.txt
python run.py
```
The server will start at **`http://localhost:8000`** and warm up the analytics cache.

### 🅱️ Frontend (Vite + React)
Navigate to the `frontend/` directory and run:
```bash
npm install
npm run dev
```
The dev server will start at **`http://localhost:5173`**.

---

## 4. 100% Free Production Deployment

To host this live for free on your custom domain, follow the visual steps in our **[deploy_guide.md](file:///d:/Skylark/deploy_guide.md)**:
1. Push code to GitHub.
2. Link a free Postgres DB on **Supabase** and paste the string in Render.
3. Deploy the backend on **Render** (Free Web Service).
4. Deploy the static frontend on **Vercel** (Free Tier).
5. Bind your `.xyz` DNS CNAME records to `app` and `api`.

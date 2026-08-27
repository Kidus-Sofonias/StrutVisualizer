# Deployment Guide

## Architecture
- **Frontend** (React) → Vercel
- **Backend** (Python FastAPI) → Railway

## Step 1: Deploy Backend on Railway

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `Kidus-Sofonias/StrutVisualizer`
4. Railway will detect the Python project. Add these settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r ../requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Go to **Settings** → **Networking** → **Generate Domain**
6. Copy the generated URL (e.g., `strutvisualizer-production.up.railway.app`)
7. This is your `VITE_API_URL`

## Step 2: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **Add New** → **Project**
3. Import `Kidus-Sofonias/StrutVisualizer`
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://your-railway-backend-url` (from Step 1.6)
6. Click **Deploy**

## Step 3: Test

1. Open your Vercel URL
2. Go to Import → Upload your .mdb file
3. All calculations should work

## Environment Variables

| Variable | Where | Description |
|----------|-------|-------------|
| `VITE_API_URL` | Vercel | Backend API URL |

## Local Development

```bash
# Terminal 1 - Backend
cd backend
pip install -r ../requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Updating

```bash
# Push changes
git add -A
git commit -m "Update"
git push

# Both Vercel and Railway auto-deploy on push to main
```

# Deployment Guide

This project is split into two components: a Python FastAPI backend and a React TypeScript frontend. Both need to be deployed separately for a complete production build.

## 1. Deploying the Backend (Render / Heroku)

The easiest way to deploy the Python backend is using [Render](https://render.com/) or Heroku.

### On Render:
1. Go to Render Dashboard.
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Set the following details:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - Add `GROQ_API_KEY` and set it to your actual API key.
6. Deploy the web service.
7. Note the URL generated (e.g., `https://your-backend-app.onrender.com`).

---

## 2. Deploying the Frontend (Vercel / Netlify)

For React applications, deploying on Vercel is extremely fast and seamless.

### On Vercel:
1. Go to your [Vercel Dashboard](https://vercel.com/dashboard).
2. Click **Add New...** -> **Project**.
3. Import your GitHub repository.
4. Set the **Root Directory** to `frontend`.
5. Vercel should auto-detect "Create React App" and pre-fill the Build (`npm run build`) and Output Directory (`build`) settings.
6. **Environment Variables:**
   - Add `REACT_APP_API_URL`
   - Value: The URL from your backend deployment _(e.g., `https://your-backend-app.onrender.com`)_.
7. Click **Deploy**.

## Post-Deployment Validation
Once deployed:
1. Visit the deployed frontend URL.
2. The UI should load. Check browser output (React DevTools or F12 console) to confirm it is fetching the graph from `REACT_APP_API_URL`.
3. Issue a text query to ensure your Render backend connects successfully to Groq to return AI-driven SQL analyses.

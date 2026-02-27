# SentriX Deployment Instructions

## Current Status

- ✅ Backend deployed on Render: https://sentrix-1.onrender.com
- ✅ Frontend code updated to use production backend
- ⏳ Frontend ready for Vercel deployment

## Vercel Deployment Steps

### 1. Push Changes to GitHub

Your frontend now uses the config system, which will automatically use the production backend URL. Push these changes:

```bash
git add .
git commit -m "Configure frontend for production deployment with Render backend"
git push origin main
```

### 2. Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI if you haven't
npm install -g vercel

# Navigate to frontend directory
cd frontend

# Deploy
vercel --prod
```

#### Option B: Using Vercel Dashboard

1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import your GitHub repository
4. Set root directory to `frontend`
5. Build settings:
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`
6. Click "Deploy"

### 3. Environment Variables (Optional)

If you want to use environment variables instead of the hardcoded config:

In Vercel Dashboard → Your Project → Settings → Environment Variables:

- **Name**: `REACT_APP_API_URL`
- **Value**: `https://sentrix-1.onrender.com`

### 4. Verify Deployment

Once deployed, test these features:

- Dashboard loads with risk data
- SentriX Assistant can send queries
- Route Planner works
- Reports can be generated and downloaded

## For Local Development

To use local backend during development, edit `frontend/src/config.js`:

```javascript
const config = {
  API_URL: "http://localhost:8000", // Uncomment this line
  // API_URL: 'https://sentrix-1.onrender.com',  // Comment this line
};
```

## Backend CORS Update (Important!)

After deploying to Vercel, you'll need to update the backend CORS settings:

1. Find your Vercel URL (e.g., `https://sentrix.vercel.app`)
2. Update `backend/main.py` CORS origins:

```python
origins = [
    "https://sentrix.vercel.app",  # Your Vercel domain
    "https://your-custom-domain.com",  # If you have a custom domain
    "http://localhost:3000",  # Keep for local dev
]
```

3. Redeploy backend on Render (it will auto-deploy if connected to GitHub)

## Troubleshooting

### Issue: CORS errors in browser console

**Solution**: Update backend CORS origins with your Vercel URL

### Issue: API calls failing

**Solution**: Check that `https://sentrix-1.onrender.com` is accessible and returning data

### Issue: Render backend sleeping (cold starts)

**Solution**:

- Render free tier sleeps after 15 minutes of inactivity
- First request may take 30-60 seconds to wake up
- Consider upgrading to paid tier for always-on service

## Next Steps After Deployment

1. Test all features on production
2. Update backend CORS with Vercel URL
3. Set up custom domain (optional)
4. Monitor backend logs on Render dashboard
5. Monitor frontend errors in Vercel dashboard

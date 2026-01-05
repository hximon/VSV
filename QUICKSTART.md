# Quick Start - Deploy to Vercel in 5 Minutes

## Step 1: Test Locally (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Test the setup
python test_vercel_setup.py

# Run locally
python api/index.py
# Visit http://localhost:5000
```

## Step 2: Push to GitHub

If not already done:

```bash
git init
git add .
git commit -m "Add Vercel support for AnyShell"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AnyShell.git
git push -u origin main
```

## Step 3: Deploy to Vercel

### Option A: One-Click Deploy (Easiest)
1. Click: [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/AnyShell)
2. Sign in with GitHub
3. Click "Deploy"
4. Done! 🎉

### Option B: Import Existing Repo
1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select your AnyShell repository
4. Click "Deploy"
5. Done! 🎉

### Option C: Vercel CLI
```bash
npm install -g vercel
vercel login
vercel --prod
```

## Step 4: Access Your Dashboard

After deployment (1-2 minutes), you'll get a URL like:
```
https://anyshell-xyz123.vercel.app
```

Open it in your browser to see your system monitoring dashboard!

## Important Notes

### ✅ What Works on Vercel:
- Real-time system monitoring
- CPU, memory, disk usage stats
- Network bandwidth tracking
- Beautiful web dashboard
- Auto-scaling and global CDN

### ❌ What Doesn't Work (Vercel Limitation):
- **SSH access via tmate** - Vercel is serverless (no persistent connections)
- Shell access to the server
- Long-running background processes

### 🚀 Need SSH Access?

For full SSH functionality, deploy on these platforms instead:
- **Railway** (https://railway.app) - Best for SSH + monitoring
- **Render** (https://render.com) - Free tier with Docker
- **Fly.io** (https://fly.io) - SSH access included

Use the original Docker deployment method on those platforms.

## Customization

### Change Ping URL
In Vercel Dashboard:
1. Go to Settings → Environment Variables
2. Add: `URL_TO_PING` = `https://yoursite.com`
3. Redeploy

### Custom Domain
1. Go to Settings → Domains
2. Add your domain
3. Update DNS records as instructed

## Troubleshooting

### "Module not found" error
- Ensure all dependencies are in `requirements.txt`
- Redeploy after adding missing packages

### Template/Static files not loading
- Check `vercel.json` routes configuration
- Ensure folders are not in `.vercelignore`

### Function timeout
- Vercel free tier: 10s timeout
- Upgrade to Pro for 60s timeout
- Or optimize your code

## Next Steps

1. ⭐ Star the repository if you find it useful
2. 🔧 Customize the dashboard styling in `static/style.css`
3. 📊 Add more monitoring metrics in `api/index.py`
4. 🚀 Share your deployment!

## Need Help?

- Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide
- Check [README.vercel.md](README.vercel.md) for Vercel-specific info
- Open an issue on GitHub

---

**Happy Deploying! 🎉**

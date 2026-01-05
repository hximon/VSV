# Complete Deployment Guide

## Quick Start - Vercel Deployment

### 1. Push to GitHub (if not already done)
```bash
git init
git add .
git commit -m "Add Vercel support"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AnyShell.git
git push -u origin main
```

### 2. Deploy to Vercel

**Method 1: Vercel Dashboard (Recommended)**
1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "Add New Project"
4. Import your AnyShell repository
5. Vercel will auto-detect settings from `vercel.json`
6. Click "Deploy"
7. Wait 1-2 minutes
8. Your site will be live at `https://your-project.vercel.app`

**Method 2: Vercel CLI**
```bash
# Install Vercel CLI globally
npm install -g vercel

# Login
vercel login

# Deploy (from project directory)
cd /path/to/AnyShell
vercel

# For production deployment
vercel --prod
```

### 3. Access Your Dashboard
Visit the URL provided by Vercel (e.g., `https://anyshell-abc123.vercel.app`)

## What You'll Get on Vercel

✅ **Working Features:**
- Real-time CPU monitoring
- Memory usage statistics
- Disk usage tracking
- Network bandwidth monitoring
- Uptime tracking (per serverless function instance)
- Ping status checks
- Beautiful web dashboard

❌ **Not Available (Serverless Limitations):**
- SSH access via tmate
- Persistent shell sessions
- Long-running background processes
- Direct server access

## For Full SSH Access - Use These Platforms Instead

### Railway.app (Recommended for SSH)
1. Go to https://railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your AnyShell repository
5. Railway will detect Dockerfile and deploy
6. Access web interface + SSH via tmate

### Render.com
1. Go to https://render.com
2. Sign up/Login
3. New Web Service → Connect repository
4. Select Docker environment
5. Deploy and access

### Fly.io
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Launch app
flyctl launch

# Deploy
flyctl deploy
```

## Project Structure

```
AnyShell/
├── api/                    # Vercel serverless functions
│   ├── __init__.py
│   └── index.py           # Main Flask app for Vercel
├── templates/
│   └── index.html         # Web dashboard
├── static/
│   └── style.css          # Styles
├── app.py                 # Original Flask app (for Docker)
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel configuration
├── .vercelignore         # Files to ignore in Vercel
├── Dockerfile            # For Docker deployments
├── docker-compose.yml    # Docker Compose config
├── start.sh              # Docker startup script
├── tmate.sh              # Tmate setup (Docker only)
├── README.md             # Main documentation
└── README.vercel.md      # Vercel-specific docs
```

## Environment Variables

### For Vercel:
Set in Vercel Dashboard → Settings → Environment Variables:
- `URL_TO_PING`: URL to check ping (default: https://google.com)

### For Docker:
Edit `docker-compose.yml` or set in hosting platform:
- `PORT`: Port to run on (default: 8080)
- `URL_TO_PING`: URL to check ping

## Local Development

### For Vercel Development:
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with Flask
cd api
python index.py

# OR run with Vercel CLI (better for testing)
vercel dev
```

### For Docker Development:
```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8080
```

## Troubleshooting

### Vercel Issues

**Problem: Import errors**
- Ensure all dependencies are in `requirements.txt`
- Vercel auto-installs from this file

**Problem: Template not found**
- Check paths in `api/index.py` are relative: `../templates`
- Ensure `templates/` folder is not in `.vercelignore`

**Problem: Function timeout**
- Vercel Hobby: 10s limit, Pro: 60s limit
- Optimize heavy operations

**Problem: Need SSH access**
- Use Railway, Render, or Fly.io instead
- Vercel is serverless and doesn't support persistent connections

### Docker Issues

**Problem: Tmate not connecting**
- Check firewall settings
- Ensure port 22 is not blocked
- Wait 10-15 seconds for tmate to initialize

**Problem: Port already in use**
- Change PORT environment variable
- Stop conflicting services

## Security Notes

⚠️ **Important:**
- This tool provides system access - use responsibly
- Don't expose sensitive information via SSH
- Use strong authentication on production systems
- Monitor access logs
- Consider IP whitelisting for SSH access

## Comparison: Vercel vs Docker Hosting

| Feature | Vercel | Docker (Railway/Render) |
|---------|--------|-------------------------|
| SSH Access | ❌ No | ✅ Yes (via tmate) |
| System Monitoring | ✅ Yes | ✅ Yes |
| Deployment Speed | ⚡ Very Fast | 🚀 Fast |
| Free Tier | ✅ Generous | ✅ Limited hours |
| Persistent Processes | ❌ No | ✅ Yes |
| Custom Domains | ✅ Yes | ✅ Yes |
| Best For | Monitoring only | Full SSH + Monitoring |

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See [LICENSE](LICENSE) file.

## Support

- Open an issue for bugs
- Star the repo if you find it useful!
- Follow for updates

---

**Built for educational purposes. Use responsibly and ethically.**

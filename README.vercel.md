# Vercel Deployment Guide for AnyShell

## Important Limitations

⚠️ **Vercel is a serverless platform**, which means:
- **No SSH access via tmate** - Vercel functions are stateless and short-lived (10 second timeout on Hobby plan, 60 seconds on Pro)
- **Limited system metrics** - You'll monitor the Vercel serverless function container, not a persistent server
- **No persistent processes** - Each request runs in an isolated, ephemeral container

## What Works on Vercel

✅ Web-based system monitoring dashboard
✅ CPU, Memory, Disk usage of the serverless function
✅ Network bandwidth statistics
✅ Uptime of the function (resets on each cold start)
✅ Ping status monitoring

## What Doesn't Work

❌ SSH access via tmate (requires persistent connection)
❌ Persistent shell access
❌ Long-running background processes

## Deployment Steps

### 1. Prerequisites
- GitHub account
- Vercel account (sign up at [vercel.com](https://vercel.com))

### 2. Deploy to Vercel

#### Option A: Via Vercel Dashboard
1. Fork this repository to your GitHub account
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your forked repository
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click "Deploy"

#### Option B: Via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod
```

### 3. Access Your Dashboard

After deployment, you'll get a URL like:
```
https://your-project.vercel.app
```

Visit this URL to see your system monitoring dashboard.

## Configuration

Edit `vercel.json` to customize:
- Environment variables (e.g., `URL_TO_PING`)
- Routes and redirects
- Build settings

## Alternative for SSH Access

If you need actual SSH/terminal access to a server, consider:
- **Railway.app** - Supports Docker and persistent connections
- **Render.com** - Free tier with Docker support
- **Fly.io** - Free tier with SSH access
- **AWS EC2** - Full VPS control
- **DigitalOcean** - Classic VPS hosting
- **Heroku** - Free tier (with some limitations)

The original Docker-based deployment in this repo works perfectly on those platforms.

## Local Development

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run locally
python api/index.py

# Or use Vercel CLI for local testing
vercel dev
```

## Environment Variables

Set in Vercel Dashboard → Settings → Environment Variables:

- `URL_TO_PING` - URL to check ping (default: https://google.com)

## Troubleshooting

### Issue: Functions timing out
- Vercel Hobby plan has 10s timeout, Pro has 60s
- Reduce monitoring interval or optimize code

### Issue: High cold start times
- First request after idle may be slow
- Consider upgrading to Vercel Pro for better performance

### Issue: Need SSH access
- Vercel doesn't support this - use Railway, Render, or a VPS instead

## Contributing

Feel free to open issues or submit PRs to improve Vercel compatibility!

## License

Same as the original project.

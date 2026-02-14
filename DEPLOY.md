# Mordomo EDP - Deployment Guide

This document provides deployment instructions for multiple platforms.

## Prerequisites

All deployments require the following environment variable:
- `SYNTHETIC_API_KEY` - Your API key for Synthetic.new LLM service

## Option 1: Render.com (Recommended)

The repository includes a `render.yaml` blueprint file for easy deployment.

### Steps:
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New" → "Web Service"
3. Connect your GitHub account and select the `mordomo-edp` repository
4. Render will automatically detect the `render.yaml` blueprint
5. Click "Create Web Service"
6. Once deployed, go to the service settings and add the environment variable:
   - `SYNTHETIC_API_KEY` = your_api_key_here
7. The service will be available at `https://mordomo-edp.onrender.com`

### URLs:
- Health check: `https://mordomo-edp.onrender.com/health`
- Chat API: `https://mordomo-edp.onrender.com/chat`

## Option 2: Railway.app

### Steps:
1. Go to [Railway Dashboard](https://railway.app/)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose the `mordomo-edp` repository
5. Railway will auto-detect the Python application
6. Add environment variable in the Variables tab:
   - `SYNTHETIC_API_KEY` = your_api_key_here
7. Deploy the service
8. Railway will provide a URL like `mordomo-edp.up.railway.app`

### Alternative: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd mordomo-edp
railway init

# Set environment variable
railway variables set SYNTHETIC_API_KEY=your_api_key_here

# Deploy
railway up
```

## Option 3: Fly.io

The repository includes a `fly.toml` configuration file.

### Steps:
1. Install Fly.io CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Login to Fly.io:
   ```bash
   flyctl auth login
   ```

3. Launch the app:
   ```bash
   cd mordomo-edp
   flyctl launch
   ```

4. Set the environment variable:
   ```bash
   flyctl secrets set SYNTHETIC_API_KEY=your_api_key_here
   ```

5. Deploy:
   ```bash
   flyctl deploy
   ```

The app will be available at `https://mordomo-edp.fly.dev`

## Option 4: Heroku

The repository includes `app.json` for Heroku deployment.

### Steps:
1. Install Heroku CLI:
   ```bash
   brew install heroku
   ```

2. Login to Heroku:
   ```bash
   heroku login
   ```

3. Create the app:
   ```bash
   cd mordomo-edp
   heroku create mordomo-edp
   ```

4. Set the environment variable:
   ```bash
   heroku config:set SYNTHETIC_API_KEY=your_api_key_here
   ```

5. Deploy:
   ```bash
   git push heroku main
   ```

The app will be available at `https://mordomo-edp.herokuapp.com`

### Alternative: Heroku Dashboard
1. Go to [Heroku Dashboard](https://dashboard.heroku.com/)
2. Click "New" → "Create new app"
3. Name it `mordomo-edp`
4. Connect GitHub repository
5. Enable automatic deploys from main branch
6. Add environment variable `SYNTHETIC_API_KEY`
7. Click "Deploy Branch"

## Testing the Deployment

After deployment, test the endpoints:

### Health Check
```bash
curl https://your-app-url/health
# Expected: {"status": "healthy", "agents": 3}
```

### Chat Endpoint
```bash
curl -X POST https://your-app-url/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá, qual é a minha fatura?", "session_id": "test"}'
```

## Troubleshooting

### Port Configuration
The application uses the `$PORT` environment variable provided by all platforms. Make sure your platform sets this automatically.

### Build Issues
If you encounter build issues:
1. Check that `requirements.txt` includes all dependencies
2. Verify Python version (3.11+ recommended)
3. Check build logs in the platform dashboard

### Environment Variables
Make sure `SYNTHETIC_API_KEY` is set correctly. Without it, the LLM integration will fail.

## Files Added for Deployment

- `render.yaml` - Render blueprint
- `runtime.txt` - Python version specification
- `Procfile` - Process definition for Render/Heroku
- `fly.toml` - Fly.io configuration
- `Procfile.heroku` - Heroku-specific Procfile
- `app.json` - Heroku app configuration
- `DEPLOY.md` - This file

## Support

For deployment issues, check the platform-specific documentation:
- [Render Docs](https://render.com/docs)
- [Railway Docs](https://docs.railway.app/)
- [Fly.io Docs](https://fly.io/docs/)
- [Heroku Docs](https://devcenter.heroku.com/)

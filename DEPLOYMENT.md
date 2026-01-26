# 🚀 Deployment Guide: Synthetic MRI Inspector

## Quick Deploy to Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account (you already have this!)
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### Deployment Steps

#### 1. **Sign Up for Streamlit Cloud**
   - Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
   - Click "Sign up" → "Sign up with GitHub"
   - Authorize Streamlit to access your GitHub repos

#### 2. **Deploy Your App**
   - Click "New app"
   - Select:
     - **Repository**: `MoumitaBasu/synthetic-mri-inspector`
     - **Branch**: `main`
     - **Main file path**: `app.py`
   - Click "Deploy"

✅ **Your app will be live in 2-3 minutes!**

Your URL will be: `https://synthetic-mri-inspector.streamlit.app` (or auto-generated)

#### 3. **Configure App Settings (Optional)**
   In Streamlit Cloud dashboard → App settings:
   - Set Python version: 3.9+
   - Add any secrets needed
   - Configure resource allocation

---

## Alternative Deployment Options

### 🟡 Railway.app (Modern Alternative)

#### 1. **Create Railway Account**
   - Go to [https://railway.app](https://railway.app)
   - Sign up with GitHub

#### 2. **Deploy via Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   cd /Users/moumitamac/synthetic-mri-inspector
   railway init
   railway up
   ```

#### 3. **Set Environment Variable**
   In Railway dashboard:
   - Add `STREAMLIT_SERVER_PORT=8000`

---

### 🔵 Render (Easy Alternative)

#### 1. **Create Render Account**
   - Go to [https://render.com](https://render.com)
   - Sign up with GitHub

#### 2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select your GitHub repo
   - Set:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `streamlit run app.py`
   - Deploy!

---

### 🔴 Azure App Service (Enterprise)

#### 1. **Install Azure CLI**
   ```bash
   brew install azure-cli
   az login
   ```

#### 2. **Create Resource Group**
   ```bash
   az group create --name mri-inspector-rg --location eastus
   ```

#### 3. **Create App Service Plan**
   ```bash
   az appservice plan create \
     --name mri-plan \
     --resource-group mri-inspector-rg \
     --sku B1 \
     --is-linux
   ```

#### 4. **Create Web App**
   ```bash
   az webapp create \
     --resource-group mri-inspector-rg \
     --plan mri-plan \
     --name synthetic-mri-inspector \
     --runtime "PYTHON|3.9"
   ```

#### 5. **Deploy Code**
   ```bash
   cd /Users/moumitamac/synthetic-mri-inspector
   az webapp up --name synthetic-mri-inspector
   ```

---

## Post-Deployment Checklist

- [ ] Test app loads without errors
- [ ] Test image upload functionality
- [ ] Test batch processing
- [ ] Test download/export features
- [ ] Check logs for errors
- [ ] Share URL with team/stakeholders

---

## Troubleshooting

### App Won't Start
```bash
# Check requirements
pip install -r requirements.txt

# Run locally first
streamlit run app.py
```

### Missing Dependencies
```bash
# Update requirements.txt
pip freeze > requirements.txt
```

### Performance Issues
- Increase server resources
- Reduce batch processing size limits
- Enable caching in Streamlit

### Image Upload Not Working
- Check file size limits (currently 200MB)
- Verify MIME types are allowed
- Check server logs

---

## Monitoring & Maintenance

### Streamlit Cloud
- View logs in dashboard
- Check app health
- View CPU/memory usage
- Manage secrets safely

### Local Updates
```bash
# Make changes locally
git add .
git commit -m "Update: Feature X"
git push origin main

# Auto-redeploys on Streamlit Cloud!
```

---

## Scaling Considerations

| Metric | Limit | Solution |
|--------|-------|----------|
| Concurrent Users | Depends on tier | Upgrade Streamlit Cloud plan |
| Upload Size | 200MB | Increase server limits |
| Memory | Varies | Optimize image processing |
| Processing Time | Streamlit timeout (24h) | Reduce batch size |

---

## Cost Estimates (Monthly)

| Platform | Free Tier | Paid Tier |
|----------|-----------|-----------|
| Streamlit Cloud | Yes (1 app) | $5-100+/month |
| Railway | $5 credit | Pay-as-you-go |
| Render | Limited free | $7-70+/month |
| Azure | 12-month free | $10-200+/month |

---

## Questions?

Refer to:
- [Streamlit Deployment Docs](https://docs.streamlit.io/streamlit-cloud)
- [Project README](./readme.md)
- [Setup Guide](./setup_guide.md)

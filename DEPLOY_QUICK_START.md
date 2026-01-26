# ⚡ Quick Deploy Reference

## 🟢 **FASTEST WAY: Streamlit Cloud (2 minutes)**

1. Go to → https://streamlit.io/cloud
2. Click **"New app"**
3. Select:
   - Repo: `MoumitaBasu/synthetic-mri-inspector`
   - Branch: `main`
   - File: `app.py`
4. Click **"Deploy"** ✅

**Done!** Your app is live in 2-3 minutes at `https://synthetic-mri-inspector.streamlit.app`

---

## 📋 What Gets Deployed

✅ **Your Code**
- `app.py` (Streamlit UI)
- `src/` folder (all modules)
- `requirements.txt` (Python packages)

✅ **Configuration**
- `.streamlit/config.toml` (UI theme & settings)
- `.streamlit/secrets.toml` (API keys - kept private)

❌ **NOT Deployed** (Git-ignored)
- `outputs/` (generated files)
- `venv/` (virtual environment)
- `__pycache__/` (Python cache)

---

## 🔗 Your Live App

Once deployed:
- **URL**: https://your-app.streamlit.app
- **Share with**: Anyone with the link
- **Auto-updates**: Every time you push to GitHub

---

## 🎛️ Post-Deployment Config (In Streamlit Cloud)

Click your app → Settings:
- Python version: **3.9+** ✓
- Advanced settings:
  - Client max message size: **200MB** ✓
  - Logger level: **info** ✓

---

## 🐛 If App Crashes

Check **Logs** tab in Streamlit Cloud dashboard:
- Look for error messages
- Common issues:
  - Missing dependencies → Update `requirements.txt`
  - Import errors → Check `sys.path.append('src')`
  - Memory issues → Reduce batch size limits

---

## 🔄 Updates & Rollback

```bash
# Make changes locally
nano app.py

# Commit & push
git add app.py
git commit -m "Fix: Description of change"
git push origin main

# Streamlit Cloud auto-redeploys in ~1 minute!
```

To rollback: Redeploy previous commit from Streamlit Cloud dashboard

---

## 📊 Monitor Your App

Streamlit Cloud shows:
- ✅ Last deployment status
- 📈 CPU/memory usage
- 🔴 Error logs
- 👥 Active user count

---

## 🚀 Deploy Now!

→ [Streamlit Cloud](https://streamlit.io/cloud)

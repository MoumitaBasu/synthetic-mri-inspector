# 🔧 Streamlit Deployment Troubleshooting

## Issue: `ModuleNotFoundError: matplotlib` (or other imports)

### Root Cause
Streamlit Cloud couldn't install dependencies from `requirements.txt` properly.

### Solution

Your `requirements.txt` has been updated with explicit, compatible versions:

```txt
# Core Scientific Stack
numpy>=1.20.0,<2.0
scipy>=1.6.0
pandas>=1.4.0
matplotlib>=3.5.0
seaborn>=0.11.0

# Image Processing
scikit-image>=0.18.0
Pillow>=9.0.0

# Streamlit
streamlit>=1.50.0

# Jupyter (for notebooks)
jupyter>=1.0.0
ipython>=7.0.0
```

### Steps to Fix

1. **Clear Streamlit Cloud Cache**
   - Go to your app in Streamlit Cloud
   - Click **"Manage app"** (lower right)
   - Click **"Reboot app"**
   - Wait 2-3 minutes for fresh install

2. **Redeploy from GitHub**
   - Make sure the latest commit is on main branch
   - Click **"Reboot app"** in Streamlit Cloud
   - Monitor **Logs** tab for installation progress

3. **Verify Locally** (Optional)
   ```bash
   cd /Users/moumitamac/synthetic-mri-inspector
   source venv/bin/activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

---

## Issue: `matplotlib` takes too long to import

### Solution
matplotlib is heavy but essential for visualizations. Streamlit Cloud will cache it after first install.

- ✅ First deployment: 3-5 minutes (matplotlib building)
- ✅ Subsequent deploys: 30-60 seconds (cached)

### If still slow:
1. Check **Logs** tab for detailed build status
2. Wait for "requirements successfully installed" message
3. Don't refresh or reboot mid-installation

---

## Issue: App crashes after "successfully deployed"

### Possible Causes & Fixes

| Error | Fix |
|-------|-----|
| `ImportError: No module named 'src'` | Check `sys.path.append('src')` at line 9 in app.py |
| `FileNotFoundError: outputs/` | App tries to create dirs - this is handled, should be OK |
| `ModuleNotFoundError: image_upload_handler` | Verify `src/image_upload_handler.py` exists in repo |
| Memory timeout | Reduce batch size or reload page |

### Debug Steps

1. **Check Logs**
   - Click your app → **Manage app** → **Logs**
   - Scroll to bottom for error details
   - Look for "ERROR" or "Traceback" lines

2. **Verify GitHub Commit**
   ```bash
   git log --oneline -3
   git status  # Should show "nothing to commit"
   ```

3. **Force Redeploy**
   - In Streamlit Cloud: Click **Reboot app** → **Yes**
   - Wait full 3-5 minutes

---

## Issue: Upload/Download buttons not working

### Likely Cause
Server-side save mode (`outputs/`) may not have write permissions.

### Solution
1. Go to Settings in Streamlit Cloud app
2. Change **Export Options** → **Save mode**
3. Select **"Download (browser)"** instead of "Save on server"
4. Refresh page and try again

---

## Issue: Batch processing times out

### Cause
Processing 20 samples takes >60 seconds (Streamlit Cloud timeout).

### Solution
1. Reduce batch size in sidebar to 5-10 samples
2. Or split into multiple smaller batches
3. Monitor the progress bar

---

## Issue: Image upload shows "File too large"

### Cause
Upload limit is 200MB (set in `config.toml`).

### Solution
For files >200MB:
1. Resize locally before uploading
2. Or increase limit in `.streamlit/config.toml`:
   ```toml
   [server]
   maxUploadSize = 500  # MB
   ```

---

## What to Do If Nothing Works

### Nuclear Option: Fresh Deploy

1. **In Streamlit Cloud:**
   - Delete the app (Settings → Delete app)
   - Wait 2 minutes

2. **Redeploy:**
   - Click "New app"
   - Select same repo & branch
   - Let it build fresh

3. **This usually fixes:**
   - Cached dependency issues
   - Configuration conflicts
   - Memory leaks from previous deploys

---

## Quick Health Check

Your app is working if:

✅ Page loads without errors  
✅ "Synthetic MRI Inspector" title visible  
✅ Sidebar controls responsive  
✅ "Generate New Sample" button works  
✅ Image displays in center  
✅ Download buttons appear  

---

## Still Having Issues?

Check these files in your repo:

- `requirements.txt` → Has all dependencies ✓
- `.streamlit/config.toml` → Valid TOML syntax ✓
- `app.py` → No syntax errors ✓
- `src/` folder → All 6 modules present ✓

If all verified, try fresh deploy (nuclear option above).

---

## Performance Tips

| Action | Benefit |
|--------|---------|
| Use Streamlit Cloud "Community" tier | Free |
| Limit batch to 5-10 samples | Prevents timeout |
| Use browser download mode | Faster (no server save) |
| Clear browser cache | Fixes UI glitches |
| Close unused tabs | Reduces memory use |

---

## Monitoring Your Deployment

**Streamlit Cloud Dashboard:**
- ✅ Shows deployment status (🟢 = healthy)
- ✅ Logs available 24/7
- ✅ Auto-redeploys on git push
- ✅ CPU/memory usage graphs

**GitHub Integration:**
- ✅ Auto-redeploy when you push to main
- ✅ Each commit gets logged
- ✅ Rollback available via branch selection

---

**Last Updated**: January 26, 2026  
**Status**: Requirements fixed & optimized for Streamlit Cloud

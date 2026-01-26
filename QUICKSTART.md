# 🚀 Quick Start Guide - Streamlit UI

## The Problem You Had
Before: When you ran `demo.py`, you only saw text in the terminal.  
Now: The Streamlit UI shows everything interactively with live visualizations!

## Installation (One-Time Setup)

```bash
# Navigate to project directory
cd synthetic-mri-inspector

# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# Install all dependencies including Streamlit
pip install -r requirements.txt
```

## Running the App

### The Simple Way
```bash
# From project root with venv activated:
streamlit run app.py
```

Your browser should automatically open at `http://localhost:8501`

If it doesn't open automatically:
- Manually visit: http://localhost:8501 in your web browser

### Stopping the App
Press `Ctrl+C` in the terminal where Streamlit is running

## What You'll See

### 🎯 Main Interface (4 Tabs)

**Tab 1: 📊 Single Analysis**
- Generate one custom sample
- See the synthetic MRI image
- View all extracted features
- Get quality classification with reasoning
- View comprehensive analysis visualization

**Tab 2: 📦 Batch Processing**
- Generate 1-20 samples at once
- See quality distribution (pie chart + bar chart)
- Compare feature statistics across samples
- Analyze feature correlations

**Tab 3: 📈 Feature Analysis**
- Detailed breakdown of each feature
- Radial density profile (center to edge)
- Feature importance visualization

**Tab 4: ℹ️ About**
- Project explanation
- How the classification works
- Real-world applications
- Technical stack info

### ⚙️ Sidebar Controls
- **Generate Sample**: Adjust seed, core, defect, click button
- **Batch Processing**: Set sample count, click button
- **Tune Thresholds**: Adjust classification thresholds in real-time

## Common Tasks

### Generate a Reproducible Sample
1. Sidebar → Set "Seed" to 42
2. Check "Force Core" if you want a core
3. Uncheck "Force Defect" for a good sample
4. Click "🔄 Generate New Sample"
5. See results in "Single Analysis" tab

### Process a Batch of Samples
1. Sidebar → Set "Number of Samples" to 10
2. Click "📦 Process Batch"
3. Wait for progress bar
4. View results: statistics, distribution, feature table
5. Scroll down for feature correlations

### Tune Classification Thresholds
1. Sidebar → Click "Tune Thresholds" to expand
2. Adjust sliders for:
   - **Min Uniformity** (default 0.60)
   - **Min Symmetry** (default 0.65)
   - **Max Anomaly Severity** (default 0.02)
3. Changes apply immediately!
4. Re-generate samples to see new classifications

### View Feature Details
1. Single Analysis tab
2. Scroll to "🔍 Extracted Features" section
3. See metrics for:
   - Intensity statistics
   - Structural features
   - Quality metrics

### Understand Why a Sample Got Its Grade
1. Generate a sample
2. Scroll to "📝 Decision Reasoning"
3. Each step shows:
   - What was checked ✓ or ⚠️
   - The value found
   - Impact on quality score

## Example Workflow

```
1. Start App
   → streamlit run app.py

2. Generate Sample
   → Sidebar: Seed=42, Force Core=ON, Defect=OFF
   → Click "Generate New Sample"

3. Review Results
   → See image in "Single Analysis"
   → Check metrics (Uniformity=0.78, Symmetry=0.82, etc.)
   → Read reasoning: "✓ Good uniformity", "⚠️ Wall too thick"

4. Process Batch
   → Sidebar: Number of Samples = 10
   → Click "Process Batch"
   → See distribution: 60% Standard, 40% Premium

5. Analyze Features
   → Tab: "📈 Feature Analysis"
   → View radial profile
   → See feature importance

6. Tune & Retry
   → Sidebar: Lower "Min Uniformity" to 0.50
   → Regenerate sample
   → See how threshold change affects grade
```

## Understanding the Visualizations

### Quality Score Bar
- Shows 0-100 scale
- Green line at 85 = Premium threshold
- Orange line at 60 = Standard threshold
- Your score position indicates grade

### Feature Metrics
- **Uniformity** (0-1): Material consistency
- **Symmetry** (0-1): Structural balance
- **Wall Thickness** (pixels): Shell measurement
- **Anomaly Severity** (0-1): Defect impact
- **Has Anomaly**: Boolean defect detection

### Radial Profile
- X-axis: Distance from center
- Y-axis: Intensity (brightness)
- Shape shows internal structure
- Peaks indicate boundaries between shell and inner tissue

### Correlation Scatter
- Shows relationship between features
- Points closer to diagonal = stronger correlation
- Color gradient shows quality score

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Stop app | `Ctrl+C` |
| Reload app | `R` (when focused on Streamlit) |
| Clear cache | Click "Always rerun" or `Ctrl+Shift+R` |

## Browser Tips

### If app is slow:
- Try a different browser (Chrome recommended)
- Clear browser cache
- Reduce batch size
- Close other tabs

### If visualizations don't show:
- Refresh the page (F5)
- Check browser console (F12) for errors
- Ensure matplotlib is properly installed
- Try another browser

### To maximize screen space:
- Press `X` to hide sidebar (sidebar button top-left)
- Sidebar returns on click
- Use fullscreen visualization mode if available

## Troubleshooting

### "Port 8501 already in use"
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### "Module not found: streamlit"
```bash
# Make sure venv is activated
source venv/bin/activate
pip install streamlit
```

### Black screen / nothing appears
1. Wait 10 seconds for initial load
2. Refresh browser (Ctrl+R)
3. Check terminal for error messages
4. Try: `streamlit run app.py --logger.level=debug`

### Visualizations missing
- Matplotlib might need a backend configuration
- Try closing and restarting the app
- Ensure you're using a modern web browser

## Comparing Demo vs Streamlit

### `demo.py` (Command-Line)
```bash
python demo.py
```
✓ Terminal text output  
✓ Generates PNG files  
✓ Good for automation  
✗ No interactivity  
✗ Hard to visualize  

### `app.py` (Streamlit UI)
```bash
streamlit run app.py
```
✓ **Interactive web interface**  
✓ **Real-time visualizations**  
✓ **Threshold tuning**  
✓ **Batch processing with feedback**  
✓ **Professional charts**  
✓ **Data tables**  

## Next Steps

### Explore the Project
1. **Single Analysis**: Generate samples with different seeds
2. **Batch Processing**: Understand quality distribution
3. **Feature Analysis**: Learn what each feature measures
4. **About Tab**: Read the complete explanation

### Modify and Experiment
- Adjust thresholds to see impacts
- Generate defective samples to understand detection
- Process large batches to find patterns
- Use specific seeds for reproducibility

### Integrate with Your Workflow
- Export feature tables for analysis
- Take screenshots for presentations
- Use as a teaching/demo tool
- Customize thresholds for your domain

### Run Both Interfaces
```bash
# Terminal 1: Streamlit UI
streamlit run app.py

# Terminal 2: Command-line demo (still works!)
python demo.py
```

## Getting Help

### In-App Help
- **About Tab**: Complete project explanation
- **Feature tooltips**: Hover over metrics for descriptions
- **Decision Reasoning**: Explains every classification

### Documentation
- **STREAMLIT_README.md**: Comprehensive feature guide
- **.github/copilot-instructions.md**: Architecture details
- **README.md**: Project overview
- **Source code comments**: Implementation details

## Performance Notes

- **Generating a sample**: < 1 second
- **Processing 10 samples**: 5-10 seconds
- **Processing 20 samples**: 10-20 seconds
- **Visualizations**: Generated on-demand, typically instant

Streamlit caches results automatically, so re-running with same settings is much faster!

---

## Now You're Ready! 🎉

```bash
# Start the app
source venv/bin/activate
streamlit run app.py

# Browser opens automatically at http://localhost:8501
# Start exploring!
```

**No more terminal-only text output!** 🎨📊✨

Questions? Check the About tab in the app or review STREAMLIT_README.md for comprehensive documentation.

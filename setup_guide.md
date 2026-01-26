# Setup Guide for GitHub

## Quick Setup (5 minutes)

### 1. Create Repository Structure

```bash
# Create project directory
mkdir synthetic-mri-inspector
cd synthetic-mri-inspector

# Create directory structure
mkdir -p src notebooks examples/outputs

# Initialize git
git init
```

### 2. Add Files

Copy all the provided files into their respective directories:

```
synthetic-mri-inspector/
├── README.md
├── requirements.txt
├── demo.py
├── src/
│   ├── __init__.py  (empty file)
│   ├── data_generator.py
│   ├── feature_extractor.py
│   ├── classifier.py
│   └── visualizer.py
├── notebooks/
│   └── exploration.ipynb
└── examples/
    └── outputs/  (will be populated when you run demo)
```

### 3. Create __init__.py

```bash
# Make src a Python package
touch src/__init__.py
```

### 4. Create .gitignore

Create a `.gitignore` file with:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebook
.ipynb_checkpoints
*.ipynb_checkpoints/

# Output files
examples/outputs/*.png
examples/outputs/*.txt
*.png
*.txt

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
```

### 5. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 6. Test the Setup

```bash
# Run the demo script
python demo.py
```

You should see output like:
```
======================================================================
  SYNTHETIC MRI INSIGHT EXPLORER - DEMO
======================================================================

[1/5] Initializing components...
      ✓ All components initialized

[2/5] Generating synthetic MRI samples...
      Sample 1: Premium (Score: 92, Confidence: 93%)
      ...
```

### 7. Commit to Git

```bash
git add .
git commit -m "Initial commit: Synthetic MRI Insight Explorer"
```

### 8. Push to GitHub

```bash
# Create a new repository on GitHub first, then:
git remote add origin https://github.com/yourusername/synthetic-mri-inspector.git
git branch -M main
git push -u origin main
```

---

## Testing Checklist

Before sharing your repository, verify:

- [ ] `python demo.py` runs without errors
- [ ] Jupyter notebook opens: `jupyter notebook notebooks/exploration.ipynb`
- [ ] All visualizations are generated in `examples/outputs/`
- [ ] README.md displays correctly on GitHub
- [ ] No sensitive information in commits
- [ ] `.gitignore` is working (no `__pycache__` in repo)

---

## Customization Tips

### Update README.md

1. Replace `[Your Name]` with your actual name
2. Replace GitHub/LinkedIn URLs with your profiles
3. Add your email if desired

### Add a License

Create `LICENSE` file:
```bash
# For MIT License
curl https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt > LICENSE
```

Then edit to add your name and year.

### Optional: Add GitHub Actions

Create `.github/workflows/test.yml` for automated testing:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run demo
      run: python demo.py
```

---

## Presentation Tips for Interview

### What to Show

1. **Start with README** - Let them see your thinking
2. **Run `demo.py`** - Show it works end-to-end
3. **Open Jupyter notebook** - Walk through the pipeline
4. **Show visualizations** - Discuss interpretability
5. **Explain code** - Pick one module to dive deep

### What to Say

**Opening**: "I built this to demonstrate my understanding of Orbem's philosophy: non-invasive inspection with data-efficient, interpretable methods."

**Key points**:
- "I chose rule-based classification over deep learning to show I understand when simpler is better"
- "Every decision is traceable - crucial for industrial quality control"
- "This works immediately without training data - important for rapid deployment"
- "With real MRI data, I'd validate these features and optimize thresholds"

**Closing**: "I'd love to discuss how this approach could complement Orbem's existing solutions or inspire new applications."

---

## Troubleshooting

### Issue: `ModuleNotFoundError`

**Solution**: Make sure you're in the project root and have activated your virtual environment:
```bash
cd synthetic-mri-inspector
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### Issue: Matplotlib not displaying

**Solution**: For Jupyter notebooks, add at the top:
```python
%matplotlib inline
```

### Issue: Import errors in Jupyter

**Solution**: Make sure Jupyter is installed in the same environment:
```bash
pip install jupyter
```

---

## Time Estimate

- **Basic setup**: 5 minutes
- **Testing everything**: 10 minutes
- **Customization**: 15 minutes
- **Total**: ~30 minutes

Good luck with your interview! 🚀

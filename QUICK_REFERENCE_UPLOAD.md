# Quick Reference - Image Upload Feature

## 🎯 Two-Mode Operation

```
┌─────────────────────────────────────────────────────────────┐
│                  SYNTHETIC MRI INSPECTOR                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  MODE 1: GENERATE SYNTHETIC            MODE 2: UPLOAD REAL  │
│  ════════════════════════════          ═══════════════════  │
│                                                              │
│  ┌─────────────────────────┐      ┌──────────────────────┐  │
│  │ Seed: [42________]      │      │ Choose File: [📁]   │  │
│  │ ☑ Force Core            │      │                      │  │
│  │ ☐ Force Defect          │      │ ✅ Format: PNG/JPG  │  │
│  │                         │      │ ✅ Size: < 10 MB    │  │
│  │ [🔄 Generate Sample]   │      │ ✅ Auto-resized     │  │
│  │                         │      │                      │  │
│  │ (each click = new image)│      │ [🔄 Reset]          │  │
│  └─────────────────────────┘      └──────────────────────┘  │
│         ↓ Synthetic                      ↓ Uploaded          │
│                                                              │
│           ┌──────────────────────────────┐                  │
│           │    IMAGE DISPLAYED & ANALYZED │                 │
│           │  (Same 15+ features either way)                 │
│           └──────────────────────────────┘                  │
│                                                              │
│  Both modes get:                                            │
│  ✓ Image statistics                                        │
│  ✓ 15+ feature extraction                                 │
│  ✓ Quality classification                                 │
│  ✓ Advanced visualizations                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Sidebar Controls

### Generate Mode (Top)
```
⚙️ Configuration
├─ Generate Sample
│  ├─ Seed: [number input]
│  ├─ ☐/☑ Force Core
│  ├─ ☐/☑ Force Defect
│  └─ [🔄 Generate New Sample]
│
└─ [→ Next Section Below]
```

### Upload Mode (Middle)
```
├─ Upload Real MRI Image
│  ├─ [Choose an MRI image ↓]
│  └─ [🔄 Reset to Synthetic]
│
└─ [→ Threshold Tuning Below]
```

### Configuration (Bottom)
```
├─ Batch Processing
│  ├─ Slider: Number of Samples
│  └─ [📦 Process Batch]
│
└─ Thresholds
   ├─ [⚙️ Tune Thresholds ↓]
   └─ (Min Uniformity, Symmetry, etc.)
```

---

## 🔄 User Workflows

### Workflow A: Synthetic Only
```
Click [🔄 Generate New Sample]
              ↓
        New image
              ↓
        Analyze results
              ↓
        Repeat or adjust seed
```

### Workflow B: Upload Only
```
Click [Choose an MRI image]
              ↓
     Select file → Upload
              ↓
     Image auto-processes
              ↓
     Analyze results
              ↓
     Click [🔄 Reset] for synthetic
```

### Workflow C: Mixed (Recommended)
```
Generate sample
    ↓ (Study results)
Upload image
    ↓ (Compare features)
Reset to synthetic
    ↓ (Back to generation)
Upload another
    ↓ (Test different images)
...repeat
```

---

## 📊 Analysis Output (Both Modes)

```
┌──────────────────────────────┐
│ 📊 SINGLE ANALYSIS TAB       │
├──────────────────────────────┤
│                              │
│ [Image Display]    [Stats]   │
│ ┌──────────────┐  • Mean     │
│ │   MRI Image  │  • StdDev   │
│ │   256×256    │  • Min/Max  │
│ └──────────────┘             │
│                              │
│ 🔍 Extracted Features (15+)  │
│ ├─ Intensity Stats           │
│ ├─ Structural Features       │
│ └─ Quality Metrics           │
│                              │
│ 📋 Quality Classification    │
│ ├─ Grade: Premium/Standard   │
│ ├─ Score: 70/100            │
│ ├─ Confidence: 80%          │
│ └─ Decision Reasoning        │
│                              │
└──────────────────────────────┘
```

---

## 💾 File Specifications

### Input Formats
| Format | Ext | Status |
|--------|-----|--------|
| PNG | .png | ✅ Best |
| JPEG | .jpg | ✅ Good |
| GIF | .gif | ✅ Works |
| BMP | .bmp | ✅ Works |
| TIFF | .tiff | ✅ Works |

### Processing
```
Input                    Processing              Output
─────────────────────────────────────────────────────────
any.png        →  Validate        →  ✅ OK
               →  Load            →  PIL Image
               →  To Grayscale    →  (if color)
               →  Resize 256×256  →  (if different size)
               →  Normalize 0-1   →  (intensity values)
                                  →  Ready for analysis

Errors:        →  File > 10 MB    →  ❌ File too large
               →  Unknown format  →  ❌ Unsupported
               →  Corrupted file  →  ❌ Can't load
```

---

## 🎯 Sidebar Buttons Reference

### Main Controls
```
[🔄 Generate New Sample]  - Create new synthetic image
                            (generates different one each time)

[Choose an MRI image]     - Upload file picker
                            (select from computer)

[🔄 Reset to Synthetic]   - Back to generation mode
                            (clears uploaded image)

[📦 Process Batch]        - Run batch analysis
                            (synthetic samples only)
```

---

## 🔍 Detection: What Happens to Your Image

```
Your Upload
    ↓
[Validation]  → File format OK? Size < 10MB?
    ↓
[Loading]     → Open with PIL
    ↓
[Convert]     → Make grayscale (if color)
    ↓
[Resize]      → Force to 256×256 pixels
    ↓
[Normalize]   → Scale to 0-1 range
    ↓
[Store]       → Save in session memory
    ↓
[Analyze]     → Extract 15+ features
    ↓
[Classify]    → Assign quality grade
    ↓
[Display]     → Show results & visualizations
```

---

## 📚 Finding Test Images

### Quick Test (< 1 min)
→ Use any grayscale image you have

### Real Medical Data (< 30 min)
→ Download from:
  - **OpenNeuro** (easiest, no registration)
  - **BraTS** (brain tumors, registration needed)
  - **TCIA** (general medical imaging)

### Conversion Help
```bash
# NIFTI → PNG
python3 convert_nifti.py input.nii.gz output.png

# DICOM → PNG
python3 convert_dicom.py input.dcm output.png

# See TEST_MRI_SOURCES.md for full scripts
```

---

## ✨ Feature Highlights

### Synthetic Mode Advantages
- ✅ Instant generation
- ✅ Reproducible (same seed = same image)
- ✅ Control parameters (core, defect)
- ✅ Perfect for testing
- ✅ No external files needed

### Upload Mode Advantages
- ✅ Analyze real medical images
- ✅ Test on actual data
- ✅ Industrial quality control use
- ✅ Scientific imaging analysis
- ✅ Flexible image sources

### Both Modes
- ✅ Same 15+ features extracted
- ✅ Identical classification system
- ✅ Full visualization suite
- ✅ Decision reasoning explained

---

## 🚀 Getting Started (3 Steps)

### Step 1: Generate
```
1. Open http://localhost:8501
2. Click [🔄 Generate New Sample]
3. See synthetic MRI image
```

### Step 2: Analyze
```
1. Explore all 3 tabs
2. See features and classification
3. Click [🔄 Generate] multiple times
4. Watch quality grade change
```

### Step 3: Upload (Optional)
```
1. Get a test image (see TEST_MRI_SOURCES.md)
2. Click [Choose an MRI image]
3. Upload and analyze
4. Compare with synthetic samples
```

---

## 📖 Read Next

1. **IMAGE_UPLOAD_GUIDE.md** - Full feature documentation
2. **TEST_MRI_SOURCES.md** - Where to find real MRI images
3. **QUICKSTART.md** - General app usage
4. **STREAMLIT_README.md** - All UI features

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Upload button doesn't appear | Scroll down in sidebar |
| File rejected | Check format (PNG/JPG) & size (< 10MB) |
| Image looks wrong | Might be RGB, app converts to grayscale |
| "Reset" doesn't work | Refresh browser (Ctrl+R) |
| Same image twice | Features similar, classification may repeat |

---

## 💡 Pro Tips

1. **Generate 5-10 synthetic samples** to see how quality varies
2. **Upload same image twice** to verify reproducibility
3. **Compare synthetic vs real** in the Feature Analysis tab
4. **Adjust thresholds** while viewing to see instant effect
5. **Check "Upload Info"** expander to see original image details

---

**Ready to analyze?** Open http://localhost:8501 now! 🔬📊

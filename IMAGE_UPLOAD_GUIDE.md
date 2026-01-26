# Image Upload Feature - Complete Guide

## 🎉 New Feature: Upload Real MRI Images

The Synthetic MRI Inspector now supports **uploading real MRI scanned images** in addition to generating synthetic samples!

## How to Use

### Option 1: Generate Synthetic Samples (Original)
1. In the sidebar under **"Generate Sample"**:
   - Set the **Seed** value (or keep default 42)
   - Check/uncheck **Force Core** (whether object has internal core)
   - Check/uncheck **Force Defect** (whether object has anomalies)
2. Click **"🔄 Generate New Sample"**
3. See a randomly generated synthetic MRI image

**Advantage**: Quick, reproducible, no external files needed

### Option 2: Upload Your Own MRI Image (New!)
1. In the sidebar under **"Upload Real MRI Image"**:
   - Click **"Choose an MRI image"**
   - Select an image file from your computer
2. The app will:
   - ✅ Validate the file format
   - ✅ Convert to grayscale (if needed)
   - ✅ Resize to 256×256 pixels
   - ✅ Normalize intensity values
3. See your uploaded image analyzed

**Advantage**: Analyze real medical/industrial images

### Switch Between Modes
- **To upload after generating**: Just upload a file - it replaces the synthetic image
- **To go back to synthetic**: Click **"🔄 Reset to Synthetic"**

## Supported Image Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PNG | .png | Recommended, lossless |
| JPEG | .jpg, .jpeg | Common, may lose detail |
| GIF | .gif | Animated GIFs show first frame |
| BMP | .bmp | Windows bitmap |
| TIFF | .tiff | Scientific imaging |

## File Size Limit

- **Maximum**: 10 MB per image
- Most medical scans are much smaller (< 5 MB)

## What Happens to Your Upload

1. **Size**: Automatically resized to 256×256 pixels (standard size)
2. **Color**: Converted to grayscale if color image
3. **Intensity**: Normalized to 0-1 range for analysis
4. **Analysis**: Same 15+ features extracted and classified

## Finding Real MRI Images to Test

### Option A: Use Your Own Medical Images
- If you have access to medical MRI scans
- Ensure you have permission to use them
- Remove any patient identifiers
- Follow HIPAA/GDPR regulations

### Option B: Download Free Public Datasets

**Brain MRI:**
- **BraTS Dataset** - https://www.med.upenn.edu/cbica/brats2020/
  - Free registration required
  - T1, T2, FLAIR weighted scans
  - Thousands of brain tumors

- **OpenNeuro** - https://openneuro.org/
  - No registration for downloads
  - Neuroimaging datasets
  - Free and open science

**Medical Imaging Archives:**
- **The Cancer Imaging Archive (TCIA)** - https://www.cancerimagingarchive.net/
  - Multi-organ imaging
  - Free with registration
  - High-quality clinical scans

- **ADNI** - https://adni.loni.usc.edu/
  - Alzheimer's disease neuroimaging
  - Longitudinal brain MRI data

### Option C: Create a Test Image
If you can't find public datasets:
1. Download any grayscale image (medical or not)
2. Resize to 256×256 pixels using:
   - **Python**: `from PIL import Image; Image.open('img.jpg').resize((256, 256))`
   - **Online tool**: https://imageresizer.com/
3. Convert to grayscale if colored:
   - **Python**: `img.convert('L')`
   - **Online**: https://convert.town/image-to-grayscale

## Example Workflow

### Workflow 1: Test with Synthetic Images
```
1. App loads → Shows synthetic sample (seed 42)
2. Click "Generate New Sample" → See different image
3. Click "Generate New Sample" again → See another variation
4. Watch Classification change between Standard ⚠️ and Premium ✅
```

### Workflow 2: Test with Uploaded Image
```
1. Click "Choose an MRI image" → Select file from computer
2. Image loads and gets resized/normalized
3. See "Uploaded MRI Image: filename.png" title
4. View "Upload Info" expander to see:
   - Original file size
   - Original color mode (RGB, L, etc.)
   - Resized dimensions
5. Analyze features and classification
```

### Workflow 3: Mix Both
```
1. Start with generated sample
2. Upload an image
3. Analyze the uploaded image
4. Click "Reset to Synthetic"
5. Go back to generating samples
```

## What Gets Analyzed

Regardless of image source, the analysis includes:

### 📊 **Image Statistics**
- Mean, Std Dev, Min, Max intensity
- Intensity distribution histogram

### 🔍 **Extracted Features** (15+)
- **Intensity**: mean, std, range
- **Structural**: wall thickness, layers, core detection
- **Symmetry**: horizontal, vertical, overall
- **Quality**: uniformity, anomaly detection

### 📋 **Classification**
- **Quality Grade**: Premium ✅, Standard ⚠️, or Defective ❌
- **Score**: 0-100
- **Confidence**: % certainty
- **Decision Reasoning**: Explains each rule applied

### 📈 **Advanced Analysis**
- Radial density profile (center to edge)
- Feature importance heatmap
- Detailed breakdown by feature category

## Differences: Synthetic vs Uploaded

| Aspect | Synthetic | Uploaded |
|--------|-----------|----------|
| Source | Generated algorithmically | Real image file |
| Reproducibility | Deterministic (same seed = same image) | One-time upload |
| Control | Seed, core, defect flags | None (image as-is) |
| Speed | Instant generation | Resize/normalize needed |
| Use Case | Testing, demos, training | Real analysis |
| Limitations | Artificial appearance | Depends on image quality |

## Batch Processing with Uploads

⚠️ **Note**: Batch processing (Tab 2) currently works with **synthetic samples only**. 

To analyze multiple uploaded images:
1. Upload image 1 → Analyze
2. Reset → Upload image 2 → Analyze
3. Repeat for each image

(Feature for batch uploading may be added in future)

## Tips for Best Results

### For Synthetic Images
- Vary the seed to see different qualities
- Toggle "Force Core" and "Force Defect" to test edge cases
- Generate batches to see quality distribution

### For Uploaded Images
- Use **grayscale or clear contrast** images
- Ensure image shows **cross-sectional view** (not full object)
- **256×256 resolution** or larger (will be resized)
- Medical scans in **PNG/JPG** format work best
- Avoid **very low contrast** images (analysis needs to see structure)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "File too large" | Compress image or choose smaller file (< 10 MB) |
| "Unsupported format" | Convert to PNG/JPG using any image tool |
| "Error loading image" | Ensure file isn't corrupted; try opening in image viewer first |
| "Wrong size after upload" | App auto-resizes to 256×256; this is intentional |
| "Image looks wrong" | Check if original was upside-down or rotated |

## Privacy & Compliance

⚠️ **Important for Medical Images**:
- Only upload images you have permission to use
- Remove patient names and IDs
- Follow local data protection laws:
  - 🇺🇸 HIPAA (US medical data)
  - 🇪🇺 GDPR (EU personal data)
  - Other country-specific regulations
- Never upload to public servers without proper anonymization
- Consider running locally instead of cloud deployment

## Advanced: Analyzing DICOM Medical Scans

If you have `.dcm` (DICOM) medical scan files:

1. **Convert DICOM to PNG/JPG**:
   ```bash
   # Install pydicom and convert
   pip install pydicom pillow
   python3 << 'EOF'
   import pydicom
   from PIL import Image
   import numpy as np
   
   dcm = pydicom.read_file('scan.dcm')
   img = dcm.pixel_array
   img = ((img - img.min()) / (img.max() - img.min()) * 255).astype(np.uint8)
   Image.fromarray(img).save('scan.png')
   EOF
   ```

2. **Upload the PNG to the inspector**

3. **Analyze with full feature extraction**

## What's Next?

### Potential Future Features
- 🔜 Batch upload multiple images
- 🔜 Side-by-side comparison of synthetic vs real
- 🔜 DICOM file support (native .dcm format)
- 🔜 Export analysis reports (PDF)
- 🔜 Preprocessing tools (brightness, contrast adjustment)
- 🔜 Region-of-interest (ROI) selection
- 🔜 Save and compare analyses

## Questions?

1. Check the main **README.md** for project overview
2. See **STREAMLIT_README.md** for UI feature details
3. Review **QUICKSTART.md** for basic usage
4. Check `.github/copilot-instructions.md` for architecture details

---

**Enjoy analyzing real and synthetic MRI images!** 🔬📊

# Testing Image Upload - Sample MRI Sources

## Quick Start: Get a Test Image

Follow one of these methods to get a real MRI image to test the upload feature.

---

## Method 1: Use a Simple Grayscale Image (Fastest)

**No medical knowledge needed!** Use any grayscale image as a test:

### Step 1: Download a sample image
Download this public domain image:
- **Lena.png** - Classic test image (256×256, grayscale)
  - https://en.wikipedia.org/wiki/Lenna
  - Direct link: https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png

### Step 2: Upload to app
1. In Streamlit sidebar: "Choose an MRI image"
2. Select the downloaded image
3. Analyze with the inspector

**Result**: The image will be analyzed as if it were an MRI scan. Not medically meaningful, but great for testing the feature!

---

## Method 2: Download Real Brain MRI (Free, No Registration)

### Option A: OpenNeuro (Recommended)
- **Website**: https://openneuro.org/
- **Features**: 
  - No registration required
  - Real neuroimaging data
  - Free and open science
  
**Steps**:
1. Go to https://openneuro.org/
2. Click "Browse Datasets"
3. Filter: "MRI" + "Brain"
4. Download any dataset
5. Extract `.nii.gz` files
6. Convert to PNG (see below)

### Option B: BraTS Dataset (Brain Tumor Scans)
- **Website**: https://www.med.upenn.edu/cbica/brats2020/
- **Features**:
  - Real tumor imaging
  - Multiple modalities (T1, T2, FLAIR)
  - ~370 patient samples
  
**Steps**:
1. Register at https://www.med.upenn.edu/cbica/brats2020/
2. Download dataset (~60 GB - large!)
3. Files are in `.nii.gz` format (medical format)
4. Convert to PNG (see below)

---

## Method 3: Get From Medical Archives (Quality Data)

### The Cancer Imaging Archive (TCIA)
- **Website**: https://www.cancerimagingarchive.net/
- **Collections**:
  - Lung scans
  - Breast imaging
  - Liver scans
  - And many more
  
**Steps**:
1. Go to https://www.cancerimagingarchive.net/
2. Sign up (free, quick)
3. Browse collections
4. Download images
5. Most are in DICOM format (convert below)

### ADNI - Alzheimer's Dataset
- **Website**: https://adni.loni.usc.edu/
- **Features**: Longitudinal brain MRI (same patients over time)

**Steps**:
1. Register at https://adni.loni.usc.edu/
2. Download brain MRI images
3. Convert from DICOM to PNG (see below)

---

## Converting Medical Formats to PNG

### If you have NIFTI files (.nii, .nii.gz)

```bash
# Install package
pip install nibabel pillow numpy

# Convert script
python3 << 'EOF'
import nibabel as nib
from PIL import Image
import numpy as np

# Load NIFTI file
nifti = nib.load('your_file.nii.gz')
data = nifti.get_fdata()

# Get middle slice (axial view)
mid_slice = data.shape[2] // 2
img_slice = data[:, :, mid_slice]

# Normalize to 0-255
img_norm = ((img_slice - img_slice.min()) / (img_slice.max() - img_slice.min()) * 255).astype(np.uint8)

# Save as PNG
Image.fromarray(img_norm).save('mri_slice.png')
print("Saved: mri_slice.png (256x256)")
EOF
```

### If you have DICOM files (.dcm)

```bash
# Install package
pip install pydicom pillow numpy

# Convert script
python3 << 'EOF'
import pydicom
from PIL import Image
import numpy as np

# Load DICOM file
dcm = pydicom.dcmread('your_file.dcm')
img_data = dcm.pixel_array

# Normalize to 0-255
img_norm = ((img_data - img_data.min()) / (img_data.max() - img_data.min()) * 255).astype(np.uint8)

# Save as PNG
Image.fromarray(img_norm).save('mri_slice.png')
print("Saved: mri_slice.png")
EOF
```

---

## Pre-Made Sample Images (Ready to Use)

We're providing a `sample_mri_images/` directory. You can add images there and reference them.

### To add your own:
1. Download/convert an image to PNG
2. Save to `/sample_mri_images/my_image.png`
3. Use the file picker in the app to select it

---

## Recommended Test Workflow

### 1. **Test with Simple Image** (5 minutes)
- Download Lena.png or similar
- Upload to app
- Verify upload feature works
- ✅ Basic functionality confirmed

### 2. **Test with Real MRI** (30 minutes)
- Download from OpenNeuro or TCIA
- Convert to PNG if needed
- Upload to app
- Compare quality with synthetic images
- ✅ Real-world use case confirmed

### 3. **Compare Synthetic vs Real** (15 minutes)
- Generate a synthetic sample
- Note the quality grade
- Upload a real MRI
- Compare features and classification
- ✅ Difference analysis complete

---

## What to Expect

### Synthetic Images (from app)
- Clean, perfect structure
- Predictable quality grades
- Symmetric and well-defined layers
- "Ideal" internal structure

### Real MRI Images
- More complex patterns
- Varied quality
- Asymmetric regions possible
- Real anatomical variation
- Might show actual pathology

### The Analyzer Should Handle Both
- Extract same 15+ features from both
- Classify both as Premium/Standard/Defective
- Find real anomalies in medical images
- Adapt thresholds for different image types

---

## Troubleshooting Image Download

| Problem | Solution |
|---------|----------|
| Downloaded .zip won't open | Use built-in unzip or Keka (Mac) |
| File is .nii.gz not .nii | Use `gunzip file.nii.gz` in terminal |
| Can't convert DICOM | Check file isn't corrupt; try Horos viewer first |
| File too large | Use only one slice, compress PNG, or split dataset |

---

## Quick Reference: Image Specs

For best results with the inspector:

```
Format:      PNG, JPG, GIF, BMP, TIFF
Size:        256×256 pixels (auto-resized)
Color:       Grayscale (auto-converted)
Contrast:    Medium to high (for feature detection)
Intensity:   0-1 or 0-255 (auto-normalized)
Max file:    10 MB
Content:     Cross-sectional scan view
```

---

## Privacy Reminder

⚠️ If using medical images:
- Only use with permission
- Remove patient identifiers
- Follow HIPAA/GDPR regulations
- Don't share on public servers
- Consider local-only analysis

---

## Next Steps

1. **Pick a download method above** (OpenNeuro recommended - easiest)
2. **Download or convert image to PNG**
3. **Upload to Synthetic MRI Inspector**
4. **Analyze and compare with synthetic results**
5. **Read the feature explanation** in the "About" tab

**Happy analyzing!** 🔬📊

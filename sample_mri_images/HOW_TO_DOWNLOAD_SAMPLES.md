# How to Download Real MRI Scan Images for Sample Testing

This guide walks you through finding and downloading **actual MRI scan images** of fruits, vegetables, eggs, and nuts - the real imagery your app is designed to process.

## 🎯 Quick Start: Academic Datasets with Real MRI Images

Instead of searching Google Images, use these **verified academic sources** that have real MRI scan images:

### 1. IEEE DataPort (Apple MRI Dataset)
- **Link**: https://ieee-dataport.org/documents/inside-defect-detection-and-classification-apple-based-mri-images
- **What**: Apple internal MRI scans showing defects
- **Access**: Free registration required
- **Download**: Direct PNG/JPG images from dataset

### 2. ResearchGate (Multiple Fruit MRI Papers)
- **Link**: https://www.researchgate.net
- **Search for**: "MRI scan apple", "MRI scan egg", "MRI scan potato"
- **Papers with images**:
  - MRI of apples with internal defects
  - MRI of raw eggs showing structure
  - MRI of potatoes
  - **How to access**: Most researchers allow downloading figures as PNG/JPG

### 3. KU Leuven University (Fruit Quality Lab)
- **Link**: https://www.biw.kuleuven.be/biosyst/mebios/postharvest-group/research/fruit-and-vegetable-quality/internal-defects.html
- **What**: Academic research on fruit internal defect detection via MRI
- **Download**: Some images available in research publications

### 4. Wellcome Collection (Free MRI Art/Science Images)
- **Link**: https://wellcomecollection.org
- **Search**: "MRI fruit", "MRI vegetable"
- **Access**: Creative Commons licensed, free to download
- **Quality**: High-resolution medical-grade images

---

## 📁 Complete MRI Image Checklist

These are the **types of real MRI images** you should look for:

### Fruits Folder - Apple MRI Images
```
sample_mri_images/fruits/
├── apple_mri_sagittal.png        (Sagittal view - side profile)
├── apple_mri_axial.png           (Axial/cross-section view)
└── apple_mri_defect.png          (Apple showing internal bruising)
```

**Where to find:**
- IEEE DataPort Apple dataset (direct download)
- ResearchGate search: "apple MRI scan defect"
- Wellcome Collection: "Apple sagittal view MRI"
- Papers by: KU Leuven, Max Planck Institute

### Vegetables Folder - Potato & Tomato MRI
```
sample_mri_images/vegetables/
├── potato_mri_t2weighted.png     (T2-weighted potato scan)
├── tomato_mri_axial.png          (Cross-section view)
└── pepper_mri_proton.png         (Red pepper MRI)
```

**Where to find:**
- ResearchGate: "potato MRI sequences"
- ResearchGate: "pepper MRI proton images"
- Academic papers on vegetable quality inspection

### Nuts Folder - Walnut & Almond MRI
```
sample_mri_images/nuts/
├── walnut_mri_shell.png          (Walnut showing shell structure)
├── almond_mri_kernel.png         (Kernel detail)
└── pecan_mri_quality.png         (Quality inspection scan)
```

**Where to find:**
- ResearchGate: "walnut MRI quality"
- CSIR research on nut inspection
- Agricultural research databases

### Poultry Folder - Egg & Embryo MRI
```
sample_mri_images/poultry/
├── egg_mri_raw.png               (Raw egg showing yolk/white/air cell)
├── embryo_mri_t2weighted.png     (Developing embryo MRI)
└── egg_mri_fertility.png         (Fertile vs non-fertile egg)
```

**Where to find:**
- ResearchGate: "MRI raw egg"
- ResearchGate: "embryonic egg MRI"
- Agricultural research on egg sexing
- Papers on fertility determination via MRI

---

## 📸 Best Sources for Real MRI Images

### Academic Databases (✅ Recommended)
1. **IEEE DataPort**
   - Organized, peer-reviewed MRI datasets
   - Direct downloads of scan images
   - Apple MRI dataset is complete and free
   - URL: https://ieee-dataport.org

2. **ResearchGate**
   - Millions of research papers with images
   - Authors allow figure downloads
   - High-quality medical-grade imagery
   - Search: "MRI apple", "MRI egg", "MRI walnut"
   - URL: https://www.researchgate.net

3. **Wellcome Collection**
   - Medical imaging archives
   - Creative Commons licensed (free to use)
   - High-resolution scans
   - URL: https://wellcomecollection.org

4. **Zenodo (European Research)**
   - Open science repository
   - Many MRI fruit quality studies
   - Free downloads
   - URL: https://zenodo.org (search "MRI fruit")

5. **Directory of Open Access Journals (DOAJ)**
   - Free research papers with MRI figures
   - Agricultural and food science focus
   - URL: https://doaj.org (search "MRI produce")

### How to Extract Images from Research Papers
1. Find paper with MRI images (ResearchGate, Google Scholar)
2. Download the PDF
3. Use PDF extraction tool to save figures as PNG/JPG
4. Crop image to remove labels if needed
5. Resize to ~256×256 pixels (app will auto-resize)

**Advantages:**
- All free to use
- No license restrictions
- High quality images
- Clearly attributed

---

## 🎨 What Real MRI Images Look Like

### Characteristics of Real MRI Scans
✅ **Look for these features:**
- Grayscale or color intensity maps
- Cross-sectional (axial/sagittal) views
- Internal structure clearly visible (not surface only)
- Labeled with "T1" or "T2" weighted indicators
- Show internal density differences (dark/light areas = different tissues)

### Examples of Good MRI Images
- **Apple**: Light core, darker flesh, seed cavities visible
- **Egg**: White (light), yolk (medium), air cell (dark), shell boundary clear
- **Potato**: Consistent gray tones, internal defects show as dark spots
- **Walnut**: Shell (bright), kernel (gray), empty spaces (dark)

### Anatomy of an MRI Scan Image
```
┌─────────────────────────┐
│ Source Label            │  (e.g., "T2-weighted MRI")
│ MMMMMMMMMMMMMMMM        │
│ MMMM   LIGHT   MMMM     │  Light areas = different tissue density
│ MMM   MMMMMM   MMM      │  Dark areas = another density
│ MMM   MMMMMM   MMM      │  Gradients show internal structure
│ MMMM           MMMM     │
│ MMMMMMMMMMMMMMMM        │
│ Scale: 2cm              │  (scale bar often included)
└─────────────────────────┘
```

---

## 📝 Step-by-Step: Download from IEEE DataPort (Easiest)

### For Apple MRI Dataset
1. **Visit**: https://ieee-dataport.org/documents/inside-defect-detection-and-classification-apple-based-mri-images
2. **Register** (free account)
3. **Download** the dataset zip file
4. **Extract** to see PNG/JPG MRI images
5. **Select** 2-3 apple MRI images
6. **Save** to: `/sample_mri_images/fruits/`
7. **Rename**: `apple_mri_1.png`, `apple_mri_2.png`, etc.

### For ResearchGate (Research Papers)
1. Go to https://www.researchgate.net
2. Search: "apple MRI defect detection"
3. Find papers with PNG figure files
4. Click paper → scroll to figures
5. Right-click image → "Save image as"
6. Save to appropriate folder
7. Rename to descriptive name

### For Wellcome Collection (Fine Art MRI)
1. Visit: https://wellcomecollection.org
2. Search: "MRI apple" or "MRI egg"
3. Click image → Download link
4. Usually available as PNG/JPG
5. Save to folder
6. Properly attribute source
   - Navigate to: `synthetic-mri-inspector/sample_mri_images/fruits/`
   - Paste image there

### Batch Download (Using Python Script)

If you want to automate downloading multiple images, I can provide a Python script. Contact me for: `batch_download_samples.py`

### Using Browser Extensions

- **Image Downloader**: Firefox/Chrome extension
- **Batch Download Plus**: Chrome extension
- Allows selecting multiple images to download at once

---

## 📂 File Organization

After downloading, your structure should look like:

## 📂 File Organization After Download

After downloading MRI images, your structure should look like:

```
synthetic-mri-inspector/
├── sample_mri_images/
│   ├── README.md
│   ├── SETUP_GUIDE.md
│   ├── HOW_TO_DOWNLOAD_SAMPLES.md (this file)
│   ├── fruits/
│   │   ├── apple_mri_sagittal.png      (from IEEE DataPort)
│   │   ├── apple_mri_axial.png         (from ResearchGate)
│   │   └── orange_mri_scan.png         (from academic source)
│   ├── vegetables/
│   │   ├── potato_mri_t2weighted.png   (from research paper)
│   │   ├── tomato_mri_cross.png        (from academic DB)
│   │   └── pepper_mri_proton.png       (from journal)
│   ├── nuts/
│   │   ├── walnut_mri_structure.png    (from agricultural research)
│   │   ├── almond_mri_quality.png      (from quality lab)
│   │   └── pecan_mri_kernel.png        (from research)
│   └── poultry/
│       ├── egg_mri_raw.png             (from embryo research)
│       ├── embryo_mri_t2w.png          (from developmental study)
│       └── egg_mri_fertility.png       (from sexing research)
```

---

## 🎯 Testing Your Images

Once you've downloaded images:

1. **Open the app**: http://localhost:8501

2. **Upload test image**:
   - Click "Choose an MRI image" in sidebar
   - Select a downloaded image
   - Should show success: "✅ Image loaded successfully!"

3. **View analysis**:
   - See image displayed
   - Check all metrics calculated
   - Verify classification assigned

4. **Try multiple**:
   - Reset and upload another
   - Compare results
   - Different items show different features

---

## 🔗 Direct Links to MRI Image Resources

### Pre-Curated Academic Sources

**Apple MRI Data:**
- IEEE DataPort: https://ieee-dataport.org/documents/inside-defect-detection-and-classification-apple-based-mri-images

**Apple MRI Papers (with figures):**
- ResearchGate search: https://www.researchgate.net/search?q=apple+MRI+defect

**Egg & Poultry MRI:**
- ResearchGate search: https://www.researchgate.net/search?q=egg+MRI
- Papers on embryo sexing with MRI available

**Potato & Vegetable MRI:**
- ResearchGate: "potato MRI T2 weighted"
- Papers on quality inspection via MRI

**Walnut & Nut MRI:**
- ResearchGate: "walnut MRI quality"
- Agricultural research databases

**General High-Quality Collections:**
- Wellcome Collection: https://wellcomecollection.org
- Zenodo: https://zenodo.org (search "MRI fruit vegetable")
- Google Scholar: https://scholar.google.com (search "MRI produce" and look for PDF links)

---

## ✅ Quick Verification

After saving images, verify they work:

```bash
# Check files exist
ls -la sample_mri_images/fruits/
ls -la sample_mri_images/poultry/
ls -la sample_mri_images/nuts/

# Check file size (should be > 10 KB typically)
du -h sample_mri_images/*/*.png
```

---

## 🎓 Why Real MRI Images are Better

Using **actual MRI scan images** instead of regular photos means:

✅ **More Authentic Testing**
- App processes real MRI data
- Features extract from actual medical imagery
- Quality classification is realistic

✅ **Educational Value**
- Users see what real MRI output looks like
- Demonstrates non-destructive testing in action
- Shows how Orbem.ai actually works

✅ **Improved Feature Extraction**
- Grayscale intensity patterns from real scans
- Internal structure visibility
- Defect/anomaly detection on real data

✅ **Production-Ready Examples**
- Matches Orbem.ai's actual input
- Shows app is designed for professional use
- Demonstrates competence in real domain

---

## 📝 Notes

- Total download time: 10-15 minutes
- Storage needed: ~50-100 MB for 9-12 images
- File format: PNG preferred (auto-converts color to grayscale)
- Sizing: App auto-resizes to 256×256 (any input size works)

---

## Next Steps

1. **Download 3 priority images** (Mango, Egg, Walnut)
2. **Test in app** - Upload one to verify
3. **Download remaining** as time permits
4. **Share folder** - Users can now explore real samples!

---

**Questions?** Check the other guides:
- `README.md` - Image requirements
- `SETUP_GUIDE.md` - Folder structure
- Or refer to main docs: `IMAGE_UPLOAD_GUIDE.md`

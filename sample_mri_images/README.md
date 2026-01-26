# Sample MRI Images for Upload Testing

## About This Directory

This directory is designed to hold **real MRI scanned images** that can be uploaded to the Synthetic MRI Inspector for analysis.

## Image Requirements

The inspector analyzes **grayscale 2D cross-sectional images** representing internal structures. Ideal images should:

- **Format**: PNG, JPG, JPEG, GIF (grayscale or will be converted)
- **Size**: Ideally 256×256 pixels (will be resized if needed)
- **Content**: Cross-sectional view of object with:
  - Outer shell/boundary
  - Internal structure (layers, core, density variations)
  - Optional defects or anomalies

## Real-World Use Cases

### 1. **Medical Imaging** (with permission)
- CT scans (cross-sectional)
- MRI scans (T1/T2 weighted)
- Ultrasound images
- X-ray cross-sections

### 2. **Industrial Quality Control**
- Pipe/tube cross-sections
- Composite material scans
- Weld quality inspection
- Material density analysis

### 3. **Material Science**
- Crystal structure imaging
- Microstructure analysis
- Grain boundary detection
- Phase distribution

### 4. **Biological Specimens**
- Cell cross-sections
- Tissue samples
- Plant stem analysis
- Tumor imaging (with permission)

## How to Add Sample Images

1. **Place image files** in this directory (e.g., `sample1.png`, `brain_scan.jpg`)
2. **Use the Streamlit app's upload feature** to analyze them
3. **The analyzer will:**
   - Convert to grayscale if needed
   - Resize to 256×256 pixels
   - Extract 15+ interpretable features
   - Classify as Premium/Standard/Defective

## Public MRI Datasets (Free to Use)

You can download real MRI images from these sources:

### Brain MRI
- **BraTS Dataset** (Brain Tumor Segmentation)
  - Link: https://www.med.upenn.edu/cbica/brats2020/
  - T1, T2, FLAIR weighted scans
  - Contains tumor samples

- **ADNI** (Alzheimer's Disease Neuroimaging Initiative)
  - Link: https://adni.loni.usc.edu/
  - Longitudinal brain MRI data

### Cardiac MRI
- **Cardiac Atlas Project**
  - Link: http://cardiacatlas.org/
  - Heart chamber imaging

### Prostate MRI
- **PROSTATEx Challenge**
  - Link: https://wiki.cancerimagingarchive.net/
  - Prostate cancer imaging

### General Medical Imaging
- **The Cancer Imaging Archive (TCIA)**
  - Link: https://www.cancerimagingarchive.net/
  - Multi-organ imaging datasets
  - Free with registration

- **OpenNeuro**
  - Link: https://openneuro.org/
  - Neuroimaging datasets
  - fMRI, T1w, T2w scans

## Testing Without Real Images

If you don't have real MRI images:
1. Use the **"Generate Sample" feature** in the app (creates synthetic images)
2. Use the **"Batch Processing"** to analyze multiple synthetic samples
3. The synthetic images are realistic 256×256 grayscale cross-sections

## Format Conversion Tips

If your image is:
- **DICOM format** (.dcm): Use free tools like:
  - Horos (Mac) - https://horosproject.org/
  - DICOM viewer online tools
  
- **Wrong size**: The app will automatically resize to 256×256

- **Color image**: The app will convert to grayscale

## Privacy & Ethics

⚠️ **Important**:
- Only use images where you have permission
- Remove patient identifiers from medical images
- Follow HIPAA/GDPR regulations if using real medical data
- Synthetic images provided are for testing only

## Example Analysis Features

When you upload an image, the inspector analyzes:
- Intensity distribution (mean, std, range)
- Structural features (wall thickness, core detection)
- Symmetry metrics (horizontal, vertical, overall)
- Anomaly detection (size, severity, count)
- Quality score (0-100)
- Classification (Premium/Standard/Defective)

## Questions?

Check the main `README.md` in the project root for more information about the analysis methodology.

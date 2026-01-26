# Sample MRI-Style Images for Testing

This directory contains sample images organized by category that simulate the types of scans Orbem.ai performs.

## Directory Structure

```
sample_mri_images/
├── fruits/
│   ├── apple_cross_section.png
│   ├── mango_cross_section.png
│   └── orange_cross_section.png
├── vegetables/
│   ├── carrot_cross_section.png
│   ├── tomato_cross_section.png
│   └── broccoli_cross_section.png
├── nuts/
│   ├── walnut_cross_section.png
│   ├── almond_cross_section.png
│   └── pecan_cross_section.png
├── poultry/
│   ├── egg_cross_section.png
│   └── chicken_embryo.png
└── README.md
```

## Image Sources

These images are **grayscale cross-sectional scans** simulating MRI/internal structure analysis.

### Fruits (Orbem.ai Use Case)
- **Mango**: Detect ripeness, fiber content, defects
- **Apple**: Monitor internal browning, cell structure
- **Orange**: Check for hollowness, juice content

**Where to find:**
- Google Images: "mango cross section", "apple cross section", "orange slice macro"
- Unsplash: Search "fruit slice" or "fruit cross section"
- Pexels: "food cross section"

### Vegetables (Related)
- **Carrot**: Root vegetable with radial structure
- **Tomato**: Shows seed chambers and internal structure
- **Broccoli**: Stalk and floret cross-sections

**Where to find:**
- Google Images: "carrot cross section", "tomato cross section"
- Food photography sites with macro/cross-section images

### Nuts (Orbem.ai Use Case)
- **Walnut**: Shell and internal structure
- **Almond**: Kernel and shell boundary
- **Pecan**: Internal detail visibility

**Where to find:**
- Google Images: "walnut cross section", "almond cross section"

### Poultry (Orbem.ai Use Case)
- **Egg cross-section**: Yolk, white, shell structure
- **Chicken embryo**: Development stage visualization

**Where to find:**
- Google Images: "egg cross section", "boiled egg cross section"
- Medical/educational imaging databases

## How to Add Images

### Step 1: Find Images
1. Go to Google Images
2. Search: "mango cross section" (or any item above)
3. Use filters: Color, Size, License (prefer free to use)

### Step 2: Download
1. Right-click image → "Save image as"
2. Name it: `item_name_cross_section.png`
3. Save to appropriate subfolder

### Step 3: Verify
1. Check image is grayscale or can be converted
2. Ensure it shows internal structure (cross-sectional view)
3. Size should be ~500×500 pixels or larger (app will resize to 256×256)

## Image Requirements

For best results with the Synthetic MRI Inspector:

- **Format**: PNG, JPG (grayscale preferred)
- **Size**: Any (will auto-resize to 256×256)
- **Color**: Grayscale or color (auto-converted to grayscale)
- **Content**: Cross-sectional or internal view
- **Quality**: Clear, good contrast

## Usage in App

Once images are in this directory, users can:

1. Open Synthetic MRI Inspector at http://localhost:8501
2. Click "Choose an MRI image" in sidebar
3. Select from downloaded samples
4. Analyze with full 15+ feature extraction
5. See quality classification

## Recommended Images to Download

### Priority 1 (Most Important for Orbem.ai Alignment)
- [ ] Mango cross-section (various angles)
- [ ] Apple cross-section (showing internal structure)
- [ ] Walnut cross-section
- [ ] Egg cross-section (whole and cut)

### Priority 2 (Good Examples)
- [ ] Orange slice (macro photography)
- [ ] Carrot cross-section
- [ ] Tomato cross-section
- [ ] Pecan half

### Priority 3 (Optional)
- [ ] Pineapple cross-section
- [ ] Kiwi slice
- [ ] Avocado half
- [ ] Coconut cross-section

## Testing Workflow

1. **Generate synthetic samples** (original feature)
2. **Upload real cross-sections** (new feature)
3. **Compare results**:
   - Synthetic: Perfect structure
   - Real: Natural variations & defects
4. **Analyze patterns**:
   - Internal structure detection
   - Defect identification
   - Quality assessment

## Notes

- Images don't need to be actual MRI scans
- Any cross-sectional or internal view works
- Color images auto-converted to grayscale
- App provides same analysis for all images
- Real food images show more natural variation than synthetic

## Future: Real MRI Data

If you want actual MRI scans of food items:
- Check OpenNeuro for food science datasets
- Look for food engineering research papers
- Search "food quality inspection MRI" academic databases

## Privacy & Attribution

- Respect image licenses when downloading
- Free-to-use sources: Unsplash, Pexels, Pixabay
- Check Google Images license filter
- Include attribution if required by license

---

**Ready to populate this directory?** See the companion guide: `HOW_TO_DOWNLOAD_SAMPLES.md`

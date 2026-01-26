# Copilot Instructions for Synthetic MRI Inspector

## Project Overview

**Synthetic MRI Insight Explorer** is a data-efficient, interpretable quality inspection system that demonstrates feature extraction and rule-based classification without machine learning training. The project simulates MRI-based analysis of internal structures for industrial quality control.

### Core Philosophy
- **Data Efficiency**: Statistical features require minimal samples, no training data
- **Interpretability**: Every classification decision traces to specific structural measurements
- **Actionable Insights**: Clear classifications enable immediate sorting decisions

## Architecture & Data Flow

```
Data Generator → Feature Extractor → Classifier → Visualizer
                      ↓
                  Structured
                  Features Dict
                      ↓
              Rule-Based Decision
```

### Component Responsibilities

| Component | File | Role |
|-----------|------|------|
| **Data Generator** | `src/data_generator.py` | Generates synthetic 2D "MRI" images with controllable internal structures (shell, core, defects) |
| **Feature Extractor** | `src/feature_extractor.py` | Extracts 15+ interpretable features (density, symmetry, anomalies, wall thickness) |
| **Classifier** | `src/classifier.py` | Rule-based decision engine - classifies as Premium/Standard/Defective with reasoning |
| **Visualizer** | `src/visualizer.py` | Creates multi-panel analysis visualizations (original image, metrics, feature importance) |

### Critical Data Structures

**Features Dictionary** (`FeatureExtractor.extract_features()` output):
- Intensity stats: `mean_intensity`, `std_intensity`, `density_range`
- Structural: `estimated_wall_thickness`, `has_core_structure`, `core_intensity`
- Quality indicators: `uniformity_score`, `overall_symmetry`, `anomaly_severity`, `has_anomaly`
- Derived: `radial_profile_mean`, `radial_gradient`

**Classification Dictionary** (`QualityClassifier.classify()` output):
- `quality`: 'Premium', 'Standard', or 'Defective'
- `quality_score`: 0-100 numeric score
- `confidence`: Percentage certainty
- `decision`: Action string
- `reasoning`: List of interpretable decision rules applied

## Critical Developer Patterns

### 1. Feature Extraction Pattern
Features must be **interpretable and independently computable** from the image. New features should:
- Extract one measurement from the image (e.g., wall thickness via edge detection)
- Return a numeric scalar (0-1 preferred for comparability)
- Have a docstring explaining physical meaning
- Be added to the returned dict in `extract_features()` and documented

**Example** (`src/feature_extractor.py:_compute_density_distribution`):
```python
radial_profile = []
for i in range(n_bins):
    r_min = (i / n_bins) * max_dist
    r_max = ((i + 1) / n_bins) * max_dist
    mask = (distances >= r_min) & (distances < r_max)
    radial_profile.append(np.mean(img[mask]))
```

### 2. Rule-Based Classification Pattern
All quality decisions use threshold-based rules in `QualityClassifier.classify()`:
```python
if features['uniformity_score'] < self.thresholds['uniformity_min']:
    quality_score -= 20
    reasoning.append(f"⚠️ Low uniformity: {features['uniformity_score']:.2f}")
```

**Guidelines**:
- Thresholds are stored in `self.thresholds` dict (tunable per domain)
- Each rule produces a score delta (positive or negative)
- Always append readable reasoning strings for transparency
- Penalties are additive; final score is clamped 0-100

### 3. Image Coordinate System
All images are 2D numpy arrays (256x256 default, `image_size` configurable):
- Center is always at `image_size // 2` in both dimensions
- Distances computed using Euclidean: `np.sqrt((x - cx)² + (y - cy)²)`
- Radial analysis: convert 2D coords to distance from center, then bin by radius
- Masks created via boolean indexing: `img[mask] = value`

## Running the Project

### Development Workflow
```bash
# 1. Install dependencies (do this once)
pip install -r requirements.txt

# 2. Run the complete pipeline demo
python demo.py

# 3. Interactive exploration
jupyter notebook notebooks/exploration.ipynb
```

### Key Outputs
- `examples/outputs/comprehensive_analysis.png` - 3x3 grid with image, classification, features
- `examples/outputs/batch_comparison.png` - Quality scores across multiple samples
- `examples/outputs/feature_importance.png` - Heatmap of which features matter most
- `examples/outputs/inspection_report.txt` - Plain-text analysis report

## Common Modification Patterns

### Adding a New Feature
1. Implement method in `FeatureExtractor` following naming `_compute_*` or `_detect_*`
2. Call from `extract_features()` and merge returned dict: `features.update(self._compute_new_feature(img))`
3. Add interpretability helper: implement `print_features()` entry if detailed output needed

### Adjusting Classification Thresholds
Edit `QualityClassifier.__init__()`:
```python
self.thresholds = {
    'uniformity_min': 0.6,  # Tune domain requirements here
    'symmetry_min': 0.65,
    'anomaly_severity_max': 0.02,
    'wall_thickness_min': 0.05,
    'wall_thickness_max': 0.25
}
```

### Adding Classification Rule
In `QualityClassifier.classify()`, follow the pattern:
```python
if <condition on features>:
    quality_score += <penalty>
    reasoning.append(f"<emoji> <explanation>: {value:.2f}")
```

### Extending Visualizations
`MRIVisualizer` methods use `GridSpec` for multi-panel layouts. Add new plots by:
1. Creating new `plot_*` method
2. Using consistent color scheme: `self.colors['Premium']`, etc.
3. Setting title/labels consistently
4. Supporting optional `save_path` parameter

## Dependencies & Versions

```
numpy>=1.20.0       # Array operations, image manipulation
scipy>=1.6.0        # ndimage for morphological operations
scikit-image>=0.18.0 # label(), regionprops() for structure detection
matplotlib>=3.3.0   # Visualization
seaborn>=0.11.0     # Statistical visualization styling
jupyter>=1.0.0      # Interactive notebooks
```

No ML frameworks (sklearn, tensorflow, torch) intentionally used—this demonstrates interpretability without black-box models.

## Testing & Debugging

- **Reproducibility**: Pass `seed` parameter to `SyntheticMRIGenerator.generate_sample()` for deterministic images
- **Feature validation**: Use `FeatureExtractor.print_features()` to inspect extracted values
- **Classification logic**: Use `QualityClassifier.print_classification()` to trace decision rules
- **Visualization inspection**: Check `examples/outputs/*.png` files for visual correctness

## File Navigation Quick Reference

```
src/
  ├── data_generator.py     → Image generation, structural parameters
  ├── feature_extractor.py  → Feature computation (15+ features)
  ├── classifier.py         → Rule-based decisions (thresholds, reasoning)
  ├── visualizer.py         → Multi-panel visualization methods
  └── __init__.py          → Empty, marks src as package

notebooks/
  └── exploration.ipynb    → Complete analysis walkthrough

demo.py                     → Entry point, orchestrates all 4 components

README.md                   → Project philosophy & overview
requirements.txt            → Python dependencies
```

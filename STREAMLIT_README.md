# 🔬 Synthetic MRI Inspector - Streamlit UI

## Overview

An interactive web-based interface for the Synthetic MRI Inspector project. This Streamlit app provides a visual way to explore data generation, feature extraction, classification, and analysis - without needing to run terminal commands or write code.

## Features

### 📊 Single Analysis Tab
- **Generate Custom Samples**: Create synthetic MRI images with specific properties
  - Control random seed for reproducibility
  - Force/disable core structures
  - Force/disable defects
- **View Detailed Features**: See all extracted features with metrics
- **Classification Results**: Get quality grades with confidence scores and reasoning
- **Comprehensive Visualization**: Multi-panel analysis reports

### 📦 Batch Processing Tab
- **Process Multiple Samples**: Generate and analyze 1-20 samples at once
- **Summary Statistics**: View quality distribution and averages
- **Feature Correlations**: See how uniformity and symmetry correlate with quality
- **Data Table**: Export feature data for each sample

### 📈 Feature Analysis Tab
- **Feature Breakdown**: Detailed view of all extracted features
- **Radial Profile**: Visualize intensity from center to edge
- **Feature Importance**: See which features matter most for quality

### ℹ️ About Tab
- **Project Philosophy**: Understand the core concepts
- **How It Works**: Detailed explanation of the pipeline
- **Classification Rules**: Learn the decision logic
- **Real-World Applications**: See industry use cases

### ⚙️ Configuration Sidebar
- **Sample Generation**: Seed, core, and defect controls
- **Batch Processing**: Adjust number of samples
- **Threshold Tuning**: Customize classification thresholds in real-time

## Installation

### Prerequisites
- Python 3.12+
- Virtual environment (recommended)

### Setup

1. **Create and activate virtual environment:**
```bash
cd synthetic-mri-inspector
python3 -m venv venv
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

This installs:
- Core dependencies: numpy, scipy, scikit-image, matplotlib, seaborn
- Jupyter for notebooks
- Streamlit for this web interface
- pandas for data tables

## Running the App

### Start Streamlit Server
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the Streamlit app
streamlit run app.py
```

The app will open automatically in your default browser at `http://localhost:8501`

### Command-Line Options
```bash
# Run with custom port
streamlit run app.py --server.port 8502

# Run in headless mode (no browser auto-open)
streamlit run app.py --logger.level=info --client.showErrorDetails=false

# Run with Streamlit config file
streamlit run app.py --config.toml .streamlit/config.toml
```

## Usage Guide

### Working with Single Samples

1. **Sidebar Configuration**:
   - Set a seed value (e.g., 42) for reproducibility
   - Check "Force Core" to ensure samples have a central structure
   - Check "Force Defect" to test defect detection
   - Click "Generate New Sample"

2. **View Results**:
   - **Single Analysis** tab shows the synthetic image
   - **Image Statistics** section displays intensity metrics
   - **Extracted Features** section shows all 15+ computed features
   - **Quality Classification** section shows the grade and reasoning

3. **Understand Reasoning**:
   - Each classification explains why a grade was assigned
   - Emoji indicators (✓, ⚠️) show which rules passed/failed
   - Metrics are shown alongside decision rules

### Working with Batches

1. **Set Batch Size**:
   - Use the slider in the sidebar to select 1-20 samples
   - Click "Process Batch"

2. **Analyze Results**:
   - See summary statistics (average score, distribution)
   - View quality distribution pie chart
   - Compare scores across all samples
   - Examine feature data in the results table

3. **Explore Correlations**:
   - See how uniformity affects quality scores
   - View symmetry vs. quality scatter plots
   - Understand feature relationships

### Feature Analysis Deep Dive

1. **View Detailed Features**:
   - Intensity statistics (mean, std, range)
   - Structural features (wall thickness, layer count)
   - Quality metrics (uniformity, symmetry, anomalies)

2. **Radial Profile**:
   - Shows intensity from center to outer edge
   - Helps understand internal structure distribution

3. **Feature Importance**:
   - Heatmap visualization of which features are most relevant

### Customizing Thresholds

1. **Access Threshold Controls**:
   - Click "Tune Thresholds" in the sidebar
   - Expands threshold adjustment panel

2. **Adjust Values**:
   - **Min Uniformity**: Controls uniformity requirement (0.0-1.0)
   - **Min Symmetry**: Controls symmetry requirement (0.0-1.0)
   - **Max Anomaly Severity**: Controls defect tolerance (0.0-0.1)

3. **Real-Time Updates**:
   - Changes apply immediately to classifications
   - Re-generate samples to see how thresholds affect grades

## Understanding the Data Flow

```
User Input (Sidebar)
    ↓
Data Generator
    ↓ (Synthetic MRI Image)
Feature Extractor
    ↓ (15+ Features)
Classifier (Rule-Based)
    ↓ (Grade + Reasoning)
Visualizer
    ↓
Interactive Display
```

### Data Structures

**Sample Image**:
- 256×256 pixel grayscale array
- Values 0.0-1.0 (intensity range)
- Simulates cross-section of object with shell, tissue, core

**Features Dictionary**:
- `mean_intensity`, `std_intensity`: Intensity statistics
- `uniformity_score`: Material consistency (0-1)
- `overall_symmetry`: Structural symmetry (0-1)
- `estimated_wall_thickness`: Shell thickness in pixels
- `has_anomaly`: Boolean indicating defects
- `anomaly_severity`: Defect impact (0-1)
- Plus 9+ more features

**Classification Dictionary**:
- `quality`: 'Premium', 'Standard', or 'Defective'
- `quality_score`: 0-100 numeric score
- `confidence`: Confidence percentage
- `decision`: Action to take
- `reasoning`: List of human-readable decision rules

## Tips and Tricks

### Reproducibility
- Use the same seed value to regenerate identical images
- Useful for testing how threshold changes affect results

### Batch Analysis
- Process batches of 10-15 samples for meaningful statistics
- Use batch correlation analysis to understand feature relationships

### Threshold Tuning
- Start with default thresholds
- Gradually adjust to match your requirements
- Lower uniformity/symmetry thresholds to accept more samples
- Increase anomaly tolerance for less strict defect detection

### Export Data
- Feature tables can be copied from the batch processing tab
- Save screenshots of visualizations for reports

## Performance Notes

- **Single Sample**: < 1 second to generate and analyze
- **Batch of 10**: 5-10 seconds
- **Batch of 20**: 10-20 seconds
- **All visualizations**: Generated on-demand, cached when possible

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install streamlit
```

### Port Already in Use
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

### Slow Performance
- Reduce batch size
- Streamlit caches visualizations automatically
- Try running on a machine with more RAM

### Missing Visualizations
- Ensure matplotlib backend is configured (usually automatic)
- Try refreshing the browser page
- Check browser console for JavaScript errors

## Comparing with Command-Line

### Command-Line Demo
```bash
python demo.py
```
- Outputs text to terminal
- Generates PNG files to `examples/outputs/`
- Good for batch automation

### Streamlit Web UI
```bash
streamlit run app.py
```
- Interactive web interface
- Real-time visualization
- Threshold tuning
- Batch processing with instant feedback

## Features Roadmap

Potential future enhancements:
- ☐ Export results to PDF reports
- ☐ Save/load configuration profiles
- ☐ Real image file upload (for real MRI data)
- ☐ Advanced feature engineering controls
- ☐ Historical comparison across runs
- ☐ Multi-user support with session management

## Project Structure

```
synthetic-mri-inspector/
├── app.py                    # This Streamlit interface (600+ lines)
├── demo.py                   # Command-line demo
├── requirements.txt          # Python dependencies
├── src/
│   ├── data_generator.py     # Synthetic image generation
│   ├── feature_extractor.py  # Feature computation (15+ features)
│   ├── classifier.py         # Rule-based classification
│   └── visualizer.py         # Matplotlib visualizations
├── notebooks/
│   └── exploration.ipynb     # Jupyter notebook guide
└── examples/
    └── outputs/              # Generated results
```

## Related Files

- **Copilot Instructions**: `.github/copilot-instructions.md`
  - Guidance for AI agents working in the codebase
  - Architecture patterns and data structures

- **Project README**: `README.md`
  - Project philosophy and motivation
  - Installation and usage

- **Setup Guide**: `setup_guide.md`
  - Initial project setup instructions

## Support

For issues or questions:
1. Check the "About" tab in the app for conceptual explanations
2. Review the Copilot Instructions for architectural details
3. Check source code comments for implementation details
4. Run `demo.py` to verify core functionality works

## License

MIT License - See LICENSE file for details

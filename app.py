"""
Streamlit UI for Synthetic MRI Inspector
Interactive visualization and analysis of MRI quality inspection
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
sys.path.append('src')

from data_generator import SyntheticMRIGenerator
from feature_extractor import FeatureExtractor
from classifier import QualityClassifier
from visualizer import MRIVisualizer
from image_upload_handler import ImageUploadHandler

# Page configuration
st.set_page_config(
    page_title="Synthetic MRI Inspector",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .premium-badge {
        background-color: #2ecc71;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .standard-badge {
        background-color: #f39c12;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
    .defective-badge {
        background-color: #e74c3c;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generator' not in st.session_state:
    st.session_state.generator = SyntheticMRIGenerator(image_size=256)
    st.session_state.extractor = FeatureExtractor()
    st.session_state.classifier = QualityClassifier()
    st.session_state.visualizer = MRIVisualizer()

# Title and description
st.title("🔬 Synthetic MRI Inspector")
st.markdown("""
**Non-invasive internal structure analysis** with interpretable, rule-based quality classification.
- 📊 Data-efficient (no training required)
- 🔍 Interpretable decisions (explainable features)
- ⚡ Real-time analysis and visualization
""")

st.divider()

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")

# Sample generation options
st.sidebar.subheader("Generate Sample")
col1, col2 = st.sidebar.columns(2)
with col1:
    seed_value = st.number_input("Seed", value=42, step=1)
with col2:
    force_core = st.checkbox("Force Core", value=True)

force_defect = st.sidebar.checkbox("Force Defect", value=False)

if st.sidebar.button("🔄 Generate New Sample", use_container_width=True):
    # Use a counter to trigger regeneration
    if 'generation_counter' not in st.session_state:
        st.session_state.generation_counter = 0
    st.session_state.generation_counter += 1

st.sidebar.divider()

# Image upload options
st.sidebar.subheader("Upload Real MRI Image")
st.sidebar.write("*or use a real scanned image*")

uploaded_file = st.sidebar.file_uploader(
    "Choose an MRI image",
    type=["png", "jpg", "jpeg", "gif", "bmp", "tiff"],
    help="Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF\nMax size: 10 MB"
)

if uploaded_file is not None:
    # Validate and load the uploaded image
    is_valid, validation_msg = ImageUploadHandler.validate_file(uploaded_file)
    
    if is_valid:
        try:
            img_uploaded, upload_metadata = ImageUploadHandler.load_and_preprocess(uploaded_file)
            st.session_state.current_img = img_uploaded
            st.session_state.current_metadata = upload_metadata
            st.session_state.use_uploaded = True
            st.sidebar.success("✅ Image loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading image: {str(e)}")
    else:
        st.sidebar.error(f"❌ {validation_msg}")

if st.sidebar.button("🔄 Reset to Synthetic", use_container_width=True):
    st.session_state.use_uploaded = False
    st.sidebar.success("Reset to synthetic generation")

st.sidebar.divider()

# Batch processing options
st.sidebar.subheader("Batch Processing")
num_samples = st.sidebar.slider("Number of Samples", 1, 20, 5)
if st.sidebar.button("📦 Process Batch", use_container_width=True):
    st.session_state.process_batch = True
    st.session_state.batch_size = num_samples

st.sidebar.divider()

# Classification thresholds
st.sidebar.subheader("Classification Thresholds")
with st.sidebar.expander("Tune Thresholds", expanded=False):
    uniformity_min = st.slider(
        "Min Uniformity", 
        0.0, 1.0, 
        st.session_state.classifier.thresholds['uniformity_min'],
        0.05
    )
    symmetry_min = st.slider(
        "Min Symmetry",
        0.0, 1.0,
        st.session_state.classifier.thresholds['symmetry_min'],
        0.05
    )
    anomaly_max = st.slider(
        "Max Anomaly Severity",
        0.0, 0.1,
        st.session_state.classifier.thresholds['anomaly_severity_max'],
        0.01
    )
    
    # Update thresholds
    st.session_state.classifier.thresholds['uniformity_min'] = uniformity_min
    st.session_state.classifier.thresholds['symmetry_min'] = symmetry_min
    st.session_state.classifier.thresholds['anomaly_severity_max'] = anomaly_max

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📊 Single Analysis", "📦 Batch Processing", "📈 Feature Analysis", "ℹ️ About"])

# ===== TAB 1: Single Analysis =====
with tab1:
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        # Determine title based on image source
        if 'use_uploaded' in st.session_state and st.session_state.use_uploaded:
            image_title = f"Uploaded MRI Image: {st.session_state.current_metadata.get('filename', 'Unknown')}"
        else:
            image_title = "Synthetic MRI Image"
        
        st.subheader(image_title)
        
        # Generate or use uploaded sample
        if 'use_uploaded' not in st.session_state or not st.session_state.use_uploaded:
            # Synthetic generation
            if 'generation_counter' not in st.session_state:
                st.session_state.generation_counter = 0
            
            # Use counter as part of seed to ensure new image each time button is clicked
            generation_seed = seed_value + st.session_state.generation_counter
            
            img, metadata = st.session_state.generator.generate_sample(
                seed=generation_seed,
                has_core=force_core,
                has_defect=force_defect
            )
            st.session_state.current_img = img
            st.session_state.current_metadata = metadata
        else:
            # Use uploaded image
            img = st.session_state.current_img
            metadata = st.session_state.current_metadata
        
        # Display image
        fig_img, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(img, cmap='gray')
        ax.set_title('MRI Cross-Section', fontweight='bold', fontsize=14)
        ax.axis('off')
        st.pyplot(fig_img, use_container_width=True)
        plt.close(fig_img)
    
    with col2:
        st.subheader("Image Statistics")
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Mean Intensity", f"{img.mean():.3f}")
            st.metric("Min Intensity", f"{img.min():.3f}")
        with col_stat2:
            st.metric("Std Dev", f"{img.std():.3f}")
            st.metric("Max Intensity", f"{img.max():.3f}")
        
        # Show metadata if uploaded
        if 'use_uploaded' in st.session_state and st.session_state.use_uploaded:
            st.divider()
            st.subheader("Upload Info")
            with st.expander("📋 View Details"):
                st.write(f"**Filename:** {metadata.get('filename', 'Unknown')}")
                st.write(f"**Original Size:** {metadata.get('original_size', 'Unknown')}")
                st.write(f"**Original Mode:** {metadata.get('original_mode', 'Unknown')}")
                st.write(f"**Resized To:** {metadata.get('resized_to', '256×256')}")
        
        st.divider()
        st.subheader("Intensity Distribution")
        fig_hist, ax = plt.subplots(figsize=(6, 4))
        ax.hist(img.flatten(), bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Intensity Value')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        st.pyplot(fig_hist, use_container_width=True)
        plt.close(fig_hist)
    
    st.divider()
    
    # Feature extraction
    st.subheader("🔍 Extracted Features")
    features = st.session_state.extractor.extract_features(img)
    
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    
    with col_feat1:
        st.metric("Uniformity Score", f"{features['uniformity_score']:.3f}", 
                 delta=None if features['uniformity_score'] >= 0.6 else "Low")
        st.metric("Overall Symmetry", f"{features['overall_symmetry']:.3f}")
        st.metric("Radial Profile Mean", f"{features['radial_profile_mean']:.3f}")
    
    with col_feat2:
        st.metric("Density Range", f"{features['density_range']:.3f}")
        st.metric("Wall Thickness", f"{features['estimated_wall_thickness']:.1f}px")
        st.metric("Has Core", "Yes" if features['has_core_structure'] else "No")
    
    with col_feat3:
        st.metric("Has Anomaly", "Yes" if features['has_anomaly'] else "No", 
                 delta="⚠️" if features['has_anomaly'] else "✓")
        st.metric("Anomaly Severity", f"{features['anomaly_severity']:.3f}")
        st.metric("Radial Gradient", f"{features['radial_gradient']:.3f}")
    
    st.divider()
    
    # Classification
    st.subheader("📋 Quality Classification")
    classification = st.session_state.classifier.classify(features)
    
    quality = classification['quality']
    score = classification['quality_score']
    confidence = classification['confidence']
    
    # Quality badge
    col_quality1, col_quality2 = st.columns([1, 2])
    
    with col_quality1:
        if quality == 'Premium':
            st.markdown('<div class="premium-badge">✅ PREMIUM</div>', unsafe_allow_html=True)
            color_progress = "#2ecc71"
        elif quality == 'Standard':
            st.markdown('<div class="standard-badge">⚠️ STANDARD</div>', unsafe_allow_html=True)
            color_progress = "#f39c12"
        else:
            st.markdown('<div class="defective-badge">❌ DEFECTIVE</div>', unsafe_allow_html=True)
            color_progress = "#e74c3c"
    
    with col_quality2:
        st.metric("Quality Score", f"{score:.0f}/100")
        st.metric("Confidence", f"{confidence:.0f}%")
    
    # Score visualization
    fig_score, ax = plt.subplots(figsize=(10, 2))
    ax.barh([0], [score], color=color_progress, height=0.5)
    ax.axvline(x=85, color='green', linestyle='--', linewidth=2, label='Premium (85+)')
    ax.axvline(x=60, color='orange', linestyle='--', linewidth=2, label='Standard (60+)')
    ax.set_xlim(0, 100)
    ax.set_ylim(-1, 1)
    ax.set_xlabel('Quality Score', fontweight='bold')
    ax.set_title('Score Distribution', fontweight='bold')
    ax.legend(loc='lower right', fontsize=8)
    ax.set_yticks([])
    st.pyplot(fig_score, use_container_width=True)
    plt.close(fig_score)
    
    st.divider()
    
    # Decision reasoning
    st.subheader("📝 Decision Reasoning")
    decision_col1, decision_col2 = st.columns([1, 2])
    
    with decision_col1:
        st.write(f"**Action**: {classification['decision']}")
    
    with decision_col2:
        st.write("**Reasoning Steps**:")
        for i, reason in enumerate(classification['reasoning'], 1):
            st.write(f"{i}. {reason}")
    
    st.divider()
    
    # Comprehensive visualization
    st.subheader("🎨 Comprehensive Analysis")
    fig = st.session_state.visualizer.plot_comprehensive_analysis(img, features, classification)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ===== TAB 2: Batch Processing =====
with tab2:
    st.subheader("📦 Batch Processing")
    
    if 'process_batch' not in st.session_state:
        st.session_state.process_batch = False
    
    if st.session_state.process_batch or st.button("Generate Batch Samples", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        images = []
        all_features = []
        all_classifications = []
        
        for i in range(num_samples):
            status_text.text(f"Processing sample {i+1}/{num_samples}...")
            img, _ = st.session_state.generator.generate_sample(seed=i*10)
            features = st.session_state.extractor.extract_features(img)
            classification = st.session_state.classifier.classify(features)
            
            images.append(img)
            all_features.append(features)
            all_classifications.append(classification)
            
            progress_bar.progress((i + 1) / num_samples)
        
        status_text.text(f"✅ Processed {num_samples} samples!")
        st.session_state.process_batch = False
        
        # Store in session
        st.session_state.batch_images = images
        st.session_state.batch_features = all_features
        st.session_state.batch_classifications = all_classifications
    
    # Display batch results if available
    if 'batch_classifications' in st.session_state:
        batch_classes = st.session_state.batch_classifications
        batch_features = st.session_state.batch_features
        
        # Summary statistics
        st.subheader("Summary Statistics")
        quality_counts = {}
        total_score = 0
        
        for clf in batch_classes:
            quality = clf['quality']
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            total_score += clf['quality_score']
        
        col_summary1, col_summary2, col_summary3, col_summary4 = st.columns(4)
        
        with col_summary1:
            st.metric("Total Samples", len(batch_classes))
        
        with col_summary2:
            st.metric("Average Score", f"{total_score/len(batch_classes):.1f}/100")
        
        with col_summary3:
            st.metric("Premium", f"{quality_counts.get('Premium', 0)}")
        
        with col_summary4:
            st.metric("Defective", f"{quality_counts.get('Defective', 0)}")
        
        st.divider()
        
        # Batch comparison visualization
        st.subheader("Quality Distribution")
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            # Bar chart
            fig_bar, ax = plt.subplots(figsize=(10, 5))
            scores = [c['quality_score'] for c in batch_classes]
            colors_bar = ['#2ecc71' if c['quality'] == 'Premium' else '#f39c12' if c['quality'] == 'Standard' else '#e74c3c' 
                         for c in batch_classes]
            
            bars = ax.bar(range(len(scores)), scores, color=colors_bar, alpha=0.7, edgecolor='black')
            ax.axhline(y=85, color='green', linestyle='--', linewidth=2, label='Premium')
            ax.axhline(y=60, color='orange', linestyle='--', linewidth=2, label='Standard')
            ax.set_xlabel('Sample', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            ax.set_title('Quality Scores Across Batch', fontweight='bold')
            ax.set_ylim(0, 105)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add labels
            for bar, score in zip(bars, scores):
                ax.text(bar.get_x() + bar.get_width()/2, score + 2, f'{score:.0f}',
                       ha='center', fontsize=9, fontweight='bold')
            
            st.pyplot(fig_bar, use_container_width=True)
            plt.close(fig_bar)
        
        with col_viz2:
            # Pie chart
            fig_pie, ax = plt.subplots(figsize=(8, 6))
            colors_pie = {'Premium': '#2ecc71', 'Standard': '#f39c12', 'Defective': '#e74c3c'}
            pie_colors = [colors_pie.get(k, '#95a5a6') for k in quality_counts.keys()]
            
            wedges, texts, autotexts = ax.pie(
                quality_counts.values(), 
                labels=quality_counts.keys(),
                autopct='%1.1f%%',
                colors=pie_colors,
                startangle=90,
                textprops={'fontsize': 11, 'fontweight': 'bold'}
            )
            ax.set_title('Quality Distribution', fontweight='bold', fontsize=14)
            
            st.pyplot(fig_pie, use_container_width=True)
            plt.close(fig_pie)
        
        st.divider()
        
        # Feature statistics table
        st.subheader("Feature Statistics")
        feature_stats = {
            'Sample': [f'Sample {i+1}' for i in range(len(batch_classes))],
            'Quality': [c['quality'] for c in batch_classes],
            'Score': [f"{c['quality_score']:.0f}" for c in batch_classes],
            'Uniformity': [f"{f['uniformity_score']:.3f}" for f in batch_features],
            'Symmetry': [f"{f['overall_symmetry']:.3f}" for f in batch_features],
            'Wall Thickness': [f"{f['estimated_wall_thickness']:.1f}" for f in batch_features],
            'Has Anomaly': ['Yes' if f['has_anomaly'] else 'No' for f in batch_features],
        }
        
        df = pd.DataFrame(feature_stats)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # Correlation analysis
        st.subheader("Feature Correlations")
        uniformity = np.array([f['uniformity_score'] for f in batch_features])
        symmetry = np.array([f['overall_symmetry'] for f in batch_features])
        scores = np.array([c['quality_score'] for c in batch_classes])
        
        corr_uniformity = np.corrcoef(uniformity, scores)[0, 1]
        corr_symmetry = np.corrcoef(symmetry, scores)[0, 1]
        
        col_corr1, col_corr2 = st.columns(2)
        with col_corr1:
            st.metric("Uniformity ↔ Quality", f"{corr_uniformity:.3f}")
        with col_corr2:
            st.metric("Symmetry ↔ Quality", f"{corr_symmetry:.3f}")
        
        # Scatter plots
        col_scatter1, col_scatter2 = st.columns(2)
        
        with col_scatter1:
            fig_scatter1, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(uniformity, scores, s=150, alpha=0.6, c=scores, cmap='RdYlGn', edgecolors='black')
            ax.set_xlabel('Uniformity Score', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            ax.set_title('Uniformity vs Quality', fontweight='bold')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig_scatter1, use_container_width=True)
            plt.close(fig_scatter1)
        
        with col_scatter2:
            fig_scatter2, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(symmetry, scores, s=150, alpha=0.6, c=scores, cmap='RdYlGn', edgecolors='black')
            ax.set_xlabel('Symmetry Score', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            ax.set_title('Symmetry vs Quality', fontweight='bold')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig_scatter2, use_container_width=True)
            plt.close(fig_scatter2)

# ===== TAB 3: Feature Analysis =====
with tab3:
    st.subheader("📈 Feature Deep Dive")
    
    if 'current_img' in st.session_state:
        img = st.session_state.current_img
        features = st.session_state.extractor.extract_features(img)
        
        st.write("Detailed feature breakdown for the current sample:")
        
        col_features1, col_features2, col_features3 = st.columns(3)
        
        with col_features1:
            st.write("**Intensity Statistics**")
            st.write(f"- Mean: {features['mean_intensity']:.3f}")
            st.write(f"- Std Dev: {features['std_intensity']:.3f}")
            st.write(f"- Min: {features['min_intensity']:.3f}")
            st.write(f"- Max: {features['max_intensity']:.3f}")
            st.write(f"- Density Range: {features['density_range']:.3f}")
        
        with col_features2:
            st.write("**Structural Features**")
            st.write(f"- Wall Thickness: {features['estimated_wall_thickness']:.3f}")
            st.write(f"- Layers Detected: {features['n_distinct_layers']}")
            st.write(f"- Has Core: {'Yes' if features['has_core_structure'] else 'No'}")
            st.write(f"- Core Intensity: {features['core_intensity']:.3f}")
            st.write(f"- Radial Gradient: {features['radial_gradient']:.3f}")
        
        with col_features3:
            st.write("**Quality Metrics**")
            st.write(f"- Uniformity: {features['uniformity_score']:.3f}")
            st.write(f"- H Symmetry: {features['horizontal_symmetry']:.3f}")
            st.write(f"- V Symmetry: {features['vertical_symmetry']:.3f}")
            st.write(f"- Overall Symmetry: {features['overall_symmetry']:.3f}")
            st.write(f"- Anomaly Severity: {features['anomaly_severity']:.3f}")
        
        st.divider()
        
        # Radial profile visualization
        st.subheader("Radial Density Profile")
        
        center = 128
        y, x = np.ogrid[:256, :256]
        distances = np.sqrt((x - center)**2 + (y - center)**2)
        
        max_dist = np.max(distances)
        n_bins = 20
        radial_profile = []
        bin_centers = []
        
        for i in range(n_bins):
            r_min = (i / n_bins) * max_dist
            r_max = ((i + 1) / n_bins) * max_dist
            mask = (distances >= r_min) & (distances < r_max)
            if mask.sum() > 0:
                radial_profile.append(np.mean(img[mask]))
            else:
                radial_profile.append(0)
            bin_centers.append((r_min + r_max) / 2)
        
        fig_radial, ax = plt.subplots(figsize=(12, 5))
        ax.plot(bin_centers, radial_profile, linewidth=3, marker='o', markersize=8, color='steelblue')
        ax.fill_between(bin_centers, radial_profile, alpha=0.3)
        ax.set_xlabel('Distance from Center (pixels)', fontweight='bold')
        ax.set_ylabel('Mean Intensity', fontweight='bold')
        ax.set_title('Radial Density Profile', fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig_radial, use_container_width=True)
        plt.close(fig_radial)
        
        st.divider()
        
        # Feature importance heatmap
        st.subheader("Feature Importance")
        fig = st.session_state.visualizer.plot_feature_importance(features)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    else:
        st.info("Generate a sample first in the 'Single Analysis' tab to see feature analysis.")

# ===== TAB 4: About =====
with tab4:
    st.subheader("About Synthetic MRI Inspector")
    
    st.markdown("""
    ### Project Philosophy
    
    **Synthetic MRI Insight Explorer** demonstrates a data-efficient, interpretable approach to quality inspection:
    
    - 📊 **Data Efficient**: No training data needed - uses statistical features
    - 🔍 **Interpretable**: Every decision traces to measurable structural features
    - ⚡ **Actionable**: Clear classifications enable immediate sorting decisions
    - 🎯 **Transparent**: All reasoning is human-readable and auditable
    
    ### How It Works
    
    **4-Component Pipeline**:
    1. **Data Generator** → Creates synthetic 2D "MRI-like" images with internal structures
    2. **Feature Extractor** → Computes 15+ interpretable features (density, symmetry, anomalies)
    3. **Classifier** → Rule-based decision engine (Premium/Standard/Defective)
    4. **Visualizer** → Professional multi-panel analysis reports
    
    ### Key Features Explained
    
    **Uniformity Score**
    - Measures consistency of material throughout the sample
    - Range: 0 (very inconsistent) to 1 (perfectly uniform)
    - Threshold: Must be ≥ 0.60 for Premium
    
    **Symmetry Score**
    - Evaluates horizontal and vertical structural symmetry
    - Indicates proper internal structure development
    - Threshold: Must be ≥ 0.65 for Premium
    
    **Wall Thickness**
    - Measures outer shell thickness (in pixels)
    - Too thin (< 0.05): Structural weakness
    - Too thick (> 0.25): Material waste
    
    **Anomaly Detection**
    - Identifies defects or irregularities
    - Severity score indicates impact on quality
    - Severity > 0.02 automatically reduces grade
    
    ### Classification Rules
    
    Samples start with a base score of 100 and are adjusted by rules:
    
    | Condition | Penalty | Impact |
    |-----------|---------|--------|
    | Significant anomaly detected | -50 | Critical defect |
    | Low uniformity | -20 | Material inconsistency |
    | Asymmetric structure | -15 | Shape issue |
    | Wall too thin/thick | -10/15 | Structural problem |
    | Well-formed core | +5 | Bonus for certain products |
    
    **Final Grades**:
    - ✅ **Premium**: Score ≥ 85 (Market-ready, top quality)
    - ⚠️ **Standard**: Score ≥ 60 (Acceptable, secondary processing)
    - ❌ **Defective**: Score < 60 (Reject, requires sorting)
    
    ### Real-World Applications
    
    This approach applies to agricultural and food processing industries:
    - 🍎 Fruit/vegetable quality inspection
    - 🥔 Crop internal structure analysis
    - 🍊 Cross-sectional defect detection
    - 📦 Rapid quality sorting without ML training
    
    ### Advantages Over Deep Learning
    
    ✅ No training data required  
    ✅ Immediate interpretability  
    ✅ Fast inference (no neural network)  
    ✅ Easy to customize per product  
    ✅ Auditable for compliance  
    ✅ Domain experts can validate rules  
    
    ### Technical Stack
    
    - **Python 3.12**
    - **NumPy** - Numerical computations
    - **SciPy** - Advanced signal processing
    - **Scikit-Image** - Image analysis (edge detection, morphology)
    - **Matplotlib/Seaborn** - Visualization
    - **Streamlit** - Interactive web UI
    
    ### Project Files
    
    ```
    src/
    ├── data_generator.py     # Synthetic MRI generation
    ├── feature_extractor.py  # Feature computation
    ├── classifier.py         # Rule-based classification
    └── visualizer.py         # Professional visualizations
    
    app.py                     # This Streamlit interface
    demo.py                    # Command-line demo
    ```
    """)
    
    st.divider()
    
    st.subheader("How to Use This Interface")
    
    st.markdown("""
    ### 📊 Single Analysis Tab
    - Generate custom samples with specific properties
    - View detailed feature extraction results
    - See classification reasoning
    - Explore comprehensive multi-panel visualizations
    
    ### 📦 Batch Processing Tab
    - Process multiple samples at once
    - Compare quality distribution
    - Analyze feature correlations
    - Generate summary statistics
    
    ### 📈 Feature Analysis Tab
    - Deep dive into individual features
    - View radial density profiles
    - Understand feature importance
    - Explore feature-quality relationships
    
    ### ⚙️ Configuration
    Use the sidebar to:
    - Adjust random seed for reproducibility
    - Force core or defect features
    - Tune classification thresholds
    - Configure batch size
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>
    <p>Synthetic MRI Inspector • Data-Efficient Quality Inspection</p>
    <p>Python 3.12 | NumPy | SciPy | Scikit-Image | Streamlit</p>
</div>
""", unsafe_allow_html=True)

"""
Streamlit UI for Synthetic MRI Inspector
Interactive visualization and analysis of MRI quality inspection
"""
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import io
import os
import uuid
import zipfile
from pathlib import Path

sys.path.append('src')

from data_generator import SyntheticMRIGenerator
from feature_extractor import FeatureExtractor
from classifier import QualityClassifier
from visualizer import MRIVisualizer
from image_upload_handler import ImageUploadHandler
from report_generator import ReportGenerator, BatchReportGenerator

# Agentic modules (Upgrade 1, 2, 3)
from quality_control_agent import QualityControlAgent, create_agent, AgentState, ConfidenceLevel
from tool_registry import ToolRegistry, get_default_registry, ToolCategory
from llm_reasoning import LLMReasoningLayer, create_reasoning_layer, LLMProvider

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

# Ensure outputs folders exist (server-side save option)
OUTPUTS_DIR = Path.cwd() / "outputs"
REPORTS_DIR = OUTPUTS_DIR / "reports"
IMAGES_DIR = OUTPUTS_DIR / "images"
ZIP_DIR = OUTPUTS_DIR / "archives"

for d in (OUTPUTS_DIR, REPORTS_DIR, IMAGES_DIR, ZIP_DIR):
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        # If running in an environment without write permissions, continue silently
        pass

# Export helper functions and global export settings (sidebar)
def _build_export_filename(suffix: str, ext: str, prefix: str = None, append_ts: bool = True, append_uuid_flag: bool = True) -> str:
    if prefix is None:
        prefix = f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}"
    parts = [prefix]
    if suffix:
        parts.append(suffix)
    if append_ts:
        parts.append(pd.Timestamp.now().strftime('%Y%m%d_%H%M%S'))
    if append_uuid_flag:
        parts.append(str(uuid.uuid4())[:8])
    return f"{'_'.join(parts)}.{ext}"

def _save_or_buffer(data, filename: str, folder: Path, is_text: bool = False, save_mode_key: str = 'export_save_mode'):
    """Save data to outputs folder if save mode is server, otherwise return a BytesIO buffer for download.
    Returns a tuple ('saved', path) or ('buffer', BytesIO).
    """
    save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
    try:
        if save_mode == 'Save on server (outputs/)':
            target = folder / filename
            if is_text:
                target.write_text(data, encoding='utf-8')
            else:
                with open(target, 'wb') as f:
                    f.write(data)
            return ('saved', str(target))
        else:
            if is_text:
                buf = io.BytesIO()
                buf.write(data.encode('utf-8'))
                buf.seek(0)
                return ('buffer', buf)
            else:
                return ('buffer', io.BytesIO(data))
    except Exception as e:
        return ('error', str(e))

def _get_batch_export_params():
    """Helper to get consistent batch export parameters. Reduces code duplication."""
    prefix = st.session_state.get('batch_prefix', f"mri_batch_{pd.Timestamp.now().strftime('%Y%m%d')}")
    append_ts = st.session_state.get('batch_append_ts', True)
    append_uuid = st.session_state.get('batch_append_uuid', True)
    save_mode = st.session_state.get('batch_save_mode', 'Download (browser)')
    return prefix, append_ts, append_uuid, save_mode

def _download_batch_viz(buffer_obj, suffix: str, label: str, key: str):
    """Helper to create download button for batch visualizations with consistent params."""
    prefix, append_ts, append_uuid, save_mode = _get_batch_export_params()
    fname = _build_export_filename(suffix, 'png', prefix=prefix, append_ts=append_ts, append_uuid_flag=append_uuid)
    
    if save_mode == "Save on server (outputs/)":
        try:
            target = IMAGES_DIR / fname
            with open(target, 'wb') as f:
                f.write(buffer_obj.getvalue())
            st.download_button(label=label, data=buffer_obj, file_name=fname, mime='image/png', use_container_width=True, key=key)
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.download_button(label=label, data=buffer_obj, file_name=fname, mime='image/png', use_container_width=True, key=key)

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

# Export options in sidebar (global controls for filenames and save mode)
with st.sidebar.expander("Export Options", expanded=True):
    st.write("Configure default export behavior for downloads and server saves")
    st.text_input("Filename prefix", value=f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}", key='export_prefix')
    st.selectbox("Save mode", ["Download (browser)", "Save on server (outputs/)"] , key='export_save_mode')
    st.checkbox("Append timestamp to filenames", value=True, key='export_append_ts')
    st.checkbox("Append UUID to filenames", value=True, key='export_append_uuid')
    st.checkbox("Include upload metadata in exported reports", value=True, key='export_include_metadata')


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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Single Analysis", "🤖 Agentic Inspection", "📦 Batch Processing", "📈 Feature Analysis", "ℹ️ About"])

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
        
        # Download button for MRI image
        fig_img_dl, ax = plt.subplots(figsize=(8, 8))
        ax.imshow(img, cmap='gray')
        ax.set_title('MRI Cross-Section', fontweight='bold', fontsize=14)
        ax.axis('off')
        buf_img_dl = io.BytesIO()
        fig_img_dl.savefig(buf_img_dl, format='png', dpi=300, bbox_inches='tight')
        buf_img_dl.seek(0)
        plt.close(fig_img_dl)
        
        filename_prefix = st.session_state.get('export_prefix', f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}")
        append_timestamp = st.session_state.get('export_append_ts', True)
        append_uuid = st.session_state.get('export_append_uuid', True)
        fname_img = _build_export_filename('_mri_image', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
        
        col_img_dl1, col_img_dl2 = st.columns(2)
        with col_img_dl1:
            if save_mode == "Save on server (outputs/)":
                target = IMAGES_DIR / fname_img
                try:
                    with open(target, 'wb') as f:
                        f.write(buf_img_dl.getvalue())
                    st.download_button(label="📥 Save MRI Image", data=buf_img_dl, file_name=fname_img, mime='image/png', use_container_width=True, key="mri_img_dl")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.download_button(label="📥 Save MRI Image", data=buf_img_dl, file_name=fname_img, mime='image/png', use_container_width=True, key="mri_img_dl")
    
    with col2:
        st.subheader("📊 Image Statistics")
        
        col_stat1, col_stat2, col_stat_dl = st.columns([1.5, 1.5, 1])
        with col_stat1:
            st.metric("Mean Intensity", f"{img.mean():.3f}")
            st.metric("Min Intensity", f"{img.min():.3f}")
        with col_stat2:
            st.metric("Std Dev", f"{img.std():.3f}")
            st.metric("Max Intensity", f"{img.max():.3f}")
        
        with col_stat_dl:
            st.write("")  # Spacer
            # Create image statistics visualization
            fig_img_stats, ax = plt.subplots(figsize=(6, 4))
            stats_labels = ['Mean', 'Std Dev', 'Min', 'Max']
            stats_values = [img.mean(), img.std(), img.min(), img.max()]
            colors_stats = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
            bars = ax.bar(stats_labels, stats_values, color=colors_stats, edgecolor='black', alpha=0.7)
            ax.set_ylabel('Intensity Value', fontweight='bold')
            ax.set_title('Image Statistics', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            for bar, val in zip(bars, stats_values):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.3f}', ha='center', fontweight='bold', fontsize=8)
            
            buf_img_stats = io.BytesIO()
            fig_img_stats.savefig(buf_img_stats, format='png', dpi=300, bbox_inches='tight')
            buf_img_stats.seek(0)
            plt.close(fig_img_stats)
            
            fname_img_stats = _build_export_filename('_image_stats', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
            
            if save_mode == "Save on server (outputs/)":
                target = IMAGES_DIR / fname_img_stats
                try:
                    with open(target, 'wb') as f:
                        f.write(buf_img_stats.getvalue())
                    st.download_button(label="📥 Stats", data=buf_img_stats, file_name=fname_img_stats, mime='image/png', use_container_width=True, key="img_stats_dl")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.download_button(label="📥 Stats", data=buf_img_stats, file_name=fname_img_stats, mime='image/png', use_container_width=True, key="img_stats_dl")
        
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
        
        # Download button for histogram
        fig_hist_dl, ax = plt.subplots(figsize=(6, 4))
        ax.hist(img.flatten(), bins=50, color='steelblue', edgecolor='black', alpha=0.7)
        ax.set_xlabel('Intensity Value')
        ax.set_ylabel('Frequency')
        ax.grid(True, alpha=0.3)
        buf_hist_dl = io.BytesIO()
        fig_hist_dl.savefig(buf_hist_dl, format='png', dpi=300, bbox_inches='tight')
        buf_hist_dl.seek(0)
        plt.close(fig_hist_dl)
        
        fname_hist = _build_export_filename('_histogram', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        
        if save_mode == "Save on server (outputs/)":
            target = IMAGES_DIR / fname_hist
            try:
                with open(target, 'wb') as f:
                    f.write(buf_hist_dl.getvalue())
                st.download_button(label="📥 Save Histogram", data=buf_hist_dl, file_name=fname_hist, mime='image/png', use_container_width=True, key="hist_dl")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.download_button(label="📥 Save Histogram", data=buf_hist_dl, file_name=fname_hist, mime='image/png', use_container_width=True, key="hist_dl")
    
    st.divider()
    
    # Feature extraction
    st.subheader("🔍 Extracted Features")
    features = st.session_state.extractor.extract_features(img)
    
    feat_display_col, feat_download_col = st.columns([4, 1])
    
    with feat_display_col:
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
    
    with feat_download_col:
        st.write("")  # Spacer
        # Create feature summary visualization
        fig_feat_summary, ax = plt.subplots(figsize=(8, 6))
        feature_names = ['Uniformity', 'Symmetry', 'Wall Thickness\n(norm)', 'Radial Gradient']
        feature_values = [
            features['uniformity_score'],
            features['overall_symmetry'],
            min(features['estimated_wall_thickness'] / 0.25, 1.0),  # Normalize
            features['radial_gradient']
        ]
        colors_feat = ['#2ecc71' if v >= 0.65 else '#f39c12' if v >= 0.5 else '#e74c3c' for v in feature_values]
        ax.barh(feature_names, feature_values, color=colors_feat, edgecolor='black', alpha=0.7)
        ax.set_xlim(0, 1)
        ax.set_xlabel('Score/Value', fontweight='bold')
        ax.set_title('Feature Summary', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        buf_feat_summary = io.BytesIO()
        fig_feat_summary.savefig(buf_feat_summary, format='png', dpi=300, bbox_inches='tight')
        buf_feat_summary.seek(0)
        plt.close(fig_feat_summary)
        
        fname_feat_summary = _build_export_filename('_features', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        
        if save_mode == "Save on server (outputs/)":
            target = IMAGES_DIR / fname_feat_summary
            try:
                with open(target, 'wb') as f:
                    f.write(buf_feat_summary.getvalue())
                st.download_button(label="📥 Features", data=buf_feat_summary, file_name=fname_feat_summary, mime='image/png', use_container_width=True, key="feat_summary_dl")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.download_button(label="📥 Features", data=buf_feat_summary, file_name=fname_feat_summary, mime='image/png', use_container_width=True, key="feat_summary_dl")
    
    st.divider()
    
    # Classification
    st.subheader("📋 Quality Classification")
    classification = st.session_state.classifier.classify(features)
    
    quality = classification['quality']
    score = classification['quality_score']
    confidence = classification['confidence']
    
    # Quality badge and classification display
    class_col, class_download = st.columns([4, 1])
    
    with class_col:
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
    
    with class_download:
        st.write("")  # Spacer
        # Create comprehensive classification visualization for download
        fig_class_dl, ax = plt.subplots(figsize=(10, 4))
        
        # Top part: badge and metrics
        ax.text(0.5, 0.85, f"{quality.upper()}", ha='center', va='center', fontsize=24, fontweight='bold', 
               bbox=dict(boxstyle='round,pad=0.8', facecolor=color_progress, alpha=0.7, edgecolor='black', linewidth=2),
               color='white', transform=ax.transAxes)
        
        ax.text(0.25, 0.6, f"Score: {score:.0f}/100", ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
        ax.text(0.75, 0.6, f"Confidence: {confidence:.0f}%", ha='center', fontsize=14, fontweight='bold', transform=ax.transAxes)
        
        ax.axis('off')
        
        buf_class_dl = io.BytesIO()
        fig_class_dl.savefig(buf_class_dl, format='png', dpi=300, bbox_inches='tight')
        buf_class_dl.seek(0)
        plt.close(fig_class_dl)
        
        filename_prefix = st.session_state.get('export_prefix', f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}")
        append_timestamp = st.session_state.get('export_append_ts', True)
        append_uuid = st.session_state.get('export_append_uuid', True)
        fname_class = _build_export_filename('_classification', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
        
        if save_mode == "Save on server (outputs/)":
            target = IMAGES_DIR / fname_class
            try:
                with open(target, 'wb') as f:
                    f.write(buf_class_dl.getvalue())
                st.download_button(label="📥 Classification", data=buf_class_dl, file_name=fname_class, mime='image/png', use_container_width=True, key="class_dl")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.download_button(label="📥 Classification", data=buf_class_dl, file_name=fname_class, mime='image/png', use_container_width=True, key="class_dl")
    
    st.divider()
    
    # Decision reasoning with download
    st.subheader("📝 Decision Reasoning")
    decision_col1, decision_col2 = st.columns([1, 2])
    
    with decision_col1:
        st.write(f"**Action**: {classification['decision']}")
    
    with decision_col2:
        st.write("**Reasoning Steps**:")
        for i, reason in enumerate(classification['reasoning'], 1):
            st.write(f"{i}. {reason}")
    
    # Download button for reasoning
    reasoning_text = f"Quality Classification: {quality.upper()}\nScore: {score:.0f}/100\nConfidence: {confidence:.0f}%\n\nAction: {classification['decision']}\n\nReasoning Steps:\n"
    for i, reason in enumerate(classification['reasoning'], 1):
        reasoning_text += f"{i}. {reason}\n"
    
    reasoning_col1, reasoning_col2 = st.columns([3, 1])
    with reasoning_col2:
        fname_reasoning = _build_export_filename('_reasoning', 'txt', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        if save_mode == "Save on server (outputs/)":
            target = REPORTS_DIR / fname_reasoning
            try:
                target.write_text(reasoning_text, encoding='utf-8')
                st.download_button(label="📥 Reasoning", data=reasoning_text, file_name=fname_reasoning, mime='text/plain', use_container_width=True, key="reasoning_dl")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.download_button(label="📥 Reasoning", data=reasoning_text, file_name=fname_reasoning, mime='text/plain', use_container_width=True, key="reasoning_dl")
    
    st.divider()
    
    # Comprehensive visualization with download
    st.subheader("🎨 Comprehensive Analysis")
    comp_col, comp_download = st.columns([4, 1])
    
    with comp_col:
        fig = st.session_state.visualizer.plot_comprehensive_analysis(img, features, classification)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)
    
    with comp_download:
        st.write("")  # Spacer to align with chart
        fig_comp_dl = st.session_state.visualizer.plot_comprehensive_analysis(img, features, classification)
        buf_comp = io.BytesIO()
        fig_comp_dl.savefig(buf_comp, format='png', dpi=300, bbox_inches='tight')
        buf_comp.seek(0)
        plt.close(fig_comp_dl)
        filename_prefix = st.session_state.get('export_prefix', f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}")
        append_timestamp = st.session_state.get('export_append_ts', True)
        append_uuid = st.session_state.get('export_append_uuid', True)
        fname_comp = _build_export_filename('', 'png', prefix=f"{filename_prefix}_comprehensive", append_ts=append_timestamp, append_uuid_flag=append_uuid)
        save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
        if save_mode == "Save on server (outputs/)":
            target = IMAGES_DIR / fname_comp
            try:
                with open(target, 'wb') as f:
                    f.write(buf_comp.getvalue())
                st.download_button(label="📥 Analysis", data=buf_comp, file_name=fname_comp, mime='image/png', use_container_width=True)
            except Exception as e:
                st.error(f"Save error: {e}")
        else:
            st.download_button(label="📥 Analysis", data=buf_comp, file_name=fname_comp, mime='image/png', use_container_width=True)
    
    st.divider()
    
    # Download Reports Section - inline with download buttons
    st.subheader("📥 Download Analysis Reports")

    # Prepare report data
    report_gen = ReportGenerator()
    metadata_for_report = st.session_state.current_metadata.copy() if 'current_metadata' in st.session_state else {}
    metadata_for_report['source'] = 'Uploaded' if ('use_uploaded' in st.session_state and st.session_state.use_uploaded) else 'Synthetic'

    # Use global export settings from sidebar
    filename_prefix = st.session_state.get('export_prefix', f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}")
    save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
    append_timestamp = st.session_state.get('export_append_ts', True)
    append_uuid = st.session_state.get('export_append_uuid', True)
    include_metadata_flag = st.session_state.get('export_include_metadata', True)

    # Generate contents
    text_report = report_gen.generate_text_report(img, features, classification, metadata_for_report if include_metadata_flag else None)
    csv_report = report_gen.generate_csv_report(features, classification, metadata_for_report if include_metadata_flag else None)
    json_report = report_gen.generate_json_report(img, features, classification, metadata_for_report if include_metadata_flag else None)

    col_download1, col_download2, col_download3 = st.columns(3)

    # TXT
    with col_download1:
        st.write("**Text Report**")
        fname_txt = _build_export_filename('', 'txt', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        if save_mode == "Save on server (outputs/)":
            target = REPORTS_DIR / fname_txt
            try:
                target.write_text(text_report, encoding='utf-8')
                with open(target, 'rb') as f:
                    st.download_button(label="📄 Download TXT", data=f, file_name=fname_txt, mime='text/plain', use_container_width=True, key="txt_btn")
            except Exception as e:
                st.error(f"Failed to save: {e}")
        else:
            st.download_button(label="📄 Download TXT", data=text_report, file_name=fname_txt, mime='text/plain', use_container_width=True, key="txt_btn")

    # CSV
    with col_download2:
        st.write("**CSV Report**")
        fname_csv = _build_export_filename('', 'csv', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        if save_mode == "Save on server (outputs/)":
            target = REPORTS_DIR / fname_csv
            try:
                target.write_text(csv_report, encoding='utf-8')
                with open(target, 'rb') as f:
                    st.download_button(label="📊 Download CSV", data=f, file_name=fname_csv, mime='text/csv', use_container_width=True, key="csv_btn")
            except Exception as e:
                st.error(f"Failed to save: {e}")
        else:
            st.download_button(label="📊 Download CSV", data=csv_report, file_name=fname_csv, mime='text/csv', use_container_width=True, key="csv_btn")

    # JSON
    with col_download3:
        st.write("**JSON Report**")
        fname_json = _build_export_filename('', 'json', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
        if save_mode == "Save on server (outputs/)":
            target = REPORTS_DIR / fname_json
            try:
                target.write_text(json_report, encoding='utf-8')
                with open(target, 'rb') as f:
                    st.download_button(label="📋 Download JSON", data=f, file_name=fname_json, mime='application/json', use_container_width=True, key="json_btn")
            except Exception as e:
                st.error(f"Failed to save: {e}")
        else:
            st.download_button(label="📋 Download JSON", data=json_report, file_name=fname_json, mime='application/json', use_container_width=True, key="json_btn")

# ===== TAB 2: Agentic Inspection (NEW) =====
with tab2:
    st.subheader("🤖 Agentic Quality Control Inspection")
    st.markdown("""
    **Intelligent, Dynamic Analysis** - The Quality Control Agent dynamically decides which tools to run 
    based on intermediate results and confidence levels.
    
    🎯 **Key Features:**
    - Dynamic tool selection based on current analysis state
    - Confidence-based escalation to deeper analysis
    - Automatic flagging for human review when uncertain
    - LLM-powered explanations (when API configured)
    """)
    
    st.divider()
    
    # Agent Configuration Section
    with st.expander("⚙️ Agent Configuration", expanded=False):
        agent_col1, agent_col2 = st.columns(2)
        
        with agent_col1:
            st.markdown("**Confidence Thresholds**")
            conf_high = st.slider("High Confidence Threshold", 0.5, 1.0, 0.85, 0.05, key="agent_conf_high")
            conf_medium = st.slider("Medium Confidence Threshold", 0.4, 0.9, 0.70, 0.05, key="agent_conf_medium")
            conf_human_review = st.slider("Human Review Threshold", 0.3, 0.8, 0.55, 0.05, key="agent_conf_review")
        
        with agent_col2:
            st.markdown("**LLM Reasoning Settings**")
            use_llm = st.checkbox("Enable LLM Reasoning", value=False, key="agent_use_llm",
                                  help="Requires API key from OpenAI, Google, or Anthropic")
            if use_llm:
                llm_provider_choice = st.selectbox("LLM Provider", 
                    ["Auto-detect", "OpenAI", "Google Gemini", "Anthropic", "Local (Rule-based)"],
                    key="agent_llm_provider")
                
                if llm_provider_choice != "Auto-detect" and llm_provider_choice != "Local (Rule-based)":
                    st.info(f"Ensure your {llm_provider_choice} API key is set in environment variables")
    
    # Tool Registry Display
    with st.expander("🔧 Available Tools", expanded=False):
        tool_registry = get_default_registry()
        
        tool_col1, tool_col2 = st.columns(2)
        
        with tool_col1:
            st.markdown("**Feature Extraction Tools**")
            feature_tools = tool_registry.list_tools(category=ToolCategory.FEATURE_EXTRACTION)
            for tool in feature_tools:
                st.markdown(f"• **{tool.name}** (cost: {tool.cost})")
                st.caption(f"  {tool.description}")
            
            st.markdown("**Anomaly Detection Tools**")
            anomaly_tools = tool_registry.list_tools(category=ToolCategory.ANOMALY_DETECTION)
            for tool in anomaly_tools:
                st.markdown(f"• **{tool.name}** (cost: {tool.cost})")
                st.caption(f"  {tool.description}")
        
        with tool_col2:
            st.markdown("**Quality Assessment Tools**")
            qa_tools = tool_registry.list_tools(category=ToolCategory.QUALITY_ASSESSMENT)
            for tool in qa_tools:
                st.markdown(f"• **{tool.name}** (cost: {tool.cost})")
                st.caption(f"  {tool.description}")
            
            st.markdown("**Reporting Tools**")
            report_tools = tool_registry.list_tools(category=ToolCategory.REPORTING)
            for tool in report_tools:
                st.markdown(f"• **{tool.name}** (cost: {tool.cost})")
                st.caption(f"  {tool.description}")
    
    st.divider()
    
    # Run Agent Inspection
    agent_run_col, agent_status_col = st.columns([1, 1])
    
    with agent_run_col:
        run_agent = st.button("🚀 Run Agentic Inspection", use_container_width=True, type="primary")
    
    if run_agent:
        # Get the current image
        if 'current_img' in st.session_state and st.session_state.current_img is not None:
            img = st.session_state.current_img
        else:
            # Generate a new sample if no image is available
            img, _ = st.session_state.generator.generate_sample(seed=42, has_core=force_core, has_defect=force_defect)
            st.session_state.current_img = img
        
        # Configure agent
        confidence_thresholds = {
            'high': st.session_state.get('agent_conf_high', 0.85),
            'medium': st.session_state.get('agent_conf_medium', 0.70),
            'low': 0.60,
            'human_review': st.session_state.get('agent_conf_review', 0.55)
        }
        
        # Initialize LLM reasoning if enabled
        llm_reasoning = None
        if st.session_state.get('agent_use_llm', False):
            try:
                llm_reasoning = create_reasoning_layer()
                st.sidebar.success(f"✓ LLM Provider: {llm_reasoning.get_provider_name()}")
            except Exception as e:
                st.sidebar.warning(f"LLM not available: {e}")
        
        # Create and run the agent
        with st.spinner("🤖 Agent is analyzing..."):
            agent = create_agent(
                confidence_thresholds=confidence_thresholds,
                quality_thresholds=st.session_state.classifier.thresholds,
                llm_reasoning=llm_reasoning
            )
            
            sample_id = f"inspection_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
            result = agent.inspect(img, sample_id=sample_id)
        
        # Store result in session for display
        st.session_state.agent_result = result
        st.session_state.agent_instance = agent
        st.session_state.agent_img = img
    
    # Display Results
    if 'agent_result' in st.session_state and st.session_state.agent_result is not None:
        result = st.session_state.agent_result
        agent = st.session_state.agent_instance
        img = st.session_state.agent_img
        
        st.divider()
        st.subheader("📊 Inspection Results")
        
        # Main result display
        result_col1, result_col2, result_col3 = st.columns(3)
        
        with result_col1:
            # Quality badge
            quality = result.quality
            if quality == 'Premium':
                st.markdown('<div class="premium-badge">✅ PREMIUM</div>', unsafe_allow_html=True)
            elif quality == 'Standard':
                st.markdown('<div class="standard-badge">⚠️ STANDARD</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="defective-badge">❌ DEFECTIVE</div>', unsafe_allow_html=True)
            
            st.metric("Quality Score", f"{result.quality_score:.0f}/100")
        
        with result_col2:
            st.metric("Confidence", f"{result.confidence:.1f}%")
            
            # Confidence level indicator
            conf_level = agent.get_confidence_level()
            if conf_level == ConfidenceLevel.HIGH:
                st.success(f"🟢 {conf_level.value.upper()} Confidence")
            elif conf_level == ConfidenceLevel.MEDIUM:
                st.warning(f"🟡 {conf_level.value.upper()} Confidence")
            else:
                st.error(f"🔴 {conf_level.value.upper()} Confidence")
        
        with result_col3:
            st.metric("Tools Used", len(result.tools_used))
            st.metric("Execution Time", f"{result.total_execution_time_ms:.0f}ms")
        
        # Human Review Flag
        if result.requires_human_review:
            st.warning("⚠️ **Human Review Required** - The agent has flagged this sample for expert review due to uncertainty in the classification.")
        
        st.divider()
        
        # Decision and Reasoning
        decision_col, tools_col = st.columns([1.5, 1])
        
        with decision_col:
            st.subheader("📝 Decision & Reasoning")
            st.info(f"**Decision:** {result.decision}")
            
            st.markdown("**Reasoning Steps:**")
            for i, reason in enumerate(result.reasoning, 1):
                st.write(f"{i}. {reason}")
            
            st.markdown("**Suggested Actions:**")
            for action in result.suggested_actions:
                st.write(f"  {action}")
        
        with tools_col:
            st.subheader("🔧 Tools Executed")
            for tool_name in result.tools_used:
                st.write(f"✓ {tool_name}")
        
        st.divider()
        
        # Agent Decision Trace
        with st.expander("📋 Agent Decision Trace", expanded=False):
            st.markdown("**Step-by-step agent decisions:**")
            
            for i, entry in enumerate(result.execution_history):
                if 'action' in entry:
                    st.markdown(f"**Step {i+1}:** [{entry.get('state', 'N/A')}] {entry.get('action', 'N/A')}")
                    st.caption(f"  Reasoning: {entry.get('reasoning', 'N/A')}")
                elif 'tool' in entry:
                    status_icon = "✅" if entry.get('success', False) else "❌"
                    st.write(f"  {status_icon} Tool: {entry.get('tool')} ({entry.get('execution_time_ms', 0):.1f}ms)")
            
            # Export decision trace
            trace_json = agent.export_decision_trace()
            st.download_button(
                label="📥 Download Decision Trace (JSON)",
                data=trace_json,
                file_name=f"agent_trace_{result.sample_id}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # LLM Explanation (if available)
        if result.llm_explanation:
            with st.expander("🧠 LLM Explanation", expanded=True):
                st.markdown(result.llm_explanation)
        
        st.divider()
        
        # Visualizations
        st.subheader("🖼️ Analysis Visualization")
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # MRI Image
            fig_agent_img, ax = plt.subplots(figsize=(6, 6))
            ax.imshow(img, cmap='gray')
            ax.set_title('MRI Cross-Section', fontweight='bold')
            ax.axis('off')
            st.pyplot(fig_agent_img, use_container_width=True)
            plt.close(fig_agent_img)
        
        with viz_col2:
            # Agent workflow visualization
            fig_workflow, ax = plt.subplots(figsize=(6, 6))
            
            # Create a simple workflow diagram
            states = ['Initial', 'Basic\nInspection', 'Deeper\nAnalysis', 'Quality\nAssessment', 'Final\nDecision']
            x_positions = [0, 1, 2, 3, 4]
            y_positions = [0.5, 0.5, 0.5, 0.5, 0.5]
            
            # Determine which states were used
            states_used = set()
            for entry in result.execution_history:
                if 'state' in entry:
                    states_used.add(entry['state'])
            
            # Color mapping
            state_colors = []
            for state in ['initial', 'basic_inspection', 'deeper_analysis', 'quality_assessment', 'final_decision']:
                if state in states_used:
                    state_colors.append('#2ecc71')  # Green for completed
                else:
                    state_colors.append('#95a5a6')  # Gray for skipped
            
            # Draw circles for each state
            for x, y, state, color in zip(x_positions, y_positions, states, state_colors):
                circle = plt.Circle((x, y), 0.15, color=color, ec='black', linewidth=2)
                ax.add_patch(circle)
                ax.text(x, y - 0.3, state, ha='center', va='top', fontsize=8, fontweight='bold')
            
            # Draw arrows
            for i in range(len(x_positions) - 1):
                ax.annotate('', xy=(x_positions[i+1] - 0.15, y_positions[i+1]), 
                           xytext=(x_positions[i] + 0.15, y_positions[i]),
                           arrowprops=dict(arrowstyle='->', color='#34495e', lw=2))
            
            ax.set_xlim(-0.5, 4.5)
            ax.set_ylim(-0.2, 1.2)
            ax.set_aspect('equal')
            ax.axis('off')
            ax.set_title('Agent Workflow', fontweight='bold')
            
            st.pyplot(fig_workflow, use_container_width=True)
            plt.close(fig_workflow)

# ===== TAB 3: Batch Processing =====
with tab3:
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
        st.subheader("📊 Summary Statistics")
        quality_counts = {}
        total_score = 0
        
        for clf in batch_classes:
            quality = clf['quality']
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            total_score += clf['quality_score']
        
        col_summary1, col_summary2, col_summary3, col_summary4, col_summary_dl = st.columns([1, 1, 1, 1, 1])
        
        with col_summary1:
            st.metric("Total Samples", len(batch_classes))
        
        with col_summary2:
            st.metric("Average Score", f"{total_score/len(batch_classes):.1f}/100")
        
        with col_summary3:
            st.metric("Premium", f"{quality_counts.get('Premium', 0)}")
        
        with col_summary4:
            st.metric("Defective", f"{quality_counts.get('Defective', 0)}")
        
        with col_summary_dl:
            st.write("")  # Spacer
            # Create summary metrics visualization
            fig_batch_summary, ax = plt.subplots(figsize=(5, 3))
            summary_labels = ['Total', 'Avg Score', 'Premium', 'Defective']
            summary_values = [
                len(batch_classes),
                total_score / len(batch_classes) / 100,  # Normalize to 0-1
                quality_counts.get('Premium', 0),
                quality_counts.get('Defective', 0)
            ]
            colors_summary = ['#3498db', '#f39c12', '#2ecc71', '#e74c3c']
            bars = ax.bar(summary_labels, summary_values, color=colors_summary, edgecolor='black', alpha=0.7)
            ax.set_ylabel('Value', fontweight='bold')
            ax.set_title('Batch Overview', fontweight='bold', fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
            for i, (bar, val) in enumerate(zip(bars, summary_values)):
                display_val = f"{len(batch_classes)}" if i == 0 else f"{total_score/len(batch_classes):.1f}" if i == 1 else f"{int(val)}"
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.02, display_val, ha='center', fontweight='bold', fontsize=8)
            
            buf_batch_summary = io.BytesIO()
            fig_batch_summary.savefig(buf_batch_summary, format='png', dpi=300, bbox_inches='tight')
            buf_batch_summary.seek(0)
            plt.close(fig_batch_summary)
            
            _download_batch_viz(buf_batch_summary, '_batch_summary', "📥 Summary", "batch_summary_dl")
        
        st.divider()
        
        # Batch comparison visualization with inline downloads
        st.subheader("Quality Distribution")
        col_viz1, col_viz1_dl, col_viz2, col_viz2_dl = st.columns([3, 1, 3, 1])
        
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
            # store binary for download later
            buf_bar = io.BytesIO()
            fig_bar.savefig(buf_bar, format='png', dpi=300, bbox_inches='tight')
            buf_bar.seek(0)
            st.session_state['batch_fig_bar'] = buf_bar.getvalue()
            plt.close(fig_bar)
        
        with col_viz1_dl:
            st.write("")  # Spacer
            fig_bar_dl, ax = plt.subplots(figsize=(8, 5))
            scores = [c['quality_score'] for c in batch_classes]
            colors_bar = ['#2ecc71' if c['quality'] == 'Premium' else '#f39c12' if c['quality'] == 'Standard' else '#e74c3c' 
                         for c in batch_classes]
            ax.bar(range(len(scores)), scores, color=colors_bar, alpha=0.7, edgecolor='black')
            ax.axhline(y=85, color='green', linestyle='--', linewidth=2)
            ax.axhline(y=60, color='orange', linestyle='--', linewidth=2)
            ax.set_xlabel('Sample', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            plt.close()
            
            buf_bar_dl = io.BytesIO()
            fig_bar_dl.savefig(buf_bar_dl, format='png', dpi=300, bbox_inches='tight')
            buf_bar_dl.seek(0)
            plt.close(fig_bar_dl)
            
            _download_batch_viz(buf_bar_dl, '_bar', "📥 Bar", "bar_dl")
        
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
            buf_pie = io.BytesIO()
            fig_pie.savefig(buf_pie, format='png', dpi=300, bbox_inches='tight')
            buf_pie.seek(0)
            st.session_state['batch_fig_pie'] = buf_pie.getvalue()
            plt.close(fig_pie)
        
        with col_viz2_dl:
            st.write("")  # Spacer
            fig_pie_dl, ax = plt.subplots(figsize=(8, 6))
            colors_pie = {'Premium': '#2ecc71', 'Standard': '#f39c12', 'Defective': '#e74c3c'}
            pie_colors = [colors_pie.get(k, '#95a5a6') for k in quality_counts.keys()]
            ax.pie(quality_counts.values(), labels=quality_counts.keys(), autopct='%1.1f%%',
                   colors=pie_colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
            
            buf_pie_dl = io.BytesIO()
            fig_pie_dl.savefig(buf_pie_dl, format='png', dpi=300, bbox_inches='tight')
            buf_pie_dl.seek(0)
            plt.close(fig_pie_dl)
            
            _download_batch_viz(buf_pie_dl, '_pie', "📥 Pie", "pie_dl")
        
        st.divider()
        
        # Feature statistics table with download
        st.subheader("📊 Summary Statistics")
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
        
        col_stats, col_stats_dl = st.columns([4, 1])
        with col_stats:
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col_stats_dl:
            st.write("")  # Spacer
            # Create summary statistics visualization
            fig_stats, axes = plt.subplots(2, 2, figsize=(10, 8))
            fig_stats.suptitle('Batch Summary Statistics', fontsize=16, fontweight='bold')
            
            # Quality distribution
            quality_counts = {}
            for c in batch_classes:
                q = c['quality']
                quality_counts[q] = quality_counts.get(q, 0) + 1
            colors_bar = {'Premium': '#2ecc71', 'Standard': '#f39c12', 'Defective': '#e74c3c'}
            bar_colors = [colors_bar.get(k, '#95a5a6') for k in quality_counts.keys()]
            axes[0, 0].bar(quality_counts.keys(), quality_counts.values(), color=bar_colors)
            axes[0, 0].set_title('Quality Distribution', fontweight='bold')
            axes[0, 0].set_ylabel('Count')
            
            # Score distribution
            scores = np.array([c['quality_score'] for c in batch_classes])
            axes[0, 1].hist(scores, bins=10, color='#3498db', edgecolor='black', alpha=0.7)
            axes[0, 1].set_title('Quality Score Distribution', fontweight='bold')
            axes[0, 1].set_xlabel('Score')
            axes[0, 1].set_ylabel('Frequency')
            
            # Uniformity distribution
            uniformity = np.array([f['uniformity_score'] for f in batch_features])
            axes[1, 0].hist(uniformity, bins=10, color='#9b59b6', edgecolor='black', alpha=0.7)
            axes[1, 0].set_title('Uniformity Distribution', fontweight='bold')
            axes[1, 0].set_xlabel('Uniformity Score')
            axes[1, 0].set_ylabel('Frequency')
            
            # Symmetry distribution
            symmetry = np.array([f['overall_symmetry'] for f in batch_features])
            axes[1, 1].hist(symmetry, bins=10, color='#e67e22', edgecolor='black', alpha=0.7)
            axes[1, 1].set_title('Symmetry Distribution', fontweight='bold')
            axes[1, 1].set_xlabel('Symmetry Score')
            axes[1, 1].set_ylabel('Frequency')
            
            plt.tight_layout()
            
            buf_stats = io.BytesIO()
            fig_stats.savefig(buf_stats, format='png', dpi=300, bbox_inches='tight')
            buf_stats.seek(0)
            plt.close(fig_stats)
            
            _download_batch_viz(buf_stats, '_summary_stats', "📥 Stats", "stats_dl")
        
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
        
        # Scatter plots with inline downloads
        col_scatter1, col_scatter1_dl, col_scatter2, col_scatter2_dl = st.columns([3, 1, 3, 1])
        
        with col_scatter1:
            fig_scatter1, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(uniformity, scores, s=150, alpha=0.6, c=scores, cmap='RdYlGn', edgecolors='black')
            ax.set_xlabel('Uniformity Score', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            ax.set_title('Uniformity vs Quality', fontweight='bold')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig_scatter1, use_container_width=True)
            buf_sc1 = io.BytesIO()
            fig_scatter1.savefig(buf_sc1, format='png', dpi=300, bbox_inches='tight')
            buf_sc1.seek(0)
            st.session_state['batch_fig_scatter1'] = buf_sc1.getvalue()
            plt.close(fig_scatter1)
        
        with col_scatter1_dl:
            st.write("")  # Spacer
            fig_sc1_dl, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(uniformity, scores, s=150, alpha=0.6, c=scores, cmap='RdYlGn', edgecolors='black')
            ax.set_xlabel('Uniformity Score', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            
            buf_sc1_dl = io.BytesIO()
            fig_sc1_dl.savefig(buf_sc1_dl, format='png', dpi=300, bbox_inches='tight')
            buf_sc1_dl.seek(0)
            plt.close(fig_sc1_dl)
            
            _download_batch_viz(buf_sc1_dl, '_scatter_uniformity', "📥 Scatter 1", "scatter1_dl")
        
        with col_scatter2:
            fig_scatter2, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(symmetry, scores, s=150, alpha=0.6, c=scores, cmap='RdYlGn', edgecolors='black')
            ax.set_xlabel('Symmetry Score', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            ax.set_title('Symmetry vs Quality', fontweight='bold')
            ax.grid(True, alpha=0.3)
            st.pyplot(fig_scatter2, use_container_width=True)
            buf_sc2 = io.BytesIO()
            fig_scatter2.savefig(buf_sc2, format='png', dpi=300, bbox_inches='tight')
            buf_sc2.seek(0)
            st.session_state['batch_fig_scatter2'] = buf_sc2.getvalue()
            plt.close(fig_scatter2)
        
        with col_scatter2_dl:
            st.write("")  # Spacer
            fig_sc2_dl, ax = plt.subplots(figsize=(8, 5))
            ax.scatter(symmetry, scores, s=150, alpha=0.6, c=scores, cmap='RdYlGn', edgecolors='black')
            ax.set_xlabel('Symmetry Score', fontweight='bold')
            ax.set_ylabel('Quality Score', fontweight='bold')
            
            buf_sc2_dl = io.BytesIO()
            fig_sc2_dl.savefig(buf_sc2_dl, format='png', dpi=300, bbox_inches='tight')
            buf_sc2_dl.seek(0)
            plt.close(fig_sc2_dl)
            
            _download_batch_viz(buf_sc2_dl, '_scatter_symmetry', "📥 Scatter 2", "scatter2_dl")
        
        st.divider()
        
        # Batch Download Section (custom name + server save + ZIP export)
        st.subheader("📥 Download Batch Report")

        batch_report_gen = BatchReportGenerator()
        batch_text_report = batch_report_gen.generate_batch_summary(batch_classes, batch_features)

        # Batch filename options
        bf_prefix = st.text_input("Batch filename prefix", value=f"mri_batch_{pd.Timestamp.now().strftime('%Y%m%d')}")
        bf_append_ts = st.checkbox("Append timestamp to batch files", value=True)
        bf_append_uuid = st.checkbox("Append UUID to batch files", value=True)
        bf_save_mode = st.selectbox("Batch save mode", ["Download (browser)", "Save on server (outputs/)"])

        def build_batch_name(prefix: str, ext: str) -> str:
            parts = [prefix]
            if bf_append_ts:
                parts.append(pd.Timestamp.now().strftime('%Y%m%d_%H%M%S'))
            if bf_append_uuid:
                parts.append(str(uuid.uuid4())[:8])
            return f"{'_'.join(parts)}.{ext}"

        col_batch_download1, col_batch_download2, col_batch_download3 = st.columns(3)

        # Batch TXT summary
        with col_batch_download1:
            fname_batch_txt = build_batch_name(bf_prefix, 'txt')
            if bf_save_mode == "Save on server (outputs/)":
                target = REPORTS_DIR / fname_batch_txt
                try:
                    target.write_text(batch_text_report, encoding='utf-8')
                    st.success(f"Saved batch summary to {str(target)}")
                    with open(target, 'rb') as f:
                        st.download_button(label="📄 Download saved Batch TXT", data=f, file_name=fname_batch_txt, mime='text/plain')
                except Exception as e:
                    st.error(f"Failed to save batch TXT: {e}")
            else:
                st.download_button(label="📄 Download Batch Summary (TXT)", data=batch_text_report, file_name=fname_batch_txt, mime='text/plain')

        # Batch CSV
        with col_batch_download2:
            fname_batch_csv = build_batch_name(bf_prefix, 'csv')
            batch_csv = ReportGenerator().generate_batch_csv_report(batch_classes, batch_features)
            if bf_save_mode == "Save on server (outputs/)":
                target = REPORTS_DIR / fname_batch_csv
                try:
                    target.write_text(batch_csv, encoding='utf-8')
                    st.success(f"Saved batch CSV to {str(target)}")
                    with open(target, 'rb') as f:
                        st.download_button(label="📊 Download saved Batch CSV", data=f, file_name=fname_batch_csv, mime='text/csv')
                except Exception as e:
                    st.error(f"Failed to save batch CSV: {e}")
            else:
                st.download_button(label="📊 Download Batch Data (CSV)", data=batch_csv, file_name=fname_batch_csv, mime='text/csv')

        # Feature matrix CSV
        with col_batch_download3:
            feature_stats = {
                'Sample': [f'Sample {i+1}' for i in range(len(batch_classes))],
                'Quality': [c['quality'] for c in batch_classes],
                'Score': [f"{c['quality_score']:.0f}" for c in batch_classes],
                'Uniformity': [f"{f['uniformity_score']:.3f}" for f in batch_features],
                'Symmetry': [f"{f['overall_symmetry']:.3f}" for f in batch_features],
                'Wall_Thickness': [f"{f['estimated_wall_thickness']:.1f}" for f in batch_features],
                'Has_Anomaly': ['Yes' if f['has_anomaly'] else 'No' for f in batch_features],
            }
            df_export = pd.DataFrame(feature_stats)
            csv_buffer = df_export.to_csv(index=False)
            fname_matrix = build_batch_name(bf_prefix + '_feature_matrix', 'csv')
            if bf_save_mode == "Save on server (outputs/)":
                target = REPORTS_DIR / fname_matrix
                try:
                    target.write_text(csv_buffer, encoding='utf-8')
                    st.success(f"Saved feature matrix to {str(target)}")
                    with open(target, 'rb') as f:
                        st.download_button(label="📈 Download saved Feature Matrix (CSV)", data=f, file_name=fname_matrix, mime='text/csv')
                except Exception as e:
                    st.error(f"Failed to save feature matrix: {e}")
            else:
                st.download_button(label="📈 Download Feature Matrix (CSV)", data=csv_buffer, file_name=fname_matrix, mime='text/csv')

        # Offer ZIP with both CSV and TXT when requested
        st.markdown("---")
        if st.button("📦 Create ZIP with Batch CSV + Summary"):
            zip_name = build_batch_name(bf_prefix + '_bundle', 'zip')
            zip_path = ZIP_DIR / zip_name
            try:
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                    # add CSV
                    zf.writestr(fname_batch_csv, batch_csv)
                    # add TXT summary
                    zf.writestr(fname_batch_txt, batch_text_report)
                    # add feature matrix
                    zf.writestr(fname_matrix, csv_buffer)
                st.success(f"Created ZIP: {str(zip_path)}")
                with open(zip_path, 'rb') as f:
                    st.download_button(label="📦 Download ZIP", data=f, file_name=zip_name, mime='application/zip')
            except Exception as e:
                st.error(f"Failed to create ZIP: {e}")

# ===== TAB 4: Feature Analysis =====
with tab4:
    st.subheader("📈 Feature Deep Dive")
    
    if 'current_img' in st.session_state:
        img = st.session_state.current_img
        features = st.session_state.extractor.extract_features(img)
        
        st.write("Detailed feature breakdown for the current sample:")
        
        col_features1, col_features2, col_features3, col_features_dl = st.columns([1, 1, 1, 1])
        
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
        
        with col_features_dl:
            st.write("")  # Spacer
            # Create feature breakdown summary visualization
            fig_breakdown, ax = plt.subplots(figsize=(6, 4))
            
            breakdown_labels = ['Uniformity', 'Symmetry', 'Anomaly\nSeverity', 'Radial\nGradient']
            breakdown_values = [
                features['uniformity_score'],
                features['overall_symmetry'],
                features['anomaly_severity'],
                features['radial_gradient']
            ]
            colors_breakdown = ['#2ecc71' if v >= 0.65 else '#f39c12' if v >= 0.5 else '#e74c3c' for v in breakdown_values]
            bars = ax.bar(breakdown_labels, breakdown_values, color=colors_breakdown, edgecolor='black', alpha=0.7)
            ax.set_ylabel('Score/Value', fontweight='bold')
            ax.set_title('Key Feature Metrics', fontweight='bold')
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3, axis='y')
            for bar, val in zip(bars, breakdown_values):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.03, f'{val:.3f}', ha='center', fontweight='bold')
            
            buf_breakdown = io.BytesIO()
            fig_breakdown.savefig(buf_breakdown, format='png', dpi=300, bbox_inches='tight')
            buf_breakdown.seek(0)
            plt.close(fig_breakdown)
            
            filename_prefix = st.session_state.get('export_prefix', f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}")
            append_timestamp = st.session_state.get('export_append_ts', True)
            append_uuid = st.session_state.get('export_append_uuid', True)
            fname_breakdown = _build_export_filename('_feature_breakdown', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
            save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
            
            if save_mode == "Save on server (outputs/)":
                target = IMAGES_DIR / fname_breakdown
                try:
                    with open(target, 'wb') as f:
                        f.write(buf_breakdown.getvalue())
                    st.download_button(label="📥 Breakdown", data=buf_breakdown, file_name=fname_breakdown, mime='image/png', use_container_width=True, key="breakdown_dl")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.download_button(label="📥 Breakdown", data=buf_breakdown, file_name=fname_breakdown, mime='image/png', use_container_width=True, key="breakdown_dl")
        
        st.divider()
        
        # Radial profile visualization with download
        st.subheader("Radial Density Profile")
        radial_col, radial_dl = st.columns([4, 1])
        
        with radial_col:
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
        
        with radial_dl:
            st.write("")  # Spacer
            fig_radial_dl, ax = plt.subplots(figsize=(12, 5))
            ax.plot(bin_centers, radial_profile, linewidth=3, marker='o', markersize=8, color='steelblue')
            ax.fill_between(bin_centers, radial_profile, alpha=0.3)
            ax.set_xlabel('Distance from Center (pixels)', fontweight='bold')
            ax.set_ylabel('Mean Intensity', fontweight='bold')
            
            buf_radial_dl = io.BytesIO()
            fig_radial_dl.savefig(buf_radial_dl, format='png', dpi=300, bbox_inches='tight')
            buf_radial_dl.seek(0)
            plt.close(fig_radial_dl)
            
            filename_prefix = st.session_state.get('export_prefix', f"mri_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}")
            append_timestamp = st.session_state.get('export_append_ts', True)
            append_uuid = st.session_state.get('export_append_uuid', True)
            fname_radial = _build_export_filename('_radial_profile', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
            save_mode = st.session_state.get('export_save_mode', 'Download (browser)')
            
            if save_mode == "Save on server (outputs/)":
                target = IMAGES_DIR / fname_radial
                try:
                    with open(target, 'wb') as f:
                        f.write(buf_radial_dl.getvalue())
                    st.download_button(label="📥 Radial", data=buf_radial_dl, file_name=fname_radial, mime='image/png', use_container_width=True, key="radial_dl")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.download_button(label="📥 Radial", data=buf_radial_dl, file_name=fname_radial, mime='image/png', use_container_width=True, key="radial_dl")
        
        st.divider()
        
        # Feature importance heatmap with download
        st.subheader("Feature Importance")
        feat_col, feat_dl = st.columns([4, 1])
        
        with feat_col:
            fig = st.session_state.visualizer.plot_feature_importance(features)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        
        with feat_dl:
            st.write("")  # Spacer
            fig_feat_dl = st.session_state.visualizer.plot_feature_importance(features)
            buf_feat_dl = io.BytesIO()
            fig_feat_dl.savefig(buf_feat_dl, format='png', dpi=300, bbox_inches='tight')
            buf_feat_dl.seek(0)
            plt.close(fig_feat_dl)
            
            fname_feat = _build_export_filename('_feature_importance', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
            
            if save_mode == "Save on server (outputs/)":
                target = IMAGES_DIR / fname_feat
                try:
                    with open(target, 'wb') as f:
                        f.write(buf_feat_dl.getvalue())
                    st.download_button(label="📥 Features", data=buf_feat_dl, file_name=fname_feat, mime='image/png', use_container_width=True, key="feat_dl")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.download_button(label="📥 Features", data=buf_feat_dl, file_name=fname_feat, mime='image/png', use_container_width=True, key="feat_dl")
        st.divider()
        
        # Feature Deep Dive comprehensive visualization with download
        st.subheader("🔬 Feature Deep Dive Summary")
        deepdive_col, deepdive_dl = st.columns([4, 1])
        
        with deepdive_col:
            # Create comprehensive feature deep dive visualization
            fig_deepdive, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig_deepdive.suptitle('Feature Deep Dive Analysis', fontsize=16, fontweight='bold')
            
            # Intensity Statistics
            ax = axes[0, 0]
            intensity_stats = ['Mean', 'Std Dev', 'Min', 'Max']
            intensity_values = [features['mean_intensity'], features['std_intensity'], features['min_intensity'], features['max_intensity']]
            bars = ax.bar(intensity_stats, intensity_values, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], alpha=0.8, edgecolor='black')
            ax.set_title('Intensity Statistics', fontweight='bold', fontsize=12)
            ax.set_ylabel('Intensity Value')
            ax.grid(True, alpha=0.3, axis='y')
            for i, (bar, val) in enumerate(zip(bars, intensity_values)):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f'{val:.3f}', ha='center', fontweight='bold')
            
            # Structural Features
            ax = axes[0, 1]
            structural_features = ['Wall\nThickness', 'Layers', 'Radial\nGradient', 'Core\nIntensity']
            structural_values = [features['estimated_wall_thickness'], features['n_distinct_layers']/10, features['radial_gradient'], features['core_intensity']]
            bars = ax.bar(structural_features, structural_values, color=['#9b59b6', '#16a085', '#d35400', '#c0392b'], alpha=0.8, edgecolor='black')
            ax.set_title('Structural Features', fontweight='bold', fontsize=12)
            ax.set_ylabel('Normalized Value')
            ax.grid(True, alpha=0.3, axis='y')
            for i, (bar, val) in enumerate(zip(bars, structural_values)):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f'{val:.3f}', ha='center', fontweight='bold')
            
            # Symmetry Metrics
            ax = axes[1, 0]
            symmetry_features = ['Horizontal', 'Vertical', 'Overall', 'Uniformity']
            symmetry_values = [features['horizontal_symmetry'], features['vertical_symmetry'], features['overall_symmetry'], features['uniformity_score']]
            bars = ax.bar(symmetry_features, symmetry_values, color=['#1abc9c', '#3498db', '#2980b9', '#8e44ad'], alpha=0.8, edgecolor='black')
            ax.set_title('Symmetry & Uniformity', fontweight='bold', fontsize=12)
            ax.set_ylabel('Score (0-1)')
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0.6, color='red', linestyle='--', linewidth=2, label='Premium Threshold')
            ax.legend()
            for i, (bar, val) in enumerate(zip(bars, symmetry_values)):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.3f}', ha='center', fontweight='bold')
            
            # Quality Indicators
            ax = axes[1, 1]
            quality_features = ['Anomaly\nSeverity', 'Density\nRange', 'Has\nAnomaly', 'Has\nCore']
            quality_values = [features['anomaly_severity'], features['density_range'], float(features['has_anomaly']), float(features['has_core_structure'])]
            colors_quality = ['#e74c3c' if features['has_anomaly'] else '#2ecc71', '#f39c12', '#e74c3c' if features['has_anomaly'] else '#2ecc71', '#2ecc71' if features['has_core_structure'] else '#e74c3c']
            bars = ax.bar(quality_features, quality_values, color=colors_quality, alpha=0.8, edgecolor='black')
            ax.set_title('Quality Indicators', fontweight='bold', fontsize=12)
            ax.set_ylabel('Value')
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            st.pyplot(fig_deepdive, use_container_width=True)
            plt.close(fig_deepdive)
        
        with deepdive_dl:
            st.write("")  # Spacer
            fig_deepdive_dl, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig_deepdive_dl.suptitle('Feature Deep Dive Analysis', fontsize=16, fontweight='bold')
            
            # Intensity Statistics
            ax = axes[0, 0]
            intensity_stats = ['Mean', 'Std Dev', 'Min', 'Max']
            intensity_values = [features['mean_intensity'], features['std_intensity'], features['min_intensity'], features['max_intensity']]
            bars = ax.bar(intensity_stats, intensity_values, color=['#3498db', '#e74c3c', '#2ecc71', '#f39c12'], alpha=0.8, edgecolor='black')
            ax.set_title('Intensity Statistics', fontweight='bold', fontsize=12)
            ax.set_ylabel('Intensity Value')
            ax.grid(True, alpha=0.3, axis='y')
            for i, (bar, val) in enumerate(zip(bars, intensity_values)):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f'{val:.3f}', ha='center', fontweight='bold')
            
            # Structural Features
            ax = axes[0, 1]
            structural_features = ['Wall\nThickness', 'Layers', 'Radial\nGradient', 'Core\nIntensity']
            structural_values = [features['estimated_wall_thickness'], features['n_distinct_layers']/10, features['radial_gradient'], features['core_intensity']]
            bars = ax.bar(structural_features, structural_values, color=['#9b59b6', '#16a085', '#d35400', '#c0392b'], alpha=0.8, edgecolor='black')
            ax.set_title('Structural Features', fontweight='bold', fontsize=12)
            ax.set_ylabel('Normalized Value')
            ax.grid(True, alpha=0.3, axis='y')
            for i, (bar, val) in enumerate(zip(bars, structural_values)):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.01, f'{val:.3f}', ha='center', fontweight='bold')
            
            # Symmetry Metrics
            ax = axes[1, 0]
            symmetry_features = ['Horizontal', 'Vertical', 'Overall', 'Uniformity']
            symmetry_values = [features['horizontal_symmetry'], features['vertical_symmetry'], features['overall_symmetry'], features['uniformity_score']]
            bars = ax.bar(symmetry_features, symmetry_values, color=['#1abc9c', '#3498db', '#2980b9', '#8e44ad'], alpha=0.8, edgecolor='black')
            ax.set_title('Symmetry & Uniformity', fontweight='bold', fontsize=12)
            ax.set_ylabel('Score (0-1)')
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0.6, color='red', linestyle='--', linewidth=2, label='Premium Threshold')
            ax.legend()
            for i, (bar, val) in enumerate(zip(bars, symmetry_values)):
                ax.text(bar.get_x() + bar.get_width()/2, val + 0.02, f'{val:.3f}', ha='center', fontweight='bold')
            
            # Quality Indicators
            ax = axes[1, 1]
            quality_features = ['Anomaly\nSeverity', 'Density\nRange', 'Has\nAnomaly', 'Has\nCore']
            quality_values = [features['anomaly_severity'], features['density_range'], float(features['has_anomaly']), float(features['has_core_structure'])]
            colors_quality = ['#e74c3c' if features['has_anomaly'] else '#2ecc71', '#f39c12', '#e74c3c' if features['has_anomaly'] else '#2ecc71', '#2ecc71' if features['has_core_structure'] else '#e74c3c']
            bars = ax.bar(quality_features, quality_values, color=colors_quality, alpha=0.8, edgecolor='black')
            ax.set_title('Quality Indicators', fontweight='bold', fontsize=12)
            ax.set_ylabel('Value')
            ax.set_ylim([0, 1])
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            buf_deepdive = io.BytesIO()
            fig_deepdive_dl.savefig(buf_deepdive, format='png', dpi=300, bbox_inches='tight')
            buf_deepdive.seek(0)
            plt.close(fig_deepdive_dl)
            
            fname_deepdive = _build_export_filename('_feature_deep_dive', 'png', prefix=filename_prefix, append_ts=append_timestamp, append_uuid_flag=append_uuid)
            
            if save_mode == "Save on server (outputs/)":
                target = IMAGES_DIR / fname_deepdive
                try:
                    with open(target, 'wb') as f:
                        f.write(buf_deepdive.getvalue())
                    st.download_button(label="📥 Deep Dive", data=buf_deepdive, file_name=fname_deepdive, mime='image/png', use_container_width=True, key="deepdive_dl")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.download_button(label="📥 Deep Dive", data=buf_deepdive, file_name=fname_deepdive, mime='image/png', use_container_width=True, key="deepdive_dl")
    else:
        st.info("Generate a sample first in the 'Single Analysis' tab to see feature analysis.")

# ===== TAB 5: About =====
with tab5:
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
    ├── data_generator.py         # Synthetic MRI generation
    ├── feature_extractor.py      # Feature computation
    ├── classifier.py             # Rule-based classification
    ├── visualizer.py             # Professional visualizations
    ├── quality_control_agent.py  # 🤖 NEW: Agentic Quality Control
    ├── tool_registry.py          # 🔧 NEW: Dynamic Tool Selection
    └── llm_reasoning.py          # 🧠 NEW: LLM Reasoning Layer
    
    app.py                         # This Streamlit interface
    demo.py                        # Command-line demo
    ```
    
    ### 🤖 Agentic Upgrade (v2.0)
    
    The system has been upgraded with three major enhancements:
    
    **1. Quality Control Agent** (Upgrade 1)
    - Dynamic decision-making based on intermediate results
    - Confidence-based workflow escalation
    - Automatic human review flagging
    - Complete decision trace for auditability
    
    **2. Tool Selection** (Upgrade 2)
    - Agent dynamically selects which analysis tools to run
    - Cost-aware tool selection
    - Category-based tool organization
    - Lazy execution based on analysis needs
    
    **3. LLM Reasoning Layer** (Upgrade 3)
    - Natural language explanations of decisions
    - Confidence assessment recommendations
    - Threshold adjustment suggestions
    - Supports OpenAI, Google Gemini, Anthropic, or local mode
    """)
    
    st.divider()
    
    st.subheader("How to Use This Interface")
    
    st.markdown("""
    ### 📊 Single Analysis Tab
    - Generate custom samples with specific properties
    - View detailed feature extraction results
    - See classification reasoning
    - Explore comprehensive multi-panel visualizations
    
    ### 🤖 Agentic Inspection Tab (NEW)
    - Run the Quality Control Agent for intelligent analysis
    - Watch the agent dynamically select analysis tools
    - View confidence levels and escalation decisions
    - See LLM-generated explanations (when configured)
    - Download complete decision traces
    
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
    - Configure LLM settings for explanations
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; margin-top: 20px;'>
    <p>Synthetic MRI Inspector v2.0 • Agentic Quality Inspection</p>
    <p>🤖 Quality Control Agent | 🔧 Dynamic Tool Selection | 🧠 LLM Reasoning</p>
    <p>Python 3.12 | NumPy | SciPy | Scikit-Image | Streamlit</p>
</div>
""", unsafe_allow_html=True)

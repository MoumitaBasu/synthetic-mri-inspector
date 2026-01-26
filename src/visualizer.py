"""
Visualization Module
Creates comprehensive visualizations of MRI analysis
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from typing import Dict
import seaborn as sns


class MRIVisualizer:
    """Create visualizations for MRI analysis results"""
    
    def __init__(self):
        sns.set_style("darkgrid")
        self.colors = {
            'Premium': '#2ecc71',
            'Standard': '#f39c12',
            'Defective': '#e74c3c'
        }
    
    def plot_comprehensive_analysis(self, img: np.ndarray, 
                                   features: Dict, 
                                   classification: Dict,
                                   save_path: str = None):
        """
        Create a comprehensive visualization of the analysis
        
        Args:
            img: Original MRI image
            features: Extracted features
            classification: Classification results
            save_path: Optional path to save figure
        """
        fig = plt.figure(figsize=(16, 10))
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Original Image
        ax1 = fig.add_subplot(gs[0:2, 0])
        ax1.imshow(img, cmap='gray')
        ax1.set_title('Synthetic MRI Scan', fontsize=14, fontweight='bold')
        ax1.axis('off')
        
        # 2. Classification Result
        ax2 = fig.add_subplot(gs[0, 1])
        quality = classification['quality']
        color = self.colors.get(quality, '#95a5a6')
        ax2.text(0.5, 0.6, quality, 
                ha='center', va='center', 
                fontsize=32, fontweight='bold',
                color=color)
        ax2.text(0.5, 0.3, f"{classification['quality_score']:.0f}/100",
                ha='center', va='center',
                fontsize=20, color='gray')
        ax2.text(0.5, 0.1, f"Confidence: {classification['confidence']:.0f}%",
                ha='center', va='center',
                fontsize=14, color='gray')
        ax2.set_xlim(0, 1)
        ax2.set_ylim(0, 1)
        ax2.axis('off')
        ax2.set_title('Classification', fontsize=14, fontweight='bold')
        
        # 3. Feature Scores
        ax3 = fig.add_subplot(gs[1, 1])
        feature_names = ['Uniformity', 'Symmetry', 'Wall\nQuality']
        feature_values = [
            features['uniformity_score'],
            features['overall_symmetry'],
            1 - features['anomaly_severity']
        ]
        bars = ax3.barh(feature_names, feature_values, color=['#3498db', '#9b59b6', '#1abc9c'])
        ax3.set_xlim(0, 1)
        ax3.set_xlabel('Score', fontsize=10)
        ax3.set_title('Key Metrics', fontsize=14, fontweight='bold')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, feature_values)):
            ax3.text(val + 0.02, i, f'{val:.2f}', 
                    va='center', fontsize=10)
        
        # 4. Radial Intensity Profile
        ax4 = fig.add_subplot(gs[0, 2])
        center = np.array(img.shape) // 2
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        distances = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        
        max_dist = np.max(distances)
        n_bins = 30
        radii = []
        intensities = []
        
        for i in range(n_bins):
            r_min = (i / n_bins) * max_dist
            r_max = ((i + 1) / n_bins) * max_dist
            mask = (distances >= r_min) & (distances < r_max)
            if mask.sum() > 0:
                radii.append((r_min + r_max) / 2)
                intensities.append(np.mean(img[mask]))
        
        ax4.plot(radii, intensities, linewidth=2, color='#e74c3c')
        ax4.fill_between(radii, intensities, alpha=0.3, color='#e74c3c')
        ax4.set_xlabel('Distance from Center (px)', fontsize=10)
        ax4.set_ylabel('Intensity', fontsize=10)
        ax4.set_title('Radial Density Profile', fontsize=12, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        
        # 5. Intensity Histogram
        ax5 = fig.add_subplot(gs[1, 2])
        ax5.hist(img.flatten(), bins=50, color='#34495e', alpha=0.7, edgecolor='black')
        ax5.axvline(np.mean(img), color='#e74c3c', linestyle='--', 
                   linewidth=2, label=f'Mean: {np.mean(img):.2f}')
        ax5.set_xlabel('Intensity', fontsize=10)
        ax5.set_ylabel('Frequency', fontsize=10)
        ax5.set_title('Intensity Distribution', fontsize=12, fontweight='bold')
        ax5.legend(fontsize=9)
        ax5.grid(True, alpha=0.3)
        
        # 6. Reasoning Panel
        ax6 = fig.add_subplot(gs[2, :])
        ax6.axis('off')
        
        reasoning_text = "Analysis Reasoning:\n\n"
        for i, reason in enumerate(classification['reasoning'], 1):
            reasoning_text += f"{i}. {reason}\n"
        
        reasoning_text += f"\nDecision: {classification['decision']}"
        
        ax6.text(0.05, 0.95, reasoning_text,
                transform=ax6.transAxes,
                fontsize=11,
                verticalalignment='top',
                fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        # Overall title
        fig.suptitle('Synthetic MRI Quality Analysis Report', 
                    fontsize=18, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        
        return fig
    
    def plot_batch_comparison(self, images: np.ndarray, 
                            features_list: list,
                            classifications: list,
                            save_path: str = None):
        """
        Compare multiple samples side by side
        
        Args:
            images: Array of images
            features_list: List of feature dictionaries
            classifications: List of classification results
            save_path: Optional path to save
        """
        n_samples = len(images)
        fig, axes = plt.subplots(2, n_samples, figsize=(4*n_samples, 8))
        
        if n_samples == 1:
            axes = axes.reshape(2, 1)
        
        for i in range(n_samples):
            # Image
            axes[0, i].imshow(images[i], cmap='gray')
            axes[0, i].set_title(f'Sample {i+1}', fontsize=12, fontweight='bold')
            axes[0, i].axis('off')
            
            # Classification info
            quality = classifications[i]['quality']
            score = classifications[i]['quality_score']
            color = self.colors.get(quality, '#95a5a6')
            
            axes[1, i].text(0.5, 0.7, quality,
                          ha='center', va='center',
                          fontsize=20, fontweight='bold',
                          color=color)
            axes[1, i].text(0.5, 0.4, f"Score: {score:.0f}",
                          ha='center', va='center',
                          fontsize=14)
            
            # Key metrics
            metrics = f"U: {features_list[i]['uniformity_score']:.2f}\n"
            metrics += f"S: {features_list[i]['overall_symmetry']:.2f}\n"
            metrics += f"A: {'Yes' if features_list[i]['has_anomaly'] else 'No'}"
            
            axes[1, i].text(0.5, 0.1, metrics,
                          ha='center', va='top',
                          fontsize=10, fontfamily='monospace')
            
            axes[1, i].set_xlim(0, 1)
            axes[1, i].set_ylim(0, 1)
            axes[1, i].axis('off')
        
        plt.suptitle('Batch Quality Comparison', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Batch comparison saved to {save_path}")
        
        return fig
    
    def plot_feature_importance(self, features: Dict, save_path: str = None):
        """Plot feature importance/contribution"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        feature_names = [
            'Uniformity',
            'Symmetry',
            'Wall Thickness',
            'Anomaly Free',
            'Density Range'
        ]
        
        feature_values = [
            features['uniformity_score'],
            features['overall_symmetry'],
            min(1.0, features['estimated_wall_thickness'] * 5),
            1 - features['anomaly_severity'],
            1 - (features['density_range'] / 1.0)
        ]
        
        colors_gradient = plt.cm.RdYlGn(np.array(feature_values))
        bars = ax.barh(feature_names, feature_values, color=colors_gradient)
        
        ax.set_xlabel('Score', fontsize=12)
        ax.set_title('Feature Contribution to Quality', fontsize=14, fontweight='bold')
        ax.set_xlim(0, 1)
        
        # Add value labels
        for bar, val in zip(bars, feature_values):
            width = bar.get_width()
            ax.text(width + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{val:.2f}',
                   ha='left', va='center', fontsize=11)
        
        ax.grid(True, alpha=0.3, axis='x')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
        
        return fig


if __name__ == "__main__":
    # Demo usage
    from data_generator import SyntheticMRIGenerator
    from feature_extractor import FeatureExtractor
    from classifier import QualityClassifier
    
    generator = SyntheticMRIGenerator(image_size=256)
    extractor = FeatureExtractor()
    classifier = QualityClassifier()
    visualizer = MRIVisualizer()
    
    # Generate sample
    img, metadata = generator.generate_sample(seed=42)
    features = extractor.extract_features(img)
    classification = classifier.classify(features)
    
    # Create comprehensive visualization
    visualizer.plot_comprehensive_analysis(img, features, classification, 
                                          save_path='analysis_report.png')
    
    print("Visualization complete! Check 'analysis_report.png'")

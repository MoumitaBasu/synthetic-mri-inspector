"""
Quick Demo Script
Run this to see the complete pipeline in action
"""
import os
import sys
sys.path.append('src')

from data_generator import SyntheticMRIGenerator
from feature_extractor import FeatureExtractor
from classifier import QualityClassifier
from visualizer import MRIVisualizer
import matplotlib.pyplot as plt


def main():
    print("="*70)
    print("  SYNTHETIC MRI INSIGHT EXPLORER - DEMO")
    print("="*70)
    print()
    
    # Create output directory
    os.makedirs('examples/outputs', exist_ok=True)
    
    # Initialize all components
    print("[1/5] Initializing components...")
    generator = SyntheticMRIGenerator(image_size=256)
    extractor = FeatureExtractor()
    classifier = QualityClassifier()
    visualizer = MRIVisualizer()
    print("      ✓ All components initialized")
    print()
    
    # Generate samples
    print("[2/5] Generating synthetic MRI samples...")
    n_samples = 5
    images = []
    all_features = []
    all_classifications = []
    
    for i in range(n_samples):
        img, metadata = generator.generate_sample(seed=i*10)
        images.append(img)
        
        features = extractor.extract_features(img)
        all_features.append(features)
        
        classification = classifier.classify(features)
        all_classifications.append(classification)
        
        print(f"      Sample {i+1}: {classification['quality']} "
              f"(Score: {classification['quality_score']:.0f}, "
              f"Confidence: {classification['confidence']:.0f}%)")
    
    print()
    
    # Detailed analysis of first sample
    print("[3/5] Performing detailed analysis on Sample 1...")
    print()
    extractor.print_features(all_features[0])
    classifier.print_classification(all_classifications[0])
    
    # Generate visualizations
    print("[4/5] Creating visualizations...")
    
    # Comprehensive analysis of first sample
    fig1 = visualizer.plot_comprehensive_analysis(
        images[0], 
        all_features[0], 
        all_classifications[0],
        save_path='examples/outputs/comprehensive_analysis.png'
    )
    plt.close(fig1)
    print("      ✓ Comprehensive analysis saved")
    
    # Batch comparison
    import numpy as np
    fig2 = visualizer.plot_batch_comparison(
        np.array(images),
        all_features,
        all_classifications,
        save_path='examples/outputs/batch_comparison.png'
    )
    plt.close(fig2)
    print("      ✓ Batch comparison saved")
    
    # Feature importance
    fig3 = visualizer.plot_feature_importance(
        all_features[0],
        save_path='examples/outputs/feature_importance.png'
    )
    plt.close(fig3)
    print("      ✓ Feature importance saved")
    
    print()
    
    # Generate report
    print("[5/5] Generating inspection report...")
    report = classifier.generate_report(all_features[0], all_classifications[0])
    
    report_path = 'examples/outputs/inspection_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"      ✓ Report saved to {report_path}")
    print()
    
    # Summary statistics
    print("="*70)
    print("  SUMMARY STATISTICS")
    print("="*70)
    
    quality_counts = {}
    total_score = 0
    
    for clf in all_classifications:
        quality = clf['quality']
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
        total_score += clf['quality_score']
    
    print(f"\nTotal Samples Processed: {n_samples}")
    print(f"Average Quality Score: {total_score/n_samples:.1f}/100")
    print(f"\nQuality Distribution:")
    for quality, count in sorted(quality_counts.items()):
        percentage = (count / n_samples) * 100
        print(f"  {quality}: {count} ({percentage:.0f}%)")
    
    print("\n" + "="*70)
    print("  DEMO COMPLETE!")
    print("="*70)
    print("\nGenerated files in examples/outputs/:")
    print("  • comprehensive_analysis.png")
    print("  • batch_comparison.png")
    print("  • feature_importance.png")
    print("  • inspection_report.txt")
    print("\nNext steps:")
    print("  1. Check the outputs directory")
    print("  2. Open notebooks/exploration.ipynb for interactive analysis")
    print("  3. Modify src/ files to experiment with different approaches")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()

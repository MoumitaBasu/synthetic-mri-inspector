"""
Rule-based Classifier
Demonstrates interpretable decision-making without ML training
"""
import numpy as np
from typing import Dict, Tuple


class QualityClassifier:
    """Rule-based classifier for quality assessment"""
    
    def __init__(self):
        # Define quality thresholds (tunable based on domain requirements)
        self.thresholds = {
            'uniformity_min': 0.6,
            'symmetry_min': 0.65,
            'anomaly_severity_max': 0.02,
            'wall_thickness_min': 0.05,
            'wall_thickness_max': 0.25
        }
    
    def classify(self, features: Dict) -> Dict:
        """
        Classify sample quality based on extracted features
        
        Args:
            features: Dictionary of features from FeatureExtractor
            
        Returns:
            Dictionary containing:
                - quality: 'Premium', 'Standard', or 'Defective'
                - confidence: 0-100
                - decision: Action to take
                - reasoning: List of reasoning steps
        """
        reasoning = []
        quality_score = 100
        quality_factors = []
        
        # Rule 1: Check for critical defects
        if features['has_anomaly'] and features['anomaly_severity'] > self.thresholds['anomaly_severity_max']:
            quality_score -= 50
            reasoning.append(f"⚠️ Significant anomaly detected (severity: {features['anomaly_severity']:.3f})")
            quality_factors.append('defect')
        
        # Rule 2: Evaluate uniformity
        if features['uniformity_score'] < self.thresholds['uniformity_min']:
            quality_score -= 20
            reasoning.append(f"⚠️ Low uniformity score: {features['uniformity_score']:.2f}")
            quality_factors.append('non_uniform')
        else:
            reasoning.append(f"✓ Good uniformity: {features['uniformity_score']:.2f}")
        
        # Rule 3: Check symmetry
        if features['overall_symmetry'] < self.thresholds['symmetry_min']:
            quality_score -= 15
            reasoning.append(f"⚠️ Asymmetric structure: {features['overall_symmetry']:.2f}")
            quality_factors.append('asymmetric')
        else:
            reasoning.append(f"✓ Symmetric structure: {features['overall_symmetry']:.2f}")
        
        # Rule 4: Wall thickness evaluation
        wall_thickness = features['estimated_wall_thickness']
        if wall_thickness < self.thresholds['wall_thickness_min']:
            quality_score -= 15
            reasoning.append(f"⚠️ Wall too thin: {wall_thickness:.3f}")
            quality_factors.append('thin_wall')
        elif wall_thickness > self.thresholds['wall_thickness_max']:
            quality_score -= 10
            reasoning.append(f"⚠️ Wall too thick: {wall_thickness:.3f}")
            quality_factors.append('thick_wall')
        else:
            reasoning.append(f"✓ Optimal wall thickness: {wall_thickness:.3f}")
        
        # Rule 5: Core structure bonus for certain applications
        if features['has_core_structure']:
            if features['core_intensity'] < 0.35:  # Well-formed core
                quality_score += 5
                reasoning.append(f"✓ Well-formed core structure detected")
            else:
                quality_score -= 5
                reasoning.append(f"⚠️ Irregular core structure")
        
        # Determine quality category
        quality_score = max(0, min(100, quality_score))
        
        if quality_score >= 85 and 'defect' not in quality_factors:
            quality = 'Premium'
            decision = 'Premium Grade - Proceed to market'
        elif quality_score >= 60 and 'defect' not in quality_factors:
            quality = 'Standard'
            decision = 'Standard Grade - Secondary processing'
        else:
            quality = 'Defective'
            decision = 'Reject - Quality control failure'
        
        # Calculate confidence based on feature reliability
        confidence = self._calculate_confidence(features, quality_factors)
        
        return {
            'quality': quality,
            'quality_score': quality_score,
            'confidence': confidence,
            'decision': decision,
            'reasoning': reasoning,
            'factors': quality_factors
        }
    
    def _calculate_confidence(self, features: Dict, quality_factors: list) -> float:
        """Calculate classification confidence based on feature clarity"""
        confidence = 90  # Base confidence
        
        # Reduce confidence for edge cases
        if features['uniformity_score'] > 0.55 and features['uniformity_score'] < 0.65:
            confidence -= 10
        
        if features['overall_symmetry'] > 0.60 and features['overall_symmetry'] < 0.70:
            confidence -= 10
        
        # Increase confidence for clear-cut cases
        if features['has_anomaly'] and features['anomaly_severity'] > 0.05:
            confidence = min(95, confidence + 5)
        
        if features['uniformity_score'] > 0.80:
            confidence = min(98, confidence + 5)
        
        # Reduce confidence for conflicting signals
        if len(quality_factors) >= 3:
            confidence -= 10
        
        return max(60, min(98, confidence))
    
    def batch_classify(self, features_list: list) -> list:
        """Classify multiple samples"""
        return [self.classify(features) for features in features_list]
    
    def print_classification(self, classification: Dict):
        """Print classification results in readable format"""
        print("\n" + "="*50)
        print("QUALITY CLASSIFICATION")
        print("="*50)
        
        print(f"\n🎯 Quality: {classification['quality']}")
        print(f"📊 Quality Score: {classification['quality_score']:.1f}/100")
        print(f"🎲 Confidence: {classification['confidence']:.1f}%")
        print(f"✅ Decision: {classification['decision']}")
        
        print("\n📝 Reasoning:")
        for i, reason in enumerate(classification['reasoning'], 1):
            print(f"  {i}. {reason}")
        
        print("="*50 + "\n")
    
    def generate_report(self, features: Dict, classification: Dict) -> str:
        """Generate a detailed inspection report"""
        report = []
        report.append("="*60)
        report.append("SYNTHETIC MRI QUALITY INSPECTION REPORT")
        report.append("="*60)
        report.append("")
        
        report.append(f"CLASSIFICATION: {classification['quality']}")
        report.append(f"Quality Score: {classification['quality_score']:.1f}/100")
        report.append(f"Confidence: {classification['confidence']:.1f}%")
        report.append(f"Decision: {classification['decision']}")
        report.append("")
        
        report.append("KEY METRICS:")
        report.append(f"  • Uniformity Score: {features['uniformity_score']:.3f}")
        report.append(f"  • Symmetry Score: {features['overall_symmetry']:.3f}")
        report.append(f"  • Wall Thickness: {features['estimated_wall_thickness']:.3f}")
        report.append(f"  • Anomaly Detected: {features['has_anomaly']}")
        if features['has_anomaly']:
            report.append(f"    - Severity: {features['anomaly_severity']:.3f}")
            report.append(f"    - Count: {features['anomaly_count']}")
        report.append("")
        
        report.append("REASONING:")
        for i, reason in enumerate(classification['reasoning'], 1):
            report.append(f"  {i}. {reason}")
        report.append("")
        
        report.append("="*60)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Demo usage
    from data_generator import SyntheticMRIGenerator
    from feature_extractor import FeatureExtractor
    
    generator = SyntheticMRIGenerator(image_size=256)
    extractor = FeatureExtractor()
    classifier = QualityClassifier()
    
    # Generate and classify multiple samples
    print("Generating and classifying samples...\n")
    
    for i in range(3):
        print(f"\n{'='*60}")
        print(f"SAMPLE {i+1}")
        print('='*60)
        
        img, metadata = generator.generate_sample(seed=i*10)
        features = extractor.extract_features(img)
        classification = classifier.classify(features)
        
        classifier.print_classification(classification)

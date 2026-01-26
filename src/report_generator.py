"""
Report Generator for MRI Analysis
Generates comprehensive reports in multiple formats (PDF, CSV, JSON)
"""
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
import json
import io


class ReportGenerator:
    """Generate analysis reports in various formats"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_text_report(self, 
                            img: np.ndarray, 
                            features: Dict, 
                            classification: Dict,
                            metadata: Dict = None) -> str:
        """
        Generate comprehensive text report
        
        Args:
            img: Image array
            features: Extracted features dictionary
            classification: Classification result dictionary
            metadata: Optional metadata (filename, upload info, etc.)
            
        Returns:
            Formatted text report as string
        """
        report = []
        report.append("=" * 80)
        report.append("SYNTHETIC MRI INSPECTOR - ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {self.timestamp}\n")
        
        # Image information
        report.append("\n" + "=" * 80)
        report.append("IMAGE INFORMATION")
        report.append("=" * 80)
        
        if metadata:
            report.append(f"Source: {metadata.get('source', 'Unknown')}")
            report.append(f"Filename: {metadata.get('filename', 'N/A')}")
            if metadata.get('original_size'):
                report.append(f"Original Size: {metadata.get('original_size')}")
                report.append(f"Resized To: {metadata.get('resized_to', '256×256')}")
        
        report.append(f"Image Dimensions: {img.shape[0]} × {img.shape[1]} pixels")
        report.append(f"Data Type: {img.dtype}")
        
        # Image statistics
        report.append("\n" + "-" * 80)
        report.append("IMAGE STATISTICS")
        report.append("-" * 80)
        report.append(f"Mean Intensity: {img.mean():.4f}")
        report.append(f"Std Deviation: {img.std():.4f}")
        report.append(f"Min Intensity: {img.min():.4f}")
        report.append(f"Max Intensity: {img.max():.4f}")
        report.append(f"Intensity Range: {img.max() - img.min():.4f}")
        report.append(f"Median Intensity: {np.median(img):.4f}")
        report.append(f"Skewness: {self._calculate_skewness(img):.4f}")
        
        # Features section
        report.append("\n" + "=" * 80)
        report.append("EXTRACTED FEATURES (15+ Metrics)")
        report.append("=" * 80)
        
        report.append("\n--- INTENSITY STATISTICS ---")
        report.append(f"Mean Intensity: {features.get('mean_intensity', 0):.4f}")
        report.append(f"Std Intensity: {features.get('std_intensity', 0):.4f}")
        report.append(f"Min Intensity: {features.get('min_intensity', 0):.4f}")
        report.append(f"Max Intensity: {features.get('max_intensity', 0):.4f}")
        report.append(f"Density Range: {features.get('density_range', 0):.4f}")
        report.append(f"Radial Profile Mean: {features.get('radial_profile_mean', 0):.4f}")
        
        report.append("\n--- STRUCTURAL FEATURES ---")
        report.append(f"Estimated Wall Thickness: {features.get('estimated_wall_thickness', 0):.3f} pixels")
        report.append(f"Number of Distinct Layers: {features.get('n_distinct_layers', 0)}")
        report.append(f"Has Core Structure: {'Yes' if features.get('has_core_structure', False) else 'No'}")
        report.append(f"Core Intensity: {features.get('core_intensity', 0):.4f}")
        report.append(f"Radial Gradient: {features.get('radial_gradient', 0):.4f}")
        
        report.append("\n--- QUALITY METRICS ---")
        report.append(f"Uniformity Score: {features.get('uniformity_score', 0):.4f} (target ≥ 0.60)")
        report.append(f"Horizontal Symmetry: {features.get('horizontal_symmetry', 0):.4f}")
        report.append(f"Vertical Symmetry: {features.get('vertical_symmetry', 0):.4f}")
        report.append(f"Overall Symmetry: {features.get('overall_symmetry', 0):.4f} (target ≥ 0.65)")
        report.append(f"Anomaly Detected: {'Yes' if features.get('has_anomaly', False) else 'No'}")
        report.append(f"Anomaly Severity: {features.get('anomaly_severity', 0):.4f} (threshold: 0.02)")
        
        # Classification section
        report.append("\n" + "=" * 80)
        report.append("QUALITY CLASSIFICATION RESULT")
        report.append("=" * 80)
        
        quality = classification.get('quality', 'Unknown')
        score = classification.get('quality_score', 0)
        confidence = classification.get('confidence', 0)
        decision = classification.get('decision', 'No decision')
        
        report.append(f"\nQuality Grade: {quality}")
        report.append(f"Quality Score: {score:.1f}/100")
        report.append(f"Confidence Level: {confidence:.1f}%")
        report.append(f"Recommended Action: {decision}")
        
        # Classification reasoning
        report.append("\n" + "-" * 80)
        report.append("DECISION REASONING (Rule-Based)")
        report.append("-" * 80)
        for i, reason in enumerate(classification.get('reasoning', []), 1):
            report.append(f"{i}. {reason}")
        
        # Threshold compliance
        report.append("\n" + "-" * 80)
        report.append("THRESHOLD COMPLIANCE")
        report.append("-" * 80)
        uniformity = features.get('uniformity_score', 0)
        symmetry = features.get('overall_symmetry', 0)
        wall_thickness = features.get('estimated_wall_thickness', 0)
        anomaly_severity = features.get('anomaly_severity', 0)
        
        report.append(f"✓ Uniformity (≥0.60): {uniformity:.3f} {'PASS' if uniformity >= 0.60 else 'FAIL'}")
        report.append(f"✓ Symmetry (≥0.65): {symmetry:.3f} {'PASS' if symmetry >= 0.65 else 'FAIL'}")
        report.append(f"✓ Wall Thickness (0.05-0.25): {wall_thickness:.3f} {'PASS' if 0.05 <= wall_thickness <= 0.25 else 'FAIL'}")
        report.append(f"✓ Anomaly Severity (≤0.02): {anomaly_severity:.3f} {'PASS' if anomaly_severity <= 0.02 else 'FAIL'}")
        
        # Summary
        report.append("\n" + "=" * 80)
        report.append("SUMMARY & RECOMMENDATIONS")
        report.append("=" * 80)
        
        if quality == 'Premium':
            report.append("""
✅ PREMIUM GRADE
This sample meets all quality standards and is ready for market.
Characteristics:
  • Excellent uniformity and structural symmetry
  • Minimal or no anomalies detected
  • Optimal wall thickness and core formation
Action: Proceed to packaging and distribution
""")
        elif quality == 'Standard':
            report.append("""
⚠️ STANDARD GRADE
This sample is acceptable but may benefit from secondary processing.
Characteristics:
  • Good structural properties but minor deviations
  • Small irregularities or slight asymmetry
  • Generally acceptable for secondary market
Action: Secondary processing recommended, quality control inspection advised
""")
        else:
            report.append("""
❌ DEFECTIVE GRADE
This sample does not meet quality standards and should be rejected.
Characteristics:
  • Significant defects or anomalies detected
  • Poor uniformity or structural integrity
  • Does not meet threshold requirements
Action: Reject sample, investigate root cause, adjust process parameters
""")
        
        # Footer
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        report.append(f"\nReport Generated: {self.timestamp}")
        report.append("Synthetic MRI Inspector • Data-Efficient Quality Inspection")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_csv_report(self, 
                           features: Dict, 
                           classification: Dict,
                           include_metadata: Dict = None) -> str:
        """
        Generate CSV report with all metrics
        
        Args:
            features: Extracted features dictionary
            classification: Classification result dictionary
            include_metadata: Optional metadata to include
            
        Returns:
            CSV formatted string
        """
        # Flatten features and classification into a single row
        data = {}
        
        # Add timestamp
        data['Timestamp'] = self.timestamp
        
        # Add classification results
        data['Quality_Grade'] = classification.get('quality', 'Unknown')
        data['Quality_Score'] = classification.get('quality_score', 0)
        data['Confidence_%'] = classification.get('confidence', 0)
        data['Decision'] = classification.get('decision', 'N/A')
        
        # Add all features
        for key, value in features.items():
            # Convert boolean to Yes/No for readability
            if isinstance(value, bool):
                data[f'Feature_{key}'] = 'Yes' if value else 'No'
            elif isinstance(value, (int, float)):
                data[f'Feature_{key}'] = round(value, 6) if isinstance(value, float) else value
            else:
                data[f'Feature_{key}'] = str(value)
        
        # Add metadata if provided
        if include_metadata:
            for key, value in include_metadata.items():
                if key != 'source':  # Skip source field
                    data[f'Metadata_{key}'] = str(value)
        
        # Create DataFrame and convert to CSV
        df = pd.DataFrame([data])
        return df.to_csv(index=False)
    
    def generate_batch_csv_report(self,
                                 classifications_list: List[Dict],
                                 features_list: List[Dict]) -> str:
        """
        Generate CSV report for batch processing results
        
        Args:
            classifications_list: List of classification results
            features_list: List of feature dictionaries
            
        Returns:
            CSV formatted string
        """
        rows = []
        
        for idx, (clf, feat) in enumerate(zip(classifications_list, features_list), 1):
            row = {
                'Sample_ID': f'Sample_{idx}',
                'Quality_Grade': clf.get('quality', 'Unknown'),
                'Quality_Score': round(clf.get('quality_score', 0), 2),
                'Confidence_%': round(clf.get('confidence', 0), 2),
            }
            
            # Add key features
            row['Uniformity_Score'] = round(feat.get('uniformity_score', 0), 4)
            row['Overall_Symmetry'] = round(feat.get('overall_symmetry', 0), 4)
            row['Wall_Thickness_px'] = round(feat.get('estimated_wall_thickness', 0), 3)
            row['Has_Anomaly'] = 'Yes' if feat.get('has_anomaly', False) else 'No'
            row['Anomaly_Severity'] = round(feat.get('anomaly_severity', 0), 4)
            row['Has_Core'] = 'Yes' if feat.get('has_core_structure', False) else 'No'
            row['Mean_Intensity'] = round(feat.get('mean_intensity', 0), 4)
            row['Std_Intensity'] = round(feat.get('std_intensity', 0), 4)
            
            rows.append(row)
        
        # Add summary statistics
        quality_counts = {}
        total_score = 0
        
        for clf in classifications_list:
            quality = clf.get('quality', 'Unknown')
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
            total_score += clf.get('quality_score', 0)
        
        # Create summary row
        summary_row = {
            'Sample_ID': '=== SUMMARY ===',
            'Quality_Grade': 'TOTAL_SAMPLES',
            'Quality_Score': len(classifications_list),
            'Confidence_%': f"AVG: {total_score/len(classifications_list):.1f}",
        }
        
        for quality_type, count in quality_counts.items():
            summary_row[quality_type] = count
        
        rows.append(summary_row)
        
        df = pd.DataFrame(rows)
        return df.to_csv(index=False)
    
    def generate_json_report(self,
                            img: np.ndarray,
                            features: Dict,
                            classification: Dict,
                            metadata: Dict = None) -> str:
        """
        Generate JSON report for programmatic use
        
        Args:
            img: Image array
            features: Extracted features dictionary
            classification: Classification result dictionary
            metadata: Optional metadata
            
        Returns:
            JSON formatted string
        """
        report_data = {
            'metadata': {
                'report_type': 'MRI_Analysis_Report',
                'timestamp': self.timestamp,
                'version': '1.0'
            },
            'image_info': {
                'dimensions': list(img.shape),
                'dtype': str(img.dtype),
                'statistics': {
                    'mean': float(img.mean()),
                    'std': float(img.std()),
                    'min': float(img.min()),
                    'max': float(img.max()),
                    'median': float(np.median(img))
                }
            },
            'features': {},
            'classification': {
                'quality': classification.get('quality', 'Unknown'),
                'quality_score': float(classification.get('quality_score', 0)),
                'confidence': float(classification.get('confidence', 0)),
                'decision': classification.get('decision', 'N/A'),
                'reasoning': classification.get('reasoning', [])
            }
        }
        
        # Add features (convert numpy types to native Python types)
        for key, value in features.items():
            if isinstance(value, np.ndarray):
                report_data['features'][key] = value.tolist()
            elif isinstance(value, (np.floating, float)):
                report_data['features'][key] = float(value)
            elif isinstance(value, (np.integer, int)):
                report_data['features'][key] = int(value)
            elif isinstance(value, bool):
                report_data['features'][key] = bool(value)
            else:
                report_data['features'][key] = str(value)
        
        # Add metadata if provided
        if metadata:
            report_data['upload_metadata'] = metadata
        
        return json.dumps(report_data, indent=2)
    
    def _calculate_skewness(self, img: np.ndarray) -> float:
        """Calculate skewness of image intensity distribution"""
        flat = img.flatten()
        mean = np.mean(flat)
        std = np.std(flat)
        if std == 0:
            return 0.0
        skewness = np.mean(((flat - mean) / std) ** 3)
        return float(skewness)


class BatchReportGenerator:
    """Generate comprehensive batch analysis reports"""
    
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate_batch_summary(self,
                              classifications_list: List[Dict],
                              features_list: List[Dict]) -> str:
        """
        Generate comprehensive batch summary report
        
        Args:
            classifications_list: List of classification dictionaries
            features_list: List of feature dictionaries
            
        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 80)
        report.append("BATCH PROCESSING ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {self.timestamp}")
        report.append(f"Total Samples Processed: {len(classifications_list)}\n")
        
        # Calculate statistics
        quality_counts = {'Premium': 0, 'Standard': 0, 'Defective': 0}
        scores = []
        confidences = []
        
        for clf in classifications_list:
            quality = clf.get('quality', 'Unknown')
            if quality in quality_counts:
                quality_counts[quality] += 1
            scores.append(clf.get('quality_score', 0))
            confidences.append(clf.get('confidence', 0))
        
        scores_array = np.array(scores)
        
        # Summary statistics
        report.append("=" * 80)
        report.append("SUMMARY STATISTICS")
        report.append("=" * 80)
        
        report.append("\n--- QUALITY DISTRIBUTION ---")
        report.append(f"Premium Samples: {quality_counts['Premium']} ({100*quality_counts['Premium']/len(classifications_list):.1f}%)")
        report.append(f"Standard Samples: {quality_counts['Standard']} ({100*quality_counts['Standard']/len(classifications_list):.1f}%)")
        report.append(f"Defective Samples: {quality_counts['Defective']} ({100*quality_counts['Defective']/len(classifications_list):.1f}%)")
        
        report.append("\n--- QUALITY SCORE STATISTICS ---")
        report.append(f"Mean Score: {scores_array.mean():.2f}/100")
        report.append(f"Median Score: {np.median(scores_array):.2f}/100")
        report.append(f"Std Deviation: {scores_array.std():.2f}")
        report.append(f"Min Score: {scores_array.min():.2f}/100")
        report.append(f"Max Score: {scores_array.max():.2f}/100")
        
        report.append("\n--- CONFIDENCE STATISTICS ---")
        conf_array = np.array(confidences)
        report.append(f"Mean Confidence: {conf_array.mean():.1f}%")
        report.append(f"Median Confidence: {np.median(conf_array):.1f}%")
        report.append(f"Min Confidence: {conf_array.min():.1f}%")
        report.append(f"Max Confidence: {conf_array.max():.1f}%")
        
        # Feature correlations
        report.append("\n" + "=" * 80)
        report.append("FEATURE CORRELATIONS WITH QUALITY")
        report.append("=" * 80)
        
        uniformity_scores = np.array([f.get('uniformity_score', 0) for f in features_list])
        symmetry_scores = np.array([f.get('overall_symmetry', 0) for f in features_list])
        wall_thickness = np.array([f.get('estimated_wall_thickness', 0) for f in features_list])
        
        if len(scores_array) > 1:
            corr_uniformity = np.corrcoef(uniformity_scores, scores_array)[0, 1]
            corr_symmetry = np.corrcoef(symmetry_scores, scores_array)[0, 1]
            corr_wall = np.corrcoef(wall_thickness, scores_array)[0, 1]
            
            report.append(f"Uniformity ↔ Quality Score: {corr_uniformity:+.3f}")
            report.append(f"Symmetry ↔ Quality Score: {corr_symmetry:+.3f}")
            report.append(f"Wall Thickness ↔ Quality Score: {corr_wall:+.3f}")
        
        # Anomaly analysis
        report.append("\n" + "=" * 80)
        report.append("ANOMALY ANALYSIS")
        report.append("=" * 80)
        
        anomaly_count = sum(1 for f in features_list if f.get('has_anomaly', False))
        anomaly_severity_scores = [f.get('anomaly_severity', 0) for f in features_list if f.get('has_anomaly', False)]
        
        report.append(f"Samples with Anomalies: {anomaly_count} ({100*anomaly_count/len(features_list):.1f}%)")
        if anomaly_severity_scores:
            report.append(f"Average Anomaly Severity: {np.mean(anomaly_severity_scores):.4f}")
            report.append(f"Max Anomaly Severity: {np.max(anomaly_severity_scores):.4f}")
        
        # Detailed sample listing
        report.append("\n" + "=" * 80)
        report.append("DETAILED SAMPLE RESULTS")
        report.append("=" * 80 + "\n")
        
        for idx, (clf, feat) in enumerate(zip(classifications_list, features_list), 1):
            report.append(f"Sample {idx}:")
            report.append(f"  Quality: {clf.get('quality', 'Unknown')}")
            report.append(f"  Score: {clf.get('quality_score', 0):.1f}/100")
            report.append(f"  Confidence: {clf.get('confidence', 0):.1f}%")
            report.append(f"  Uniformity: {feat.get('uniformity_score', 0):.3f}")
            report.append(f"  Symmetry: {feat.get('overall_symmetry', 0):.3f}")
            report.append(f"  Anomaly: {'Yes' if feat.get('has_anomaly', False) else 'No'}")
            report.append("")
        
        # Footer
        report.append("=" * 80)
        report.append("END OF BATCH REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)

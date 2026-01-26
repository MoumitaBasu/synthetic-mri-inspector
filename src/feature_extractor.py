"""
Feature Extraction Module
Extracts interpretable features from synthetic MRI images
"""
import numpy as np
from typing import Dict
from scipy import ndimage
from skimage.measure import label, regionprops


class FeatureExtractor:
    """Extract interpretable structural features from MRI images"""
    
    def __init__(self):
        pass
    
    def extract_features(self, img: np.ndarray) -> Dict:
        """
        Extract all features from an image
        
        Args:
            img: 2D numpy array (grayscale image)
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic intensity statistics
        features['mean_intensity'] = np.mean(img)
        features['std_intensity'] = np.std(img)
        features['min_intensity'] = np.min(img)
        features['max_intensity'] = np.max(img)
        
        # Density distribution
        features.update(self._compute_density_distribution(img))
        
        # Structural features
        features.update(self._detect_layers(img))
        
        # Symmetry analysis
        features.update(self._compute_symmetry(img))
        
        # Anomaly detection
        features.update(self._detect_anomalies(img))
        
        # Uniformity metrics
        features['uniformity_score'] = self._compute_uniformity(img)
        
        return features
    
    def _compute_density_distribution(self, img: np.ndarray) -> Dict:
        """Compute density distribution metrics"""
        # Radial density profile
        center = np.array(img.shape) // 2
        y, x = np.ogrid[:img.shape[0], :img.shape[1]]
        distances = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        
        max_dist = np.max(distances)
        n_bins = 20
        radial_profile = []
        
        for i in range(n_bins):
            r_min = (i / n_bins) * max_dist
            r_max = ((i + 1) / n_bins) * max_dist
            mask = (distances >= r_min) & (distances < r_max)
            if mask.sum() > 0:
                radial_profile.append(np.mean(img[mask]))
            else:
                radial_profile.append(0)
        
        radial_profile = np.array(radial_profile)
        
        return {
            'radial_profile_mean': np.mean(radial_profile),
            'radial_profile_std': np.std(radial_profile),
            'radial_gradient': np.mean(np.abs(np.diff(radial_profile))),
            'density_range': np.ptp(img)
        }
    
    def _detect_layers(self, img: np.ndarray) -> Dict:
        """Detect distinct layers or shells"""
        # Threshold image into layers
        thresholds = [0.2, 0.4, 0.6, 0.8]
        layer_areas = []
        
        for thresh in thresholds:
            binary = img > thresh
            layer_areas.append(np.sum(binary))
        
        # Estimate wall thickness from layer transitions
        layer_diffs = np.diff(layer_areas)
        wall_thickness_estimate = np.max(np.abs(layer_diffs)) if len(layer_diffs) > 0 else 0
        
        # Detect core (low-intensity center region)
        center_region = img[img.shape[0]//4:3*img.shape[0]//4, 
                           img.shape[1]//4:3*img.shape[1]//4]
        has_core = np.mean(center_region) < 0.4
        
        return {
            'estimated_wall_thickness': wall_thickness_estimate / 100,  # Normalize
            'n_distinct_layers': len(np.unique(np.digitize(img, thresholds))),
            'has_core_structure': has_core,
            'core_intensity': np.mean(center_region) if has_core else 0
        }
    
    def _compute_symmetry(self, img: np.ndarray) -> Dict:
        """Compute symmetry metrics"""
        # Horizontal symmetry
        left = img[:, :img.shape[1]//2]
        right = np.fliplr(img[:, img.shape[1]//2:])
        min_width = min(left.shape[1], right.shape[1])
        h_symmetry = 1 - np.mean(np.abs(left[:, :min_width] - right[:, :min_width]))
        
        # Vertical symmetry
        top = img[:img.shape[0]//2, :]
        bottom = np.flipud(img[img.shape[0]//2:, :])
        min_height = min(top.shape[0], bottom.shape[0])
        v_symmetry = 1 - np.mean(np.abs(top[:min_height, :] - bottom[:min_height, :]))
        
        return {
            'horizontal_symmetry': max(0, h_symmetry),
            'vertical_symmetry': max(0, v_symmetry),
            'overall_symmetry': max(0, (h_symmetry + v_symmetry) / 2)
        }
    
    def _detect_anomalies(self, img: np.ndarray) -> Dict:
        """Detect anomalous regions"""
        # Use intensity deviation to find anomalies
        mean_intensity = np.mean(img)
        std_intensity = np.std(img)
        
        # Regions significantly darker than average
        anomaly_threshold = mean_intensity - 2 * std_intensity
        anomaly_mask = img < anomaly_threshold
        
        # Label connected components
        labeled = label(anomaly_mask)
        regions = regionprops(labeled)
        
        has_anomaly = len(regions) > 0
        anomaly_count = len(regions)
        
        # Largest anomaly size
        max_anomaly_area = max([r.area for r in regions]) if regions else 0
        
        return {
            'has_anomaly': has_anomaly,
            'anomaly_count': anomaly_count,
            'max_anomaly_area': max_anomaly_area,
            'anomaly_severity': max_anomaly_area / img.size if has_anomaly else 0
        }
    
    def _compute_uniformity(self, img: np.ndarray) -> float:
        """Compute overall uniformity score (0-1)"""
        # Combine multiple uniformity metrics
        intensity_uniformity = 1 - (np.std(img) / (np.mean(img) + 1e-6))
        
        # Local variance
        from scipy.ndimage import uniform_filter
        local_mean = uniform_filter(img, size=20)
        local_variance = uniform_filter((img - local_mean)**2, size=20)
        spatial_uniformity = 1 - (np.mean(local_variance) / (np.var(img) + 1e-6))
        
        uniformity = (intensity_uniformity + spatial_uniformity) / 2
        return max(0, min(1, uniformity))
    
    def print_features(self, features: Dict):
        """Print features in readable format"""
        print("\n" + "="*50)
        print("EXTRACTED FEATURES")
        print("="*50)
        
        print("\n[Intensity Statistics]")
        print(f"  Mean: {features['mean_intensity']:.3f}")
        print(f"  Std Dev: {features['std_intensity']:.3f}")
        print(f"  Range: {features['density_range']:.3f}")
        
        print("\n[Structural Features]")
        print(f"  Wall Thickness (est): {features['estimated_wall_thickness']:.3f}")
        print(f"  Distinct Layers: {features['n_distinct_layers']}")
        print(f"  Has Core: {features['has_core_structure']}")
        
        print("\n[Symmetry Analysis]")
        print(f"  Horizontal: {features['horizontal_symmetry']:.3f}")
        print(f"  Vertical: {features['vertical_symmetry']:.3f}")
        print(f"  Overall: {features['overall_symmetry']:.3f}")
        
        print("\n[Anomaly Detection]")
        print(f"  Anomalies Detected: {features['has_anomaly']}")
        print(f"  Count: {features['anomaly_count']}")
        print(f"  Severity: {features['anomaly_severity']:.3f}")
        
        print("\n[Quality Metrics]")
        print(f"  Uniformity Score: {features['uniformity_score']:.3f}")
        print("="*50 + "\n")


if __name__ == "__main__":
    # Demo usage
    from data_generator import SyntheticMRIGenerator
    
    generator = SyntheticMRIGenerator(image_size=256)
    extractor = FeatureExtractor()
    
    # Generate sample
    img, metadata = generator.generate_sample(seed=42)
    
    # Extract features
    features = extractor.extract_features(img)
    
    # Print results
    extractor.print_features(features)

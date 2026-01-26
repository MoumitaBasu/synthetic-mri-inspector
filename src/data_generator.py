"""
Synthetic MRI Data Generator
Creates artificial cross-sectional images simulating internal structures
"""
import numpy as np
from typing import Dict, Tuple
import matplotlib.pyplot as plt


class SyntheticMRIGenerator:
    """Generate synthetic MRI-like images of objects with internal structure"""
    
    def __init__(self, image_size: int = 256):
        self.image_size = image_size
        
    def generate_sample(self, 
                       seed: int = None,
                       has_core: bool = None,
                       has_defect: bool = None) -> Tuple[np.ndarray, Dict]:
        """
        Generate a single synthetic MRI sample
        
        Args:
            seed: Random seed for reproducibility
            has_core: Force presence/absence of core structure
            has_defect: Force presence/absence of defect
            
        Returns:
            Tuple of (image_array, metadata_dict)
        """
        if seed is not None:
            np.random.seed(seed)
        
        # Initialize blank image
        img = np.zeros((self.image_size, self.image_size))
        
        # Generate random parameters
        center = self.image_size // 2
        outer_radius = self.image_size // 2 - 10
        
        # Random structural parameters
        wall_thickness = np.random.uniform(10, 30)
        core_present = np.random.rand() > 0.3 if has_core is None else has_core
        core_radius = np.random.uniform(15, 35) if core_present else 0
        core_offset_x = np.random.uniform(-10, 10) if core_present else 0
        core_offset_y = np.random.uniform(-10, 10) if core_present else 0
        defect_present = np.random.rand() > 0.6 if has_defect is None else has_defect
        
        # Create coordinate grids
        y, x = np.ogrid[:self.image_size, :self.image_size]
        
        # Outer shell
        dist_from_center = np.sqrt((x - center)**2 + (y - center)**2)
        outer_mask = dist_from_center <= outer_radius
        shell_mask = (dist_from_center <= outer_radius) & (dist_from_center > outer_radius - wall_thickness)
        
        # Shell intensity (higher density)
        img[shell_mask] = np.random.uniform(0.7, 0.9, shell_mask.sum())
        
        # Inner flesh/tissue
        inner_mask = dist_from_center <= (outer_radius - wall_thickness)
        img[inner_mask] = np.random.uniform(0.4, 0.6, inner_mask.sum())
        
        # Core/seed structure
        if core_present:
            core_x = center + core_offset_x
            core_y = center + core_offset_y
            core_dist = np.sqrt((x - core_x)**2 + (y - core_y)**2)
            core_mask = core_dist <= core_radius
            img[core_mask] = np.random.uniform(0.2, 0.35, core_mask.sum())
        
        # Add defect/anomaly
        defect_info = None
        if defect_present:
            defect_x = center + np.random.uniform(-outer_radius/2, outer_radius/2)
            defect_y = center + np.random.uniform(-outer_radius/2, outer_radius/2)
            defect_radius = np.random.uniform(5, 15)
            defect_dist = np.sqrt((x - defect_x)**2 + (y - defect_y)**2)
            defect_mask = defect_dist <= defect_radius
            img[defect_mask] = np.random.uniform(0.1, 0.25, defect_mask.sum())
            defect_info = {
                'x': defect_x,
                'y': defect_y,
                'radius': defect_radius
            }
        
        # Add realistic noise
        noise = np.random.normal(0, 0.05, img.shape)
        img = np.clip(img + noise, 0, 1)
        
        # Apply slight Gaussian blur for realism
        from scipy.ndimage import gaussian_filter
        img = gaussian_filter(img, sigma=1.5)
        
        # Metadata
        metadata = {
            'wall_thickness': wall_thickness,
            'core_present': core_present,
            'core_radius': core_radius,
            'core_offset': (core_offset_x, core_offset_y) if core_present else None,
            'defect_present': defect_present,
            'defect_info': defect_info,
            'outer_radius': outer_radius,
            'image_size': self.image_size
        }
        
        return img, metadata
    
    def generate_batch(self, n_samples: int = 10) -> Tuple[np.ndarray, list]:
        """Generate multiple samples"""
        images = []
        metadata_list = []
        
        for i in range(n_samples):
            img, meta = self.generate_sample(seed=i)
            images.append(img)
            metadata_list.append(meta)
        
        return np.array(images), metadata_list
    
    def visualize_sample(self, img: np.ndarray, metadata: Dict = None):
        """Visualize a single sample with metadata"""
        plt.figure(figsize=(8, 8))
        plt.imshow(img, cmap='gray')
        plt.colorbar(label='Density')
        plt.title('Synthetic MRI Cross-Section')
        plt.axis('off')
        
        if metadata:
            info_text = f"Wall Thickness: {metadata['wall_thickness']:.1f}px\n"
            info_text += f"Core: {'Present' if metadata['core_present'] else 'Absent'}\n"
            if metadata['core_present']:
                info_text += f"Core Radius: {metadata['core_radius']:.1f}px\n"
            info_text += f"Defect: {'Detected' if metadata['defect_present'] else 'None'}"
            
            plt.text(10, 30, info_text, fontsize=10, color='yellow',
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        plt.tight_layout()
        return plt.gcf()


if __name__ == "__main__":
    # Demo usage
    generator = SyntheticMRIGenerator(image_size=256)
    
    # Generate samples
    print("Generating synthetic MRI samples...")
    images, metadata = generator.generate_batch(n_samples=5)
    
    # Visualize first sample
    generator.visualize_sample(images[0], metadata[0])
    plt.savefig('sample_output.png', dpi=150, bbox_inches='tight')
    print("Sample saved as 'sample_output.png'")
    
    print(f"\nGenerated {len(images)} samples")
    print(f"Image shape: {images[0].shape}")

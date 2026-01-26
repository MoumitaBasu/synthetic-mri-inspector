"""
Image Upload Handler
Handles loading, validating, and preprocessing uploaded MRI images
"""
import numpy as np
from PIL import Image
from io import BytesIO
from typing import Tuple, Optional


class ImageUploadHandler:
    """Handle uploaded image files for analysis"""
    
    SUPPORTED_FORMATS = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff']
    DEFAULT_SIZE = 256
    MAX_FILE_SIZE_MB = 10
    
    @staticmethod
    def validate_file(uploaded_file) -> Tuple[bool, str]:
        """
        Validate uploaded file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (is_valid, message)
        """
        if uploaded_file is None:
            return False, "No file selected"
        
        # Check file size
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > ImageUploadHandler.MAX_FILE_SIZE_MB:
            return False, f"File too large ({file_size_mb:.1f} MB). Max: {ImageUploadHandler.MAX_FILE_SIZE_MB} MB"
        
        # Check file extension
        file_ext = uploaded_file.name.split('.')[-1].lower()
        if file_ext not in ImageUploadHandler.SUPPORTED_FORMATS:
            return False, f"Unsupported format: .{file_ext}. Supported: {', '.join(ImageUploadHandler.SUPPORTED_FORMATS)}"
        
        return True, "Valid file"
    
    @staticmethod
    def load_and_preprocess(uploaded_file, target_size: int = 256) -> Tuple[np.ndarray, dict]:
        """
        Load uploaded image and preprocess for analysis
        
        Args:
            uploaded_file: Streamlit uploaded file object
            target_size: Target image size (will be resized to this)
            
        Returns:
            Tuple of (processed_image, metadata)
        """
        try:
            # Load image
            img = Image.open(uploaded_file)
            
            # Store original info
            original_size = img.size
            original_mode = img.mode
            
            # Convert to grayscale if needed
            if img.mode != 'L':
                img = img.convert('L')
            
            # Resize to target size
            img_resized = img.resize((target_size, target_size), Image.Resampling.LANCZOS)
            
            # Convert to numpy array and normalize to 0-1
            img_array = np.array(img_resized, dtype=np.float32) / 255.0
            
            # Metadata
            metadata = {
                'source': 'uploaded',
                'filename': uploaded_file.name,
                'original_size': original_size,
                'original_mode': original_mode,
                'resized_to': (target_size, target_size),
                'min_intensity': float(np.min(img_array)),
                'max_intensity': float(np.max(img_array)),
                'mean_intensity': float(np.mean(img_array))
            }
            
            return img_array, metadata
            
        except Exception as e:
            raise ValueError(f"Error loading image: {str(e)}")
    
    @staticmethod
    def get_image_info(img: np.ndarray, filename: str = "Unknown") -> dict:
        """Get detailed information about an image"""
        return {
            'filename': filename,
            'shape': img.shape,
            'dtype': str(img.dtype),
            'min': float(np.min(img)),
            'max': float(np.max(img)),
            'mean': float(np.mean(img)),
            'std': float(np.std(img)),
            'range': float(np.max(img) - np.min(img))
        }


if __name__ == "__main__":
    # Example usage
    print("Image Upload Handler Initialized")
    print(f"Supported formats: {', '.join(ImageUploadHandler.SUPPORTED_FORMATS)}")
    print(f"Max file size: {ImageUploadHandler.MAX_FILE_SIZE_MB} MB")
    print(f"Default size: {ImageUploadHandler.DEFAULT_SIZE}×{ImageUploadHandler.DEFAULT_SIZE}")

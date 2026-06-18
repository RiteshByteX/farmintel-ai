"""
Image Processor Utility
Handles image preprocessing, augmentation, and transformation for ML model input
"""

import cv2
import numpy as np
from PIL import Image
import io
import base64
from typing import Tuple, Optional, Union, List
from flask import current_app


class ImageProcessor:
    """
    Utility class for image preprocessing and augmentation
    Prepares images for ML model input with consistent sizing and normalization
    """
    
    # Default target size for model input
    DEFAULT_TARGET_SIZE = (224, 224)
    
    # Supported image formats
    SUPPORTED_FORMATS = {'jpg', 'jpeg', 'png', 'bmp', 'webp', 'tiff'}
    
    @classmethod
    def preprocess_for_model(cls, image_input: Union[str, np.ndarray, bytes], 
                             target_size: Tuple[int, int] = None) -> Optional[np.ndarray]:
        """
        Preprocess image for model input
        
        Args:
            image_input: Image path, numpy array, or bytes
            target_size: Target size (height, width), default (224, 224)
            
        Returns:
            Preprocessed image array ready for model input
        """
        if target_size is None:
            target_size = cls.DEFAULT_TARGET_SIZE
        
        try:
            # Load image based on input type
            if isinstance(image_input, str):
                # File path
                img = cv2.imread(image_input)
                if img is None:
                    raise ValueError(f"Could not load image from {image_input}")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
            elif isinstance(image_input, np.ndarray):
                # Already numpy array
                img = image_input.copy()
                if len(img.shape) == 2:  # Grayscale
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                elif img.shape[2] == 4:  # RGBA
                    img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
                    
            elif isinstance(image_input, bytes):
                # Bytes data
                nparr = np.frombuffer(image_input, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    raise ValueError("Could not decode image from bytes")
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
            
            # Resize image
            img = cv2.resize(img, target_size)
            
            # Normalize pixel values to [0, 1]
            img = img.astype('float32') / 255.0
            
            # Add batch dimension
            img = np.expand_dims(img, axis=0)
            
            return img
            
        except Exception as e:
            current_app.logger.error(f"Image preprocessing error: {str(e)}")
            return None
    
    @classmethod
    def resize_image(cls, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """
        Resize image to target size
        
        Args:
            image: Input image array
            target_size: Target size (width, height)
            
        Returns:
            Resized image
        """
        return cv2.resize(image, target_size)
    
    @classmethod
    def normalize_image(cls, image: np.ndarray) -> np.ndarray:
        """
        Normalize image pixel values to [0, 1]
        
        Args:
            image: Input image array
            
        Returns:
            Normalized image
        """
        return image.astype('float32') / 255.0
    
    @classmethod
    def denormalize_image(cls, image: np.ndarray) -> np.ndarray:
        """
        Denormalize image from [0, 1] to [0, 255]
        
        Args:
            image: Normalized image array
            
        Returns:
            Denormalized image as uint8
        """
        return (image * 255).astype('uint8')
    
    @classmethod
    def convert_to_rgb(cls, image: np.ndarray) -> np.ndarray:
        """
        Convert image to RGB format
        
        Args:
            image: Input image array
            
        Returns:
            RGB image
        """
        if len(image.shape) == 2:
            # Grayscale to RGB
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 3:
            # Already RGB, assume it's correct
            return image
        elif image.shape[2] == 4:
            # RGBA to RGB
            return cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        else:
            return image
    
    @classmethod
    def convert_to_bgr(cls, image: np.ndarray) -> np.ndarray:
        """
        Convert image to BGR format (OpenCV default)
        
        Args:
            image: Input image array
            
        Returns:
            BGR image
        """
        if len(image.shape) == 2:
            return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        elif image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            return image
    
    @classmethod
    def rotate_image(cls, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Rotate image by specified angle
        
        Args:
            image: Input image
            angle: Rotation angle in degrees
            
        Returns:
            Rotated image
        """
        h, w = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h))
        return rotated
    
    @classmethod
    def flip_image(cls, image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
        """
        Flip image horizontally or vertically
        
        Args:
            image: Input image
            direction: 'horizontal' or 'vertical'
            
        Returns:
            Flipped image
        """
        if direction == 'horizontal':
            return cv2.flip(image, 1)
        elif direction == 'vertical':
            return cv2.flip(image, 0)
        else:
            return image
    
    @classmethod
    def adjust_brightness(cls, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image brightness
        
        Args:
            image: Input image
            factor: Brightness factor (0.5 - 1.5)
            
        Returns:
            Brightness adjusted image
        """
        return np.clip(image * factor, 0, 255).astype('uint8')
    
    @classmethod
    def adjust_contrast(cls, image: np.ndarray, factor: float) -> np.ndarray:
        """
        Adjust image contrast
        
        Args:
            image: Input image
            factor: Contrast factor (0.5 - 1.5)
            
        Returns:
            Contrast adjusted image
        """
        mean = np.mean(image)
        return np.clip((image - mean) * factor + mean, 0, 255).astype('uint8')
    
    @classmethod
    def apply_augmentation(cls, image: np.ndarray, augmentation_type: str = 'basic') -> np.ndarray:
        """
        Apply data augmentation to image
        
        Args:
            image: Input image
            augmentation_type: 'basic', 'heavy', or 'none'
            
        Returns:
            Augmented image
        """
        import random
        
        if augmentation_type == 'none':
            return image
        
        img = image.copy()
        
        if augmentation_type == 'basic':
            # Random horizontal flip (50% chance)
            if random.random() > 0.5:
                img = cls.flip_image(img, 'horizontal')
            
            # Random rotation (±15 degrees)
            if random.random() > 0.7:
                angle = random.uniform(-15, 15)
                img = cls.rotate_image(img, angle)
            
            # Random brightness adjustment
            if random.random() > 0.7:
                factor = random.uniform(0.8, 1.2)
                img = cls.adjust_brightness(img, factor)
        
        elif augmentation_type == 'heavy':
            # Random horizontal flip
            if random.random() > 0.3:
                img = cls.flip_image(img, 'horizontal')
            
            # Random vertical flip
            if random.random() > 0.7:
                img = cls.flip_image(img, 'vertical')
            
            # Random rotation (±30 degrees)
            if random.random() > 0.5:
                angle = random.uniform(-30, 30)
                img = cls.rotate_image(img, angle)
            
            # Random brightness adjustment
            if random.random() > 0.5:
                factor = random.uniform(0.6, 1.4)
                img = cls.adjust_brightness(img, factor)
            
            # Random contrast adjustment
            if random.random() > 0.7:
                factor = random.uniform(0.7, 1.3)
                img = cls.adjust_contrast(img, factor)
            
            # Add slight blur
            if random.random() > 0.8:
                ksize = random.choice([3, 5])
                img = cv2.GaussianBlur(img, (ksize, ksize), 0)
        
        return img
    
    @classmethod
    def image_to_base64(cls, image: np.ndarray, format: str = 'jpg') -> str:
        """
        Convert image array to base64 string
        
        Args:
            image: Image array
            format: Output format ('jpg', 'png')
            
        Returns:
            Base64 encoded string
        """
        if format == 'jpg':
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            _, buffer = cv2.imencode('.jpg', cls.convert_to_bgr(image), encode_param)
        else:
            _, buffer = cv2.imencode('.png', cls.convert_to_bgr(image))
        
        base64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/{format};base64,{base64_str}"
    
    @classmethod
    def base64_to_image(cls, base64_str: str) -> Optional[np.ndarray]:
        """
        Convert base64 string to image array
        
        Args:
            base64_str: Base64 encoded image string
            
        Returns:
            Image array or None if error
        """
        try:
            # Remove data URL prefix if present
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            
            # Decode base64
            img_data = base64.b64decode(base64_str)
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
        except Exception as e:
            current_app.logger.error(f"Base64 to image error: {str(e)}")
            return None
    
    @classmethod
    def get_image_info(cls, image: np.ndarray) -> dict:
        """
        Get information about an image
        
        Args:
            image: Input image array
            
        Returns:
            Dictionary with image information
        """
        info = {
            'shape': image.shape,
            'height': image.shape[0],
            'width': image.shape[1],
            'dtype': str(image.dtype),
            'min_value': float(np.min(image)),
            'max_value': float(np.max(image)),
            'mean_value': float(np.mean(image))
        }
        
        if len(image.shape) == 3:
            info['channels'] = image.shape[2]
            info['color_space'] = 'RGB' if image.shape[2] == 3 else 'RGBA'
        else:
            info['channels'] = 1
            info['color_space'] = 'Grayscale'
        
        return info
    
    @classmethod
    def validate_image(cls, image_path: str) -> dict:
        """
        Validate image file for model input
        
        Args:
            image_path: Path to image file
            
        Returns:
            Validation result dictionary
        """
        try:
            # Check if file exists
            import os
            if not os.path.exists(image_path):
                return {
                    'valid': False,
                    'error': 'File not found',
                    'message': f'Image file does not exist: {image_path}'
                }
            
            # Check file extension
            ext = image_path.split('.')[-1].lower()
            if ext not in cls.SUPPORTED_FORMATS:
                return {
                    'valid': False,
                    'error': 'Unsupported format',
                    'message': f'Unsupported image format: {ext}. Supported: {", ".join(cls.SUPPORTED_FORMATS)}'
                }
            
            # Check file size
            file_size = os.path.getsize(image_path)
            max_size = 16 * 1024 * 1024  # 16MB
            if file_size > max_size:
                return {
                    'valid': False,
                    'error': 'File too large',
                    'message': f'Image size {file_size // 1024}KB exceeds limit {max_size // 1024}KB'
                }
            
            # Try to load image
            img = cv2.imread(image_path)
            if img is None:
                return {
                    'valid': False,
                    'error': 'Corrupt image',
                    'message': 'Could not read image file. File may be corrupt.'
                }
            
            # Check minimum dimensions
            h, w = img.shape[:2]
            if h < 50 or w < 50:
                return {
                    'valid': False,
                    'error': 'Image too small',
                    'message': f'Image dimensions {w}x{h} are too small. Minimum 50x50 required.'
                }
            
            return {
                'valid': True,
                'width': w,
                'height': h,
                'file_size_kb': file_size // 1024,
                'format': ext
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': 'Validation error',
                'message': str(e)
            }
    
    @classmethod
    def extract_leaf_region(cls, image: np.ndarray) -> np.ndarray:
        """
        Extract leaf region from image using basic segmentation
        
        Args:
            image: Input image array
            
        Returns:
            Cropped leaf region
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply threshold to create mask
        _, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour (assumed to be the leaf)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            
            # Add padding
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            
            # Crop to leaf region
            leaf = image[y:y+h, x:x+w]
            return leaf
        
        return image
    
    @classmethod
    def enhance_image(cls, image: np.ndarray) -> np.ndarray:
        """
        Enhance image quality for better detection
        
        Args:
            image: Input image array
            
        Returns:
            Enhanced image
        """
        # Convert to LAB color space for better enhancement
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        # Merge back
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)
        
        # Sharpen image
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        enhanced = cv2.filter2D(enhanced, -1, kernel)
        
        return enhanced
"""
Data Service - Dataset Loading and Preprocessing Service
Handles dataset operations, data augmentation, and data validation
Supports 29 disease classes from PlantVillage dataset
"""

import os
import json
import random
import numpy as np
import cv2
from flask import current_app
from typing import Dict, Any, Tuple, List, Optional, Union
from datetime import datetime
import shutil
from tqdm import tqdm
import hashlib


class DataService:
    """
    Service for dataset management and preprocessing
    Handles dataset loading, splitting, augmentation, and validation
    """
    
    # 29 Class Names (PlantVillage Dataset)
    CLASS_NAMES = [
        # Apple (4)
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
        # Bell Pepper (2)
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
        # Cherry (2)
        'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew',
        # Corn/Maize (4)
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust',
        'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight',
        # Grape (4)
        'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        # Peach (2)
        'Peach___Bacterial_spot', 'Peach___healthy',
        # Potato (3)
        'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight',
        # Strawberry (2)
        'Strawberry___healthy', 'Strawberry___Leaf_scorch',
        # Tomato (6)
        'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy',
        'Tomato___Late_blight', 'Tomato___Septoria_leaf_spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
    ]
    
    # User-friendly display names
    DISPLAY_NAMES = {
        'Apple___Apple_scab': 'Apple Scab',
        'Apple___Black_rot': 'Apple Black Rot',
        'Apple___Cedar_apple_rust': 'Apple Cedar Rust',
        'Apple___healthy': 'Apple Healthy',
        'Pepper,_bell___Bacterial_spot': 'Bell Pepper Bacterial Spot',
        'Pepper,_bell___healthy': 'Bell Pepper Healthy',
        'Cherry_(including_sour)___healthy': 'Cherry Healthy',
        'Cherry_(including_sour)___Powdery_mildew': 'Cherry Powdery Mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Corn Cercospora Leaf Spot',
        'Corn_(maize)___Common_rust': 'Corn Common Rust',
        'Corn_(maize)___healthy': 'Corn Healthy',
        'Corn_(maize)___Northern_Leaf_Blight': 'Corn Northern Leaf Blight',
        'Grape___Black_rot': 'Grape Black Rot',
        'Grape___Esca_(Black_Measles)': 'Grape Esca',
        'Grape___healthy': 'Grape Healthy',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 'Grape Leaf Blight',
        'Peach___Bacterial_spot': 'Peach Bacterial Spot',
        'Peach___healthy': 'Peach Healthy',
        'Potato___Early_blight': 'Potato Early Blight',
        'Potato___healthy': 'Potato Healthy',
        'Potato___Late_blight': 'Potato Late Blight',
        'Strawberry___healthy': 'Strawberry Healthy',
        'Strawberry___Leaf_scorch': 'Strawberry Leaf Scorch',
        'Tomato___Bacterial_spot': 'Tomato Bacterial Spot',
        'Tomato___Early_blight': 'Tomato Early Blight',
        'Tomato___healthy': 'Tomato Healthy',
        'Tomato___Late_blight': 'Tomato Late Blight',
        'Tomato___Septoria_leaf_spot': 'Tomato Septoria Leaf Spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Tomato Yellow Leaf Curl Virus'
    }
    
    # Crop grouping
    CROP_GROUPS = {
        'Apple': ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy'],
        'Bell Pepper': ['Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy'],
        'Cherry': ['Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew'],
        'Corn': ['Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust',
                 'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight'],
        'Grape': ['Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)'],
        'Peach': ['Peach___Bacterial_spot', 'Peach___healthy'],
        'Potato': ['Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight'],
        'Strawberry': ['Strawberry___healthy', 'Strawberry___Leaf_scorch'],
        'Tomato': ['Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy',
                   'Tomato___Late_blight', 'Tomato___Septoria_leaf_spot', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus']
    }
    
    # Image file extensions
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG', '.bmp', '.tiff'}
    
    def __init__(self, config: Dict = None):
        """
        Initialize data service
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.dataset_path = self.config.get('dataset_path', 'dataset')
        self.train_split = self.config.get('train_split', 0.7)
        self.val_split = self.config.get('val_split', 0.2)
        self.test_split = self.config.get('test_split', 0.1)
        self.image_size = self.config.get('image_size', (224, 224))
        self.random_seed = self.config.get('random_seed', 42)
        self.use_symlinks = self.config.get('use_symlinks', False)  # Use symlinks instead of copying
        
        # Set random seed for reproducibility
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
    
    def _get_image_files(self, directory: str) -> List[str]:
        """
        Get all image files in a directory
        
        Args:
            directory: Directory path
            
        Returns:
            List of image file paths
        """
        images = []
        for f in os.listdir(directory):
            if any(f.lower().endswith(ext) for ext in self.IMAGE_EXTENSIONS):
                images.append(f)
        return images
    
    def get_dataset_info(self, data_dir: str = None) -> Dict:
        """
        Get information about the dataset
        
        Args:
            data_dir: Path to dataset directory
            
        Returns:
            Dictionary with dataset information
        """
        if data_dir is None:
            data_dir = self.dataset_path
        
        try:
            info = {
                'path': data_dir,
                'exists': os.path.exists(data_dir),
                'classes': [],
                'total_images': 0,
                'class_distribution': {},
                'crop_distribution': {},
                'image_format_stats': {}
            }
            
            if not os.path.exists(data_dir):
                info['error'] = f'Dataset path not found: {data_dir}'
                return info
            
            # Get all class directories
            class_dirs = [d for d in os.listdir(data_dir) 
                         if os.path.isdir(os.path.join(data_dir, d))]
            
            format_counts = {}
            
            for class_name in class_dirs:
                class_path = os.path.join(data_dir, class_name)
                images = self._get_image_files(class_path)
                
                # Count formats
                for img in images:
                    ext = os.path.splitext(img)[1].lower()
                    format_counts[ext] = format_counts.get(ext, 0) + 1
                
                info['classes'].append(class_name)
                info['class_distribution'][class_name] = len(images)
                info['total_images'] += len(images)
            
            info['image_format_stats'] = format_counts
            
            # Calculate crop distribution
            for crop, crop_classes in self.CROP_GROUPS.items():
                crop_images = 0
                for class_name in crop_classes:
                    if class_name in info['class_distribution']:
                        crop_images += info['class_distribution'][class_name]
                info['crop_distribution'][crop] = crop_images
            
            info['num_classes'] = len(info['classes'])
            info['avg_images_per_class'] = info['total_images'] / info['num_classes'] if info['num_classes'] > 0 else 0
            
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f"📊 Dataset Info:")
                current_app.logger.info(f"   Classes: {info['num_classes']}")
                current_app.logger.info(f"   Total Images: {info['total_images']}")
                current_app.logger.info(f"   Avg per class: {info['avg_images_per_class']:.1f}")
            
            return info
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error getting dataset info: {str(e)}")
            return {'error': str(e)}
    
    def split_dataset(self, source_dir: str, target_dir: str = None, 
                      force: bool = False, use_symlinks: bool = None) -> Dict:
        """
        Split dataset into train/validation/test sets
        
        Args:
            source_dir: Source dataset directory
            target_dir: Target directory for split data
            force: Force overwrite if exists
            use_symlinks: Use symlinks instead of copying (saves disk space)
            
        Returns:
            Dictionary with split statistics
        """
        if target_dir is None:
            target_dir = os.path.join(os.path.dirname(source_dir), 'split_dataset')
        
        use_symlinks = use_symlinks if use_symlinks is not None else self.use_symlinks
        
        try:
            # Check if target exists
            if os.path.exists(target_dir):
                if not force:
                    raise ValueError(f"Target directory exists. Use force=True to overwrite.")
                shutil.rmtree(target_dir)
            
            # Create target directories
            train_dir = os.path.join(target_dir, 'train')
            val_dir = os.path.join(target_dir, 'val')
            test_dir = os.path.join(target_dir, 'test')
            
            for split_dir in [train_dir, val_dir, test_dir]:
                os.makedirs(split_dir, exist_ok=True)
            
            # Get all class directories
            class_dirs = [d for d in os.listdir(source_dir) 
                         if os.path.isdir(os.path.join(source_dir, d))]
            
            split_stats = {}
            total_train = 0
            total_val = 0
            total_test = 0
            
            for class_name in tqdm(class_dirs, desc="Splitting dataset"):
                class_path = os.path.join(source_dir, class_name)
                images = self._get_image_files(class_path)
                
                # Shuffle images
                random.shuffle(images)
                
                # Calculate split indices
                n_train = int(len(images) * self.train_split)
                n_val = int(len(images) * self.val_split)
                
                train_images = images[:n_train]
                val_images = images[n_train:n_train + n_val]
                test_images = images[n_train + n_val:]
                
                split_stats[class_name] = {
                    'total': len(images),
                    'train': len(train_images),
                    'validation': len(val_images),
                    'test': len(test_images)
                }
                
                total_train += len(train_images)
                total_val += len(val_images)
                total_test += len(test_images)
                
                # Create class directories in splits
                train_class_dir = os.path.join(train_dir, class_name)
                val_class_dir = os.path.join(val_dir, class_name)
                test_class_dir = os.path.join(test_dir, class_name)
                
                os.makedirs(train_class_dir, exist_ok=True)
                os.makedirs(val_class_dir, exist_ok=True)
                os.makedirs(test_class_dir, exist_ok=True)
                
                # Copy or symlink images
                copy_func = os.symlink if use_symlinks else shutil.copy2
                
                for img in train_images:
                    src = os.path.join(class_path, img)
                    dst = os.path.join(train_class_dir, img)
                    if use_symlinks:
                        try:
                            os.symlink(src, dst)
                        except (OSError, NotImplementedError):
                            shutil.copy2(src, dst)
                    else:
                        shutil.copy2(src, dst)
                
                for img in val_images:
                    src = os.path.join(class_path, img)
                    dst = os.path.join(val_class_dir, img)
                    if use_symlinks:
                        try:
                            os.symlink(src, dst)
                        except (OSError, NotImplementedError):
                            shutil.copy2(src, dst)
                    else:
                        shutil.copy2(src, dst)
                
                for img in test_images:
                    src = os.path.join(class_path, img)
                    dst = os.path.join(test_class_dir, img)
                    if use_symlinks:
                        try:
                            os.symlink(src, dst)
                        except (OSError, NotImplementedError):
                            shutil.copy2(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
            # Save split info
            info = {
                'split_stats': split_stats,
                'total_classes': len(class_dirs),
                'split_ratios': {
                    'train': self.train_split,
                    'validation': self.val_split,
                    'test': self.test_split
                },
                'total_counts': {
                    'train': total_train,
                    'validation': total_val,
                    'test': total_test
                },
                'use_symlinks': use_symlinks,
                'created_at': datetime.now().isoformat()
            }
            
            info_path = os.path.join(target_dir, 'split_info.json')
            with open(info_path, 'w') as f:
                json.dump(info, f, indent=2)
            
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f"✅ Dataset split completed")
                current_app.logger.info(f"   Train: {total_train} images")
                current_app.logger.info(f"   Validation: {total_val} images")
                current_app.logger.info(f"   Test: {total_test} images")
            
            return info
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error splitting dataset: {str(e)}")
            raise
    
    def validate_dataset(self, data_dir: str = None) -> Dict:
        """
        Validate dataset structure and content
        
        Args:
            data_dir: Path to dataset directory
            
        Returns:
            Validation results dictionary
        """
        if data_dir is None:
            data_dir = self.dataset_path
        
        try:
            validation = {
                'success': True,
                'errors': [],
                'warnings': [],
                'class_info': {},
                'recommendations': []
            }
            
            if not os.path.exists(data_dir):
                validation['success'] = False
                validation['errors'].append(f"Dataset path not found: {data_dir}")
                return validation
            
            # Check for class directories
            class_dirs = [d for d in os.listdir(data_dir) 
                         if os.path.isdir(os.path.join(data_dir, d))]
            
            if len(class_dirs) == 0:
                validation['success'] = False
                validation['errors'].append("No class directories found")
                return validation
            
            # Validate each class
            min_images_warning = 50
            critical_min_images = 10
            
            for class_name in class_dirs:
                class_path = os.path.join(data_dir, class_name)
                images = self._get_image_files(class_path)
                display_name = self.DISPLAY_NAMES.get(class_name, class_name)
                
                validation['class_info'][class_name] = {
                    'display_name': display_name,
                    'image_count': len(images),
                    'path': class_path
                }
                
                if len(images) == 0:
                    validation['errors'].append(f"Class '{display_name}' has NO images")
                elif len(images) < critical_min_images:
                    validation['errors'].append(f"Class '{display_name}' has only {len(images)} images (<{critical_min_images})")
                elif len(images) < min_images_warning:
                    validation['warnings'].append(f"Class '{display_name}' has only {len(images)} images (recommend >{min_images_warning})")
            
            # Check for expected classes
            expected_classes = set(self.CLASS_NAMES)
            found_classes = set(class_dirs)
            missing_classes = expected_classes - found_classes
            extra_classes = found_classes - expected_classes
            
            if missing_classes:
                missing_names = [self.DISPLAY_NAMES.get(c, c) for c in missing_classes]
                validation['warnings'].append(f"Missing expected classes: {', '.join(missing_names)}")
                validation['recommendations'].append(f"Add training data for: {', '.join(missing_names)}")
            
            if extra_classes:
                extra_names = [self.DISPLAY_NAMES.get(c, c) for c in extra_classes]
                validation['warnings'].append(f"Extra classes found: {', '.join(extra_names)}")
            
            # Calculate statistics
            total_images = sum(info['image_count'] for info in validation['class_info'].values())
            validation['total_classes'] = len(class_dirs)
            validation['total_images'] = total_images
            validation['avg_images_per_class'] = total_images / len(class_dirs) if class_dirs else 0
            
            # Add recommendations based on analysis
            if validation['avg_images_per_class'] < 100:
                validation['recommendations'].append(
                    f"Average images per class is low ({validation['avg_images_per_class']:.0f}). "
                    "Consider data augmentation or collecting more data."
                )
            
            # Log results
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f"✅ Dataset validation completed")
                current_app.logger.info(f"   Classes: {validation['total_classes']}")
                current_app.logger.info(f"   Total Images: {validation['total_images']}")
                if validation['warnings']:
                    current_app.logger.warning(f"   Warnings: {len(validation['warnings'])}")
            
            return validation
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error validating dataset: {str(e)}")
            return {
                'success': False,
                'errors': [str(e)],
                'warnings': []
            }
    
    def apply_augmentation(self, image: np.ndarray, 
                          augmentation_type: str = 'basic',
                          return_params: bool = False) -> Union[np.ndarray, Tuple[np.ndarray, Dict]]:
        """
        Apply data augmentation to an image
        
        Args:
            image: Input image array (0-255 range)
            augmentation_type: Type of augmentation ('basic', 'heavy', 'none')
            return_params: Whether to return applied augmentation parameters
            
        Returns:
            Augmented image array or (image, params) tuple
        """
        if augmentation_type == 'none':
            return image if not return_params else (image, {})
        
        applied_params = {'type': augmentation_type, 'applied': []}
        
        try:
            img = image.copy()
            
            if augmentation_type == 'basic':
                # Basic augmentations
                if random.random() > 0.5:
                    img = cv2.flip(img, 1)  # Horizontal flip
                    applied_params['applied'].append('horizontal_flip')
                
                if random.random() > 0.7:
                    angle = random.uniform(-15, 15)
                    h, w = img.shape[:2]
                    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
                    img = cv2.warpAffine(img, M, (w, h))
                    applied_params['applied'].append(f'rotation_{angle:.1f}')
                
                if random.random() > 0.7:
                    scale = random.uniform(0.9, 1.1)
                    h, w = img.shape[:2]
                    new_h, new_w = int(h * scale), int(w * scale)
                    img = cv2.resize(img, (new_w, new_h))
                    img = cv2.resize(img, (w, h))
                    applied_params['applied'].append(f'scale_{scale:.2f}')
            
            elif augmentation_type == 'heavy':
                # Heavy augmentations for robustness
                if random.random() > 0.3:
                    img = cv2.flip(img, 1)
                    applied_params['applied'].append('horizontal_flip')
                
                if random.random() > 0.5:
                    angle = random.uniform(-30, 30)
                    h, w = img.shape[:2]
                    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
                    img = cv2.warpAffine(img, M, (w, h))
                    applied_params['applied'].append(f'rotation_{angle:.1f}')
                
                if random.random() > 0.5:
                    scale = random.uniform(0.7, 1.3)
                    h, w = img.shape[:2]
                    new_h, new_w = int(h * scale), int(w * scale)
                    img = cv2.resize(img, (new_w, new_h))
                    img = cv2.resize(img, (w, h))
                    applied_params['applied'].append(f'scale_{scale:.2f}')
                
                # Brightness adjustment
                if random.random() > 0.5:
                    brightness = random.uniform(0.6, 1.4)
                    img = np.clip(img * brightness, 0, 255).astype(np.uint8)
                    applied_params['applied'].append(f'brightness_{brightness:.2f}')
                
                # Contrast adjustment
                if random.random() > 0.7:
                    mean = np.mean(img)
                    contrast = random.uniform(0.7, 1.3)
                    img = np.clip((img - mean) * contrast + mean, 0, 255).astype(np.uint8)
                    applied_params['applied'].append(f'contrast_{contrast:.2f}')
            
            if return_params:
                return img, applied_params
            return img
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error applying augmentation: {str(e)}")
            return image if not return_params else (image, {})
    
    def get_class_weights(self, data_dir: str = None) -> Dict:
        """
        Calculate class weights for imbalanced dataset
        
        Args:
            data_dir: Path to dataset directory
            
        Returns:
            Dictionary of class weights
        """
        try:
            info = self.get_dataset_info(data_dir)
            if 'error' in info:
                raise ValueError(info['error'])
            
            total_images = info['total_images']
            num_classes = info['num_classes']
            
            if total_images == 0:
                return {}
            
            class_weights = {}
            for class_name, count in info['class_distribution'].items():
                weight = total_images / (num_classes * count)
                class_weights[class_name] = min(weight, 5.0)  # Cap at 5 to avoid extreme weights
            
            return class_weights
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error calculating class weights: {str(e)}")
            return {}
    
    def preprocess_image(self, image_path: str, 
                         target_size: Tuple[int, int] = None,
                         normalize: bool = True) -> Optional[np.ndarray]:
        """
        Preprocess a single image for model input
        
        Args:
            image_path: Path to image file
            target_size: Target size (width, height)
            normalize: Whether to normalize to [0, 1]
            
        Returns:
            Preprocessed image array
        """
        if target_size is None:
            target_size = self.image_size
        
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize
            img = cv2.resize(img, target_size)
            
            # Normalize if requested
            if normalize:
                img = img.astype('float32') / 255.0
            
            return img
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error preprocessing image: {str(e)}")
            return None
    
    def create_sample_dataset(self, output_dir: str, 
                              samples_per_class: int = 10,
                              image_size: Tuple[int, int] = (224, 224)) -> Dict:
        """
        Create a sample dataset for testing
        
        Args:
            output_dir: Output directory for sample dataset
            samples_per_class: Number of sample images per class
            image_size: Size of generated images
            
        Returns:
            Dictionary with creation statistics
        """
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            colors = [
                (50, 100, 150), (100, 150, 50), (150, 50, 100),
                (200, 100, 50), (50, 200, 100), (100, 50, 200),
                (180, 180, 50), (50, 180, 180), (180, 50, 180)
            ]
            
            created_count = 0
            
            for class_name in tqdm(self.CLASS_NAMES, desc="Creating samples"):
                class_dir = os.path.join(output_dir, class_name)
                os.makedirs(class_dir, exist_ok=True)
                
                # Create placeholder images
                for i in range(samples_per_class):
                    # Create a colored image
                    base_color = colors[hash(class_name) % len(colors)]
                    variation = random.randint(-30, 30)
                    color = tuple(max(0, min(255, c + variation)) for c in base_color)
                    img = np.ones((image_size[1], image_size[0], 3), dtype=np.uint8) * np.array(color, dtype=np.uint8)
                    
                    # Add noise for realism
                    noise = np.random.randint(0, 30, img.shape, dtype=np.uint8)
                    img = cv2.addWeighted(img, 0.8, noise, 0.2, 0)
                    
                    # Add text label
                    display_name = self.DISPLAY_NAMES.get(class_name, class_name)
                    text = display_name[:25]
                    
                    # Get text size
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 0.5
                    thickness = 1
                    (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
                    
                    # Center text
                    text_x = (image_size[0] - text_w) // 2
                    text_y = (image_size[1] + text_h) // 2
                    
                    # Add white background for text
                    cv2.rectangle(img, 
                                 (text_x - 5, text_y - text_h - 5),
                                 (text_x + text_w + 5, text_y + 5),
                                 (0, 0, 0), -1)
                    
                    # Add text
                    cv2.putText(img, text, (text_x, text_y), 
                               font, font_scale, (255, 255, 255), thickness)
                    
                    # Save image
                    img_path = os.path.join(class_dir, f'sample_{i+1:03d}.jpg')
                    cv2.imwrite(img_path, img)
                    created_count += 1
            
            result = {
                'success': True,
                'output_dir': output_dir,
                'num_classes': len(self.CLASS_NAMES),
                'samples_per_class': samples_per_class,
                'total_images': created_count,
                'image_size': list(image_size)
            }
            
            if hasattr(current_app, 'logger'):
                current_app.logger.info(f"✅ Sample dataset created at {output_dir}")
                current_app.logger.info(f"   Classes: {result['num_classes']}")
                current_app.logger.info(f"   Images: {result['total_images']}")
            
            return result
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error creating sample dataset: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_dataset_hash(self, data_dir: str = None) -> str:
        """
        Generate a hash of the dataset for version tracking
        
        Args:
            data_dir: Path to dataset directory
            
        Returns:
            SHA256 hash of dataset
        """
        if data_dir is None:
            data_dir = self.dataset_path
        
        try:
            if not os.path.exists(data_dir):
                return ""
            
            # Collect all image paths
            image_paths = []
            for root, dirs, files in os.walk(data_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.IMAGE_EXTENSIONS):
                        rel_path = os.path.relpath(os.path.join(root, file), data_dir)
                        image_paths.append(rel_path)
            
            # Sort for consistency
            image_paths.sort()
            
            # Create hash
            hash_input = ",".join(image_paths)
            return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
            
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error generating dataset hash: {str(e)}")
            return ""


# Singleton instance
data_service = DataService()
#!/usr/bin/env python3
"""
Preprocess Data Script
Preprocesses images for training the disease detection model
Includes resizing, normalization, augmentation, and validation
"""

import os
import sys
import argparse
import json
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import shutil
import random
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')


class DataPreprocessor:
    """
    Utility class for preprocessing image data for model training
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    # Target size for model input
    TARGET_SIZE = (224, 224)
    
    def __init__(self, input_dir='dataset', output_dir='dataset_processed', 
                 target_size=(224, 224), quality=95, validate=True):
        """
        Initialize the data preprocessor
        
        Args:
            input_dir: Input dataset directory
            output_dir: Output directory for processed data
            target_size: Target image size (width, height)
            quality: JPEG compression quality (1-100)
            validate: Whether to validate images
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.target_size = target_size
        self.quality = quality
        self.validate = validate
        
        # Create output directories
        self.train_out = self.output_dir / 'train'
        self.val_out = self.output_dir / 'validation'
        self.test_out = self.output_dir / 'test'
        
        self.stats = {
            'total_images': 0,
            'processed_images': 0,
            'skipped_images': 0,
            'corrupt_images': 0,
            'class_stats': {}
        }
    
    def validate_image(self, image_path):
        """
        Validate if an image can be read and is not corrupt
        
        Args:
            image_path: Path to image file
            
        Returns:
            tuple: (is_valid, image, error_message)
        """
        try:
            # Try to read image
            img = cv2.imread(str(image_path))
            if img is None:
                return False, None, "Could not read image"
            
            # Check if image has valid dimensions
            if img.shape[0] < 10 or img.shape[1] < 10:
                return False, None, f"Image too small: {img.shape}"
            
            # Check for all-black or all-white images
            if np.mean(img) < 5 or np.mean(img) > 250:
                return False, None, "Image is mostly black or white"
            
            return True, img, None
            
        except Exception as e:
            return False, None, str(e)
    
    def preprocess_image(self, img):
        """
        Preprocess a single image
        
        Args:
            img: Input image array
            
        Returns:
            Preprocessed image array
        """
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize image
        img_resized = cv2.resize(img_rgb, self.target_size, interpolation=cv2.INTER_LANCZOS4)
        
        return img_resized
    
    def augment_image(self, img, augmentation_type='basic'):
        """
        Apply data augmentation to image
        
        Args:
            img: Input image array
            augmentation_type: Type of augmentation ('basic', 'heavy', 'none')
            
        Returns:
            Augmented image array
        """
        if augmentation_type == 'none':
            return img
        
        img_aug = img.copy()
        
        if augmentation_type == 'basic':
            # Random horizontal flip (50% chance)
            if random.random() > 0.5:
                img_aug = cv2.flip(img_aug, 1)
            
            # Random rotation (±15 degrees)
            if random.random() > 0.7:
                angle = random.uniform(-15, 15)
                h, w = img_aug.shape[:2]
                M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
                img_aug = cv2.warpAffine(img_aug, M, (w, h))
            
            # Random brightness adjustment
            if random.random() > 0.7:
                factor = random.uniform(0.8, 1.2)
                img_aug = np.clip(img_aug * factor, 0, 255).astype(np.uint8)
        
        elif augmentation_type == 'heavy':
            # Random horizontal flip
            if random.random() > 0.3:
                img_aug = cv2.flip(img_aug, 1)
            
            # Random vertical flip
            if random.random() > 0.7:
                img_aug = cv2.flip(img_aug, 0)
            
            # Random rotation (±30 degrees)
            if random.random() > 0.5:
                angle = random.uniform(-30, 30)
                h, w = img_aug.shape[:2]
                M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
                img_aug = cv2.warpAffine(img_aug, M, (w, h))
            
            # Random brightness adjustment
            if random.random() > 0.5:
                factor = random.uniform(0.6, 1.4)
                img_aug = np.clip(img_aug * factor, 0, 255).astype(np.uint8)
            
            # Random contrast adjustment
            if random.random() > 0.7:
                mean = np.mean(img_aug)
                factor = random.uniform(0.7, 1.3)
                img_aug = np.clip((img_aug - mean) * factor + mean, 0, 255).astype(np.uint8)
        
        return img_aug
    
    def save_image(self, img, output_path, quality=95):
        """
        Save image to disk
        
        Args:
            img: Image array
            output_path: Output file path
            quality: JPEG quality (1-100)
        """
        # Convert RGB to BGR for OpenCV
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Determine format from extension
        if output_path.suffix.lower() in ['.jpg', '.jpeg']:
            cv2.imwrite(str(output_path), img_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
        else:
            cv2.imwrite(str(output_path), img_bgr)
    
    def process_split(self, split_dir, output_split_dir, apply_augmentation=False):
        """
        Process all images in a split directory
        
        Args:
            split_dir: Input split directory (train/validation/test)
            output_split_dir: Output directory for processed images
            apply_augmentation: Whether to apply augmentation (usually only for training)
        """
        if not split_dir.exists():
            print(f"⚠️ Directory not found: {split_dir}")
            return
        
        # Get all class directories
        class_dirs = [d for d in split_dir.iterdir() if d.is_dir()]
        
        print(f"\n📁 Processing {split_dir.name}...")
        
        for class_dir in tqdm(class_dirs, desc=f"Processing {split_dir.name}", ncols=80):
            class_name = class_dir.name
            output_class_dir = output_split_dir / class_name
            output_class_dir.mkdir(parents=True, exist_ok=True)
            
            # Get all images
            images = []
            for fmt in self.SUPPORTED_FORMATS:
                images.extend(class_dir.glob(f'*{fmt}'))
            
            if class_name not in self.stats['class_stats']:
                self.stats['class_stats'][class_name] = {
                    'original': 0,
                    'processed': 0,
                    'skipped': 0,
                    'corrupt': 0
                }
            
            self.stats['class_stats'][class_name]['original'] = len(images)
            
            for img_path in images:
                self.stats['total_images'] += 1
                
                # Validate image
                is_valid, img, error = self.validate_image(img_path)
                
                if not is_valid:
                    self.stats['corrupt_images'] += 1
                    self.stats['class_stats'][class_name]['corrupt'] += 1
                    print(f"⚠️ Corrupt image: {img_path} - {error}")
                    continue
                
                # Preprocess image
                try:
                    img_processed = self.preprocess_image(img)
                    
                    # Apply augmentation for training split
                    if apply_augmentation and split_dir.name == 'train':
                        # Save original
                        output_path = output_class_dir / f"{img_path.stem}_processed{img_path.suffix}"
                        self.save_image(img_processed, output_path, self.quality)
                        self.stats['processed_images'] += 1
                        self.stats['class_stats'][class_name]['processed'] += 1
                        
                        # Generate augmented versions
                        for aug_idx in range(3):  # 3 augmented versions per image
                            img_aug = self.augment_image(img_processed, 'basic')
                            aug_path = output_class_dir / f"{img_path.stem}_aug{aug_idx+1}{img_path.suffix}"
                            self.save_image(img_aug, aug_path, self.quality)
                            self.stats['processed_images'] += 1
                            self.stats['class_stats'][class_name]['processed'] += 1
                    else:
                        # Just save the processed image
                        output_path = output_class_dir / f"{img_path.stem}_processed{img_path.suffix}"
                        self.save_image(img_processed, output_path, self.quality)
                        self.stats['processed_images'] += 1
                        self.stats['class_stats'][class_name]['processed'] += 1
                    
                except Exception as e:
                    self.stats['skipped_images'] += 1
                    self.stats['class_stats'][class_name]['skipped'] += 1
                    print(f"⚠️ Error processing {img_path}: {str(e)}")
    
    def run(self, augment_training=True):
        """
        Run the complete preprocessing pipeline
        
        Args:
            augment_training: Whether to apply augmentation to training data
        """
        print("\n" + "="*70)
        print("🖼️  Image Preprocessing Pipeline")
        print("="*70)
        print(f"\n📂 Input directory: {self.input_dir}")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"📏 Target size: {self.target_size}")
        print(f"🎨 JPEG Quality: {self.quality}")
        print(f"🔍 Validation: {self.validate}")
        print(f"🔄 Augmentation: {augment_training}")
        
        # Check if input directory exists
        if not self.input_dir.exists():
            print(f"\n❌ Input directory not found: {self.input_dir}")
            return False
        
        # Process train, validation, and test splits
        train_input = self.input_dir / 'train'
        val_input = self.input_dir / 'validation'
        test_input = self.input_dir / 'test'
        
        # If the dataset is not split yet, use the whole directory
        if not train_input.exists():
            print("\n⚠️ Dataset not split. Using entire directory as source...")
            self.process_split(self.input_dir, self.train_out, apply_augmentation=augment_training)
        else:
            # Process each split
            self.process_split(train_input, self.train_out, apply_augmentation=augment_training)
            self.process_split(val_input, self.val_out, apply_augmentation=False)
            self.process_split(test_input, self.test_out, apply_augmentation=False)
        
        # Save preprocessing statistics
        self.save_statistics()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def save_statistics(self):
        """
        Save preprocessing statistics to JSON file
        """
        stats_file = self.output_dir / 'preprocessing_stats.json'
        
        # Calculate total original images
        total_original = sum(cls['original'] for cls in self.stats['class_stats'].values())
        
        stats = {
            'timestamp': str(Path(__file__).stat().st_ctime),
            'target_size': self.target_size,
            'jpeg_quality': self.quality,
            'augmentation_applied': True,
            'total_original_images': total_original,
            'total_processed_images': self.stats['processed_images'],
            'corrupt_images': self.stats['corrupt_images'],
            'skipped_images': self.stats['skipped_images'],
            'augmentation_multiplier': self.stats['processed_images'] / total_original if total_original > 0 else 0,
            'class_stats': self.stats['class_stats']
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n✅ Preprocessing statistics saved to {stats_file}")
    
    def print_summary(self):
        """
        Print preprocessing summary
        """
        print("\n" + "="*70)
        print("📊 Preprocessing Summary")
        print("="*70)
        
        total_original = sum(cls['original'] for cls in self.stats['class_stats'].values())
        
        print(f"\n📈 Statistics:")
        print(f"   Original Images: {total_original}")
        print(f"   Processed Images: {self.stats['processed_images']}")
        print(f"   Corrupt Images: {self.stats['corrupt_images']}")
        print(f"   Skipped Images: {self.stats['skipped_images']}")
        
        if total_original > 0:
            multiplier = self.stats['processed_images'] / total_original
            print(f"   Augmentation Multiplier: {multiplier:.1f}x")
        
        print(f"\n📂 Output Structure:")
        print(f"   {self.train_out}/ - Processed training images")
        print(f"   {self.val_out}/ - Processed validation images")
        print(f"   {self.test_out}/ - Processed test images")
        
        print(f"\n✅ Preprocessing complete!")
    
    def create_sample_images(self, num_samples=5):
        """
        Create sample images for verification
        
        Args:
            num_samples: Number of sample images per class
        """
        print(f"\n📸 Creating {num_samples} sample images per class...")
        
        sample_dir = self.output_dir / 'samples'
        sample_dir.mkdir(parents=True, exist_ok=True)
        
        for class_name, class_stats in self.stats['class_stats'].items():
            class_sample_dir = sample_dir / class_name
            class_sample_dir.mkdir(parents=True, exist_ok=True)
            
            # Find processed images for this class
            processed_class_dir = self.train_out / class_name
            if not processed_class_dir.exists():
                processed_class_dir = self.val_out / class_name
            if not processed_class_dir.exists():
                processed_class_dir = self.test_out / class_name
            
            if processed_class_dir.exists():
                images = list(processed_class_dir.glob('*'))
                for i, img_path in enumerate(images[:num_samples]):
                    shutil.copy2(img_path, class_sample_dir / img_path.name)
        
        print(f"✅ Sample images saved to {sample_dir}")


def main():
    parser = argparse.ArgumentParser(description='Preprocess image dataset for model training')
    parser.add_argument('--input', '-i', default='dataset',
                       help='Input dataset directory (default: dataset)')
    parser.add_argument('--output', '-o', default='dataset_processed',
                       help='Output directory for processed dataset (default: dataset_processed)')
    parser.add_argument('--size', '-s', default='224,224',
                       help='Target image size (width,height) (default: 224,224)')
    parser.add_argument('--quality', '-q', type=int, default=95,
                       help='JPEG compression quality 1-100 (default: 95)')
    parser.add_argument('--no-augment', action='store_true',
                       help='Disable data augmentation')
    parser.add_argument('--no-validate', action='store_true',
                       help='Disable image validation')
    parser.add_argument('--samples', type=int, default=0,
                       help='Create sample images (number per class)')
    
    args = parser.parse_args()
    
    # Parse target size
    try:
        target_size = tuple(map(int, args.size.split(',')))
        if len(target_size) != 2:
            raise ValueError
    except:
        print("❌ Invalid size format. Use: width,height (e.g., 224,224)")
        sys.exit(1)
    
    # Create preprocessor
    preprocessor = DataPreprocessor(
        input_dir=args.input,
        output_dir=args.output,
        target_size=target_size,
        quality=args.quality,
        validate=not args.no_validate
    )
    
    # Run preprocessing
    success = preprocessor.run(augment_training=not args.no_augment)
    
    if not success:
        print("\n❌ Preprocessing failed.")
        sys.exit(1)
    
    # Create sample images if requested
    if args.samples > 0:
        preprocessor.create_sample_images(args.samples)
    
    print("\n🎉 Preprocessing complete! Data is ready for training.")


if __name__ == '__main__':
    main()
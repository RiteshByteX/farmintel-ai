#!/usr/bin/env python3
"""
Data Augmentation Script
Augments image dataset for training the disease detection model
Creates additional training samples through various transformations
"""

import os
import sys
import argparse
import json
import cv2
import numpy as np
from pathlib import Path
from tqdm import tqdm
import random
from multiprocessing import Pool, cpu_count
import warnings
warnings.filterwarnings('ignore')


class DataAugmenter:
    """
    Utility class for augmenting image data for model training
    """
    
    # Supported image formats
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG'}
    
    def __init__(self, input_dir='dataset/train', output_dir='dataset_augmented', 
                 augmentations_per_image=5, target_size=(224, 224), quality=95):
        """
        Initialize the data augmenter
        
        Args:
            input_dir: Input dataset directory (should contain class subdirectories)
            output_dir: Output directory for augmented data
            augmentations_per_image: Number of augmented versions per image
            target_size: Target image size (width, height)
            quality: JPEG compression quality (1-100)
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.augmentations_per_image = augmentations_per_image
        self.target_size = target_size
        self.quality = quality
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.stats = {
            'total_classes': 0,
            'total_original_images': 0,
            'total_augmented_images': 0,
            'class_stats': {}
        }
    
    def random_brightness(self, img, factor_range=(0.7, 1.3)):
        """Adjust image brightness randomly"""
        factor = random.uniform(*factor_range)
        return np.clip(img * factor, 0, 255).astype(np.uint8)
    
    def random_contrast(self, img, factor_range=(0.7, 1.3)):
        """Adjust image contrast randomly"""
        mean = np.mean(img)
        factor = random.uniform(*factor_range)
        return np.clip((img - mean) * factor + mean, 0, 255).astype(np.uint8)
    
    def random_rotation(self, img, angle_range=(-30, 30)):
        """Rotate image randomly"""
        angle = random.uniform(*angle_range)
        h, w = img.shape[:2]
        M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
        return cv2.warpAffine(img, M, (w, h))
    
    def random_flip(self, img):
        """Flip image randomly horizontally or vertically"""
        flip_type = random.choice(['none', 'horizontal', 'vertical', 'both'])
        if flip_type == 'horizontal':
            return cv2.flip(img, 1)
        elif flip_type == 'vertical':
            return cv2.flip(img, 0)
        elif flip_type == 'both':
            return cv2.flip(cv2.flip(img, 1), 0)
        return img
    
    def random_scale(self, img, scale_range=(0.8, 1.2)):
        """Scale image randomly"""
        scale = random.uniform(*scale_range)
        h, w = img.shape[:2]
        new_h, new_w = int(h * scale), int(w * scale)
        scaled = cv2.resize(img, (new_w, new_h))
        
        # Center crop or pad to original size
        if scale > 1:
            # Crop to original size
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            return scaled[start_h:start_h+h, start_w:start_w+w]
        else:
            # Pad to original size
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            padded = np.zeros((h, w, 3), dtype=np.uint8)
            padded[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = scaled
            return padded
    
    def random_shift(self, img, shift_range=(-0.1, 0.1)):
        """Shift image randomly"""
        h, w = img.shape[:2]
        shift_x = int(w * random.uniform(*shift_range))
        shift_y = int(h * random.uniform(*shift_range))
        
        M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
        return cv2.warpAffine(img, M, (w, h))
    
    def random_noise(self, img, noise_level=0.02):
        """Add random Gaussian noise"""
        noise = np.random.normal(0, noise_level * 255, img.shape).astype(np.uint8)
        return np.clip(img + noise, 0, 255).astype(np.uint8)
    
    def random_blur(self, img, kernel_size_range=(3, 7)):
        """Apply random Gaussian blur"""
        kernel_size = random.choice([3, 5, 7])
        return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)
    
    def random_saturation(self, img, factor_range=(0.5, 1.5)):
        """Adjust image saturation randomly"""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        factor = random.uniform(*factor_range)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * factor, 0, 255).astype(np.uint8)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    def random_hue(self, img, shift_range=(-10, 10)):
        """Shift hue randomly"""
        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        shift = random.uniform(*shift_range)
        hsv[:, :, 0] = (hsv[:, :, 0] + shift) % 180
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    def apply_augmentations(self, img):
        """
        Apply a random set of augmentations to an image
        
        Args:
            img: Input image array
            
        Returns:
            Augmented image array
        """
        # List of available augmentations with probabilities
        augmentations = [
            (self.random_brightness, 0.7),
            (self.random_contrast, 0.6),
            (self.random_rotation, 0.5),
            (self.random_flip, 0.7),
            (self.random_scale, 0.4),
            (self.random_shift, 0.4),
            (self.random_noise, 0.3),
            (self.random_blur, 0.2),
            (self.random_saturation, 0.5),
            (self.random_hue, 0.3)
        ]
        
        augmented = img.copy()
        
        # Apply random augmentations based on probabilities
        for aug_func, prob in augmentations:
            if random.random() < prob:
                try:
                    augmented = aug_func(augmented)
                except Exception as e:
                    # Skip augmentation if it fails
                    pass
        
        return augmented
    
    def process_class(self, class_dir):
        """
        Process all images in a class directory
        
        Args:
            class_dir: Path to class directory
            
        Returns:
            dict: Statistics for this class
        """
        class_name = class_dir.name
        output_class_dir = self.output_dir / class_name
        output_class_dir.mkdir(parents=True, exist_ok=True)
        
        # Get all images
        images = []
        for fmt in self.SUPPORTED_FORMATS:
            images.extend(class_dir.glob(f'*{fmt}'))
        
        class_stats = {
            'original_count': len(images),
            'augmented_count': 0,
            'files': []
        }
        
        for img_path in tqdm(images, desc=f"Augmenting {class_name}", leave=False):
            # Read image
            img = cv2.imread(str(img_path))
            if img is None:
                print(f"⚠️ Could not read: {img_path}")
                continue
            
            # Convert BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to target size
            img = cv2.resize(img, self.target_size)
            
            # Save original image
            output_path = output_class_dir / f"{img_path.stem}_original{img_path.suffix}"
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(output_path), img_bgr, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            class_stats['files'].append(str(output_path))
            
            # Generate augmented versions
            for aug_idx in range(self.augmentations_per_image):
                try:
                    augmented = self.apply_augmentations(img)
                    aug_path = output_class_dir / f"{img_path.stem}_aug{aug_idx+1:02d}{img_path.suffix}"
                    aug_bgr = cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR)
                    cv2.imwrite(str(aug_path), aug_bgr, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                    class_stats['files'].append(str(aug_path))
                    class_stats['augmented_count'] += 1
                except Exception as e:
                    print(f"⚠️ Augmentation failed for {img_path}: {str(e)}")
        
        return class_name, class_stats
    
    def run(self, use_multiprocessing=True):
        """
        Run the complete augmentation pipeline
        
        Args:
            use_multiprocessing: Whether to use multiprocessing for faster processing
        """
        print("\n" + "="*70)
        print("🔄 Data Augmentation Pipeline")
        print("="*70)
        print(f"\n📂 Input directory: {self.input_dir}")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"📏 Target size: {self.target_size}")
        print(f"🖼️  Augmentations per image: {self.augmentations_per_image}")
        print(f"🎨 JPEG Quality: {self.quality}")
        
        # Check if input directory exists
        if not self.input_dir.exists():
            print(f"\n❌ Input directory not found: {self.input_dir}")
            return False
        
        # Get all class directories
        class_dirs = [d for d in self.input_dir.iterdir() if d.is_dir()]
        self.stats['total_classes'] = len(class_dirs)
        
        if len(class_dirs) == 0:
            print(f"\n❌ No class directories found in {self.input_dir}")
            return False
        
        print(f"\n📁 Found {len(class_dirs)} classes")
        
        # Process each class
        if use_multiprocessing and len(class_dirs) > 1:
            # Use multiprocessing for faster processing
            num_workers = min(cpu_count(), len(class_dirs))
            print(f"🚀 Using {num_workers} workers for parallel processing")
            
            with Pool(num_workers) as pool:
                results = []
                for class_dir in class_dirs:
                    results.append(pool.apply_async(self.process_class, (class_dir,)))
                
                for result in tqdm(results, desc="Processing classes", ncols=80):
                    class_name, class_stats = result.get()
                    self.stats['class_stats'][class_name] = class_stats
                    self.stats['total_original_images'] += class_stats['original_count']
                    self.stats['total_augmented_images'] += class_stats['augmented_count']
        else:
            # Process sequentially
            for class_dir in tqdm(class_dirs, desc="Processing classes", ncols=80):
                class_name, class_stats = self.process_class(class_dir)
                self.stats['class_stats'][class_name] = class_stats
                self.stats['total_original_images'] += class_stats['original_count']
                self.stats['total_augmented_images'] += class_stats['augmented_count']
        
        # Save statistics
        self.save_statistics()
        
        # Print summary
        self.print_summary()
        
        return True
    
    def save_statistics(self):
        """
        Save augmentation statistics to JSON file
        """
        stats_file = self.output_dir / 'augmentation_stats.json'
        
        stats = {
            'timestamp': str(Path(__file__).stat().st_ctime),
            'target_size': self.target_size,
            'jpeg_quality': self.quality,
            'augmentations_per_image': self.augmentations_per_image,
            'total_classes': self.stats['total_classes'],
            'total_original_images': self.stats['total_original_images'],
            'total_augmented_images': self.stats['total_augmented_images'],
            'augmentation_multiplier': self.stats['total_augmented_images'] / self.stats['total_original_images'] if self.stats['total_original_images'] > 0 else 0,
            'class_stats': self.stats['class_stats']
        }
        
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"\n✅ Augmentation statistics saved to {stats_file}")
    
    def print_summary(self):
        """
        Print augmentation summary
        """
        print("\n" + "="*70)
        print("📊 Augmentation Summary")
        print("="*70)
        
        print(f"\n📈 Statistics:")
        print(f"   Total Classes: {self.stats['total_classes']}")
        print(f"   Original Images: {self.stats['total_original_images']}")
        print(f"   Augmented Images: {self.stats['total_augmented_images']}")
        
        if self.stats['total_original_images'] > 0:
            multiplier = self.stats['total_augmented_images'] / self.stats['total_original_images']
            print(f"   Augmentation Multiplier: {multiplier:.1f}x")
            print(f"   Final Dataset Size: {self.stats['total_original_images'] + self.stats['total_augmented_images']} images")
        
        print(f"\n📂 Output Location: {self.output_dir}")
        
        print(f"\n✅ Augmentation complete!")
    
    def create_balanced_dataset(self, target_per_class=1000):
        """
        Create a balanced dataset with target number of images per class
        
        Args:
            target_per_class: Target number of images per class
        """
        print(f"\n⚖️ Creating balanced dataset with {target_per_class} images per class...")
        
        balanced_dir = self.output_dir.parent / f"{self.output_dir.name}_balanced"
        balanced_dir.mkdir(parents=True, exist_ok=True)
        
        for class_name, class_stats in self.stats['class_stats'].items():
            current_count = class_stats['original_count'] + class_stats['augmented_count']
            
            if current_count >= target_per_class:
                # Randomly select target_per_class images
                import random
                files = class_stats['files']
                selected = random.sample(files, target_per_class)
            else:
                # Need to generate more augmentations
                selected = class_stats['files'].copy()
                needed = target_per_class - current_count
                
                # Generate additional augmentations
                class_dir = self.input_dir / class_name
                original_images = [f for f in class_dir.iterdir() if f.suffix.lower() in self.SUPPORTED_FORMATS]
                
                for i in range(needed):
                    # Pick a random original image and augment it
                    img_path = random.choice(original_images)
                    img = cv2.imread(str(img_path))
                    if img is not None:
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img = cv2.resize(img, self.target_size)
                        augmented = self.apply_augmentations(img)
                        
                        aug_path = balanced_dir / class_name / f"extra_aug_{i:03d}{img_path.suffix}"
                        aug_path.parent.mkdir(parents=True, exist_ok=True)
                        aug_bgr = cv2.cvtColor(augmented, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(str(aug_path), aug_bgr, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                        selected.append(str(aug_path))
            
            # Copy selected files to balanced directory
            class_balanced_dir = balanced_dir / class_name
            class_balanced_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in selected:
                src = Path(file_path)
                dst = class_balanced_dir / src.name
                import shutil
                shutil.copy2(src, dst)
            
            print(f"   {class_name}: {len(selected)} images")
        
        print(f"\n✅ Balanced dataset saved to {balanced_dir}")


def main():
    parser = argparse.ArgumentParser(description='Augment image dataset for model training')
    parser.add_argument('--input', '-i', default='dataset/train',
                       help='Input dataset directory (default: dataset/train)')
    parser.add_argument('--output', '-o', default='dataset_augmented',
                       help='Output directory for augmented dataset (default: dataset_augmented)')
    parser.add_argument('--num-aug', '-n', type=int, default=5,
                       help='Number of augmentations per image (default: 5)')
    parser.add_argument('--size', '-s', default='224,224',
                       help='Target image size (width,height) (default: 224,224)')
    parser.add_argument('--quality', '-q', type=int, default=95,
                       help='JPEG compression quality 1-100 (default: 95)')
    parser.add_argument('--no-multiprocessing', action='store_true',
                       help='Disable multiprocessing')
    parser.add_argument('--balanced', type=int, default=0,
                       help='Create balanced dataset with target images per class')
    
    args = parser.parse_args()
    
    # Parse target size
    try:
        target_size = tuple(map(int, args.size.split(',')))
        if len(target_size) != 2:
            raise ValueError
    except:
        print("❌ Invalid size format. Use: width,height (e.g., 224,224)")
        sys.exit(1)
    
    # Create augmenter
    augmenter = DataAugmenter(
        input_dir=args.input,
        output_dir=args.output,
        augmentations_per_image=args.num_aug,
        target_size=target_size,
        quality=args.quality
    )
    
    # Run augmentation
    success = augmenter.run(use_multiprocessing=not args.no_multiprocessing)
    
    if not success:
        print("\n❌ Augmentation failed.")
        sys.exit(1)
    
    # Create balanced dataset if requested
    if args.balanced > 0:
        augmenter.create_balanced_dataset(target_per_class=args.balanced)
    
    print("\n🎉 Augmentation complete! Data is ready for training.")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Download Dataset Script
Downloads the PlantVillage dataset for training the disease detection model
Supports 29 disease classes across 9 crops
Can also use an existing dataset from a specified path
"""

import os
import sys
import zipfile
import requests
import argparse
from tqdm import tqdm
from pathlib import Path
import shutil
import json


class DatasetDownloader:
    """
    Utility class for downloading and extracting the PlantVillage dataset
    """
    
    # Dataset information
    DATASET_URLS = {
        'plantvillage': 'https://github.com/spMohanty/PlantVillage-Dataset/raw/master/raw/color.zip',
        'plantvillage_grayscale': 'https://github.com/spMohanty/PlantVillage-Dataset/raw/master/raw/grayscale.zip',
        'plantvillage_segmented': 'https://github.com/spMohanty/PlantVillage-Dataset/raw/master/raw/segmented.zip',
        'alternative': 'https://storage.googleapis.com/kaggle-data-sets/145971/334784/bundle/archive.zip'
    }
    
    # Expected classes (29 classes)
    EXPECTED_CLASSES = [
        'Apple___Apple_scab',
        'Apple___Black_rot',
        'Apple___Cedar_apple_rust',
        'Apple___healthy',
        'Pepper,_bell___Bacterial_spot',
        'Pepper,_bell___healthy',
        'Cherry_(including_sour)___healthy',
        'Cherry_(including_sour)___Powdery_mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust',
        'Corn_(maize)___healthy',
        'Corn_(maize)___Northern_Leaf_Blight',
        'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)',
        'Grape___healthy',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Peach___Bacterial_spot',
        'Peach___healthy',
        'Potato___Early_blight',
        'Potato___healthy',
        'Potato___Late_blight',
        'Strawberry___healthy',
        'Strawberry___Leaf_scorch',
        'Tomato___Bacterial_spot',
        'Tomato___Early_blight',
        'Tomato___healthy',
        'Tomato___Late_blight',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
    ]
    
    def __init__(self, output_dir='dataset', existing_dataset_path=None):
        """
        Initialize the dataset downloader
        
        Args:
            output_dir: Directory to store the dataset
            existing_dataset_path: Path to an existing dataset (skip download)
        """
        self.output_dir = Path(output_dir)
        self.download_dir = self.output_dir / 'downloads'
        self.train_dir = self.output_dir / 'train'
        self.val_dir = self.output_dir / 'validation'
        self.test_dir = self.output_dir / 'test'
        self.existing_dataset_path = Path(existing_dataset_path) if existing_dataset_path else None
        
        # Create directories
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.train_dir.mkdir(parents=True, exist_ok=True)
        self.val_dir.mkdir(parents=True, exist_ok=True)
        self.test_dir.mkdir(parents=True, exist_ok=True)
    
    def use_existing_dataset(self):
        """
        Use an existing dataset from the provided path
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.existing_dataset_path or not self.existing_dataset_path.exists():
            print(f"❌ Existing dataset path not found: {self.existing_dataset_path}")
            return False
        
        print(f"\n📁 Using existing dataset from: {self.existing_dataset_path}")
        
        # Check if the existing dataset has the expected structure
        # It should have class subdirectories
        class_dirs = [d for d in self.existing_dataset_path.iterdir() if d.is_dir()]
        
        # Check if any expected classes are present
        found_classes = []
        for class_name in self.EXPECTED_CLASSES:
            for d in class_dirs:
                if class_name in d.name or d.name in class_name:
                    found_classes.append(class_name)
                    break
        
        if len(found_classes) == 0:
            print(f"⚠️ No expected classes found in {self.existing_dataset_path}")
            print("   The dataset should have class subdirectories like:")
            print("   - Apple___Apple_scab/")
            print("   - Tomato___Late_blight/")
            print("   - etc.")
            return False
        
        print(f"✅ Found {len(found_classes)}/{len(self.EXPECTED_CLASSES)} expected classes")
        
        # Organize the existing dataset
        stats = self.organize_dataset(source_dir=self.existing_dataset_path)
        
        # Create info files
        self.create_dataset_info(stats)
        self.create_class_indices()
        
        # Print summary
        self.print_summary(stats)
        
        return True
    
    def download_file(self, url, filename, chunk_size=8192):
        """
        Download a file with progress bar
        
        Args:
            url: URL to download from
            filename: Local filename to save
            chunk_size: Download chunk size
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Send request
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            # Get file size
            total_size = int(response.headers.get('content-length', 0))
            filepath = self.download_dir / filename
            
            # Download with progress bar
            with open(filepath, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                         desc=f"Downloading {filename}", ncols=80) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            
            print(f"✅ Downloaded: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {str(e)}")
            return False
    
    def extract_zip(self, zip_path, extract_to):
        """
        Extract a zip file
        
        Args:
            zip_path: Path to zip file
            extract_to: Directory to extract to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get total files for progress
                total_files = len(zip_ref.namelist())
                
                with tqdm(total=total_files, unit='file', 
                         desc=f"Extracting {zip_path.name}", ncols=80) as pbar:
                    for file in zip_ref.namelist():
                        zip_ref.extract(file, extract_to)
                        pbar.update(1)
            
            print(f"✅ Extracted: {zip_path.name}")
            return True
            
        except Exception as e:
            print(f"❌ Extraction failed: {str(e)}")
            return False
    
    def organize_dataset(self, source_dir=None):
        """
        Organize the extracted dataset into train/val/test structure
        
        Args:
            source_dir: Source directory containing class subdirectories (optional)
        
        Returns:
            dict: Statistics about the organized dataset
        """
        print("\n📁 Organizing dataset into train/val/test splits...")
        
        # Determine source directory
        if source_dir is None:
            # Find extracted directory
            extracted_dirs = [d for d in self.download_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                # Look for color folder
                color_dir = self.download_dir / 'color'
                if color_dir.exists():
                    source_dir = color_dir
                else:
                    source_dir = self.download_dir
            else:
                source_dir = extracted_dirs[0]
        
        print(f"   Source: {source_dir}")
        
        stats = {}
        
        for class_name in self.EXPECTED_CLASSES:
            # Find the class directory
            class_dir = None
            for d in source_dir.iterdir():
                if d.is_dir() and (class_name in d.name or d.name in class_name):
                    class_dir = d
                    break
            
            if class_dir is None:
                print(f"⚠️ Warning: Could not find class directory for {class_name}")
                continue
            
            # Get all images
            images = list(class_dir.glob('*.JPG')) + list(class_dir.glob('*.jpg')) + \
                     list(class_dir.glob('*.JPEG')) + list(class_dir.glob('*.jpeg')) + \
                     list(class_dir.glob('*.PNG')) + list(class_dir.glob('*.png'))
            
            if len(images) == 0:
                print(f"⚠️ Warning: No images found for {class_name}")
                continue
            
            # Shuffle images for random split
            import random
            random.seed(42)
            random.shuffle(images)
            
            # Calculate split sizes
            total = len(images)
            train_count = int(total * 0.7)
            val_count = int(total * 0.2)
            test_count = total - train_count - val_count
            
            # Create class directories
            train_class_dir = self.train_dir / class_name
            val_class_dir = self.val_dir / class_name
            test_class_dir = self.test_dir / class_name
            
            train_class_dir.mkdir(parents=True, exist_ok=True)
            val_class_dir.mkdir(parents=True, exist_ok=True)
            test_class_dir.mkdir(parents=True, exist_ok=True)
            
            # Split and copy images
            for i, img in enumerate(images):
                if i < train_count:
                    shutil.copy2(img, train_class_dir / img.name)
                elif i < train_count + val_count:
                    shutil.copy2(img, val_class_dir / img.name)
                else:
                    shutil.copy2(img, test_class_dir / img.name)
            
            stats[class_name] = {
                'total': total,
                'train': train_count,
                'validation': val_count,
                'test': test_count
            }
            
            print(f"   {class_name}: {total} images (Train: {train_count}, Val: {val_count}, Test: {test_count})")
        
        return stats
    
    def create_dataset_info(self, stats):
        """
        Create dataset information JSON file
        
        Args:
            stats: Dataset statistics dictionary
        """
        info = {
            'version': '1.0.0',
            'created_at': str(Path(__file__).stat().st_ctime),
            'total_classes': len(stats),
            'total_images': sum(s['total'] for s in stats.values()),
            'class_distribution': stats,
            'split_ratios': {
                'train': 0.7,
                'validation': 0.2,
                'test': 0.1
            },
            'class_names': self.EXPECTED_CLASSES,
            'crop_groups': {
                'Apple': [c for c in self.EXPECTED_CLASSES if c.startswith('Apple')],
                'Bell Pepper': [c for c in self.EXPECTED_CLASSES if 'Pepper' in c],
                'Cherry': [c for c in self.EXPECTED_CLASSES if c.startswith('Cherry')],
                'Corn': [c for c in self.EXPECTED_CLASSES if c.startswith('Corn')],
                'Grape': [c for c in self.EXPECTED_CLASSES if c.startswith('Grape')],
                'Peach': [c for c in self.EXPECTED_CLASSES if c.startswith('Peach')],
                'Potato': [c for c in self.EXPECTED_CLASSES if c.startswith('Potato')],
                'Strawberry': [c for c in self.EXPECTED_CLASSES if c.startswith('Strawberry')],
                'Tomato': [c for c in self.EXPECTED_CLASSES if c.startswith('Tomato')]
            }
        }
        
        # Save info
        info_path = self.output_dir / 'dataset_info.json'
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"\n✅ Dataset info saved to {info_path}")
    
    def create_class_indices(self):
        """
        Create class indices mapping JSON file
        """
        class_indices = {name: idx for idx, name in enumerate(self.EXPECTED_CLASSES)}
        
        indices_path = self.output_dir / 'class_indices.json'
        with open(indices_path, 'w') as f:
            json.dump(class_indices, f, indent=2)
        
        print(f"✅ Class indices saved to {indices_path}")
    
    def download_plantvillage(self, source='plantvillage'):
        """
        Download PlantVillage dataset from the specified source
        
        Args:
            source: Source name ('plantvillage', 'alternative')
        """
        print("\n" + "="*70)
        print("🌾 Downloading PlantVillage Dataset")
        print("="*70)
        
        # Get URL
        url = self.DATASET_URLS.get(source)
        if not url:
            print(f"❌ Unknown source: {source}")
            return False
        
        # Download the zip file
        zip_filename = "plantvillage_dataset.zip"
        if not self.download_file(url, zip_filename):
            # Try alternative source
            print("\n⚠️ Trying alternative source...")
            alt_url = self.DATASET_URLS['alternative']
            if not self.download_file(alt_url, "plantvillage_alt.zip"):
                print("\n❌ Failed to download dataset. Please download manually from:")
                print("   https://www.kaggle.com/datasets/emmarex/plantdisease")
                return False
        
        # Extract the zip file
        zip_path = self.download_dir / zip_filename
        if not zip_path.exists():
            zip_path = self.download_dir / "plantvillage_alt.zip"
        
        if zip_path.exists():
            self.extract_zip(zip_path, self.download_dir)
        
        # Organize dataset
        stats = self.organize_dataset()
        
        # Create info files
        self.create_dataset_info(stats)
        self.create_class_indices()
        
        # Print summary
        self.print_summary(stats)
        
        return True
    
    def print_summary(self, stats):
        """
        Print dataset summary
        
        Args:
            stats: Dataset statistics
        """
        print("\n" + "="*70)
        print("📊 Dataset Summary")
        print("="*70)
        
        total_images = sum(s['total'] for s in stats.values())
        total_train = sum(s['train'] for s in stats.values())
        total_val = sum(s['validation'] for s in stats.values())
        total_test = sum(s['test'] for s in stats.values())
        
        print(f"\n📁 Dataset Location: {self.output_dir.absolute()}")
        print(f"\n📈 Statistics:")
        print(f"   Total Classes: {len(stats)}")
        print(f"   Total Images: {total_images}")
        print(f"   Training Images: {total_train} ({total_train/total_images*100:.1f}%)")
        print(f"   Validation Images: {total_val} ({total_val/total_images*100:.1f}%)")
        print(f"   Test Images: {total_test} ({total_test/total_images*100:.1f}%)")
        
        print(f"\n📂 Directory Structure:")
        print(f"   {self.train_dir}/ - Training images")
        print(f"   {self.val_dir}/ - Validation images")
        print(f"   {self.test_dir}/ - Test images")
        
        print(f"\n🌾 Crops Included:")
        crops = set()
        for class_name in stats.keys():
            crop = class_name.split('___')[0]
            if 'Pepper' in crop:
                crop = 'Bell Pepper'
            elif 'Cherry' in crop:
                crop = 'Cherry'
            elif 'Corn' in crop:
                crop = 'Corn'
            crops.add(crop)
        
        for crop in sorted(crops):
            print(f"   • {crop}")
        
        print("\n✅ Dataset preparation complete!")
        print("\nNext steps:")
        print("   1. Run: python train_model.py")
        print("   2. Or use the training notebook: notebooks/02_model_training.ipynb")
    
    def download_from_kaggle(self, kaggle_dataset='emmarex/plantdisease'):
        """
        Download dataset from Kaggle (requires Kaggle API)
        
        Args:
            kaggle_dataset: Kaggle dataset identifier
        """
        print("\n📥 Downloading from Kaggle...")
        print("   Requires: pip install kaggle")
        
        try:
            import kaggle
            
            # Download dataset
            kaggle.api.dataset_download_files(kaggle_dataset, path=self.download_dir, unzip=True)
            
            # Organize dataset
            stats = self.organize_dataset()
            
            # Create info files
            self.create_dataset_info(stats)
            self.create_class_indices()
            
            print("✅ Download complete!")
            return True
            
        except ImportError:
            print("❌ Kaggle API not installed. Run: pip install kaggle")
            return False
        except Exception as e:
            print(f"❌ Kaggle download failed: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Download or prepare PlantVillage dataset')
    parser.add_argument('--output', '-o', default='dataset', 
                       help='Output directory for dataset (default: dataset)')
    parser.add_argument('--source', '-s', default='plantvillage',
                       choices=['plantvillage', 'alternative', 'kaggle', 'existing'],
                       help='Download source (default: plantvillage)')
    parser.add_argument('--kaggle-dataset', default='emmarex/plantdisease',
                       help='Kaggle dataset identifier (default: emmarex/plantdisease)')
    parser.add_argument('--existing-path', '-p', default=None,
                       help='Path to existing dataset directory (use with --source existing)')
    
    args = parser.parse_args()
    
    # Create downloader
    downloader = DatasetDownloader(
        output_dir=args.output,
        existing_dataset_path=args.existing_path
    )
    
    # Download or use existing dataset
    if args.source == 'existing':
        if not args.existing_path:
            print("❌ --existing-path is required when using --source existing")
            print("   Example: python download_dataset.py --source existing --existing-path /path/to/dataset")
            sys.exit(1)
        success = downloader.use_existing_dataset()
    elif args.source == 'kaggle':
        success = downloader.download_from_kaggle(args.kaggle_dataset)
    else:
        success = downloader.download_plantvillage(source=args.source)
    
    if not success:
        print("\n❌ Dataset preparation failed.")
        print("\nManual options:")
        print("   1. Provide existing dataset: python download_dataset.py --source existing --existing-path /path/to/dataset")
        print("   2. Download from: https://www.kaggle.com/datasets/emmarex/plantdisease")
        print("   3. Extract to the 'dataset' folder")
        print("   4. The folder structure should have class subdirectories")
        sys.exit(1)
    
    print("\n🎉 Dataset is ready for training!")


if __name__ == '__main__':
    main()
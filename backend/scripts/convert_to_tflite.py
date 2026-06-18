#!/usr/bin/env python3
"""
Convert to TensorFlow Lite Script
Converts the trained Keras model to TensorFlow Lite format for mobile deployment
Supports quantization options for size optimization
"""

import os
import sys
import argparse
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class TFLiteConverter:
    """
    Class for converting Keras models to TensorFlow Lite format
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
    
    def __init__(self, model_path='models/plant_disease_model.h5', 
                 output_dir='models/tflite',
                 quantization='float16'):
        """
        Initialize the TFLite converter
        
        Args:
            model_path: Path to the trained Keras model
            output_dir: Directory to save converted models
            quantization: Quantization type ('none', 'float16', 'int8', 'dynamic')
        """
        self.model_path = Path(model_path)
        self.output_dir = Path(output_dir)
        self.quantization = quantization
        
        self.model = None
        self.converter = None
        self.tflite_model = None
        self.representative_dataset = None
        
        # Results storage
        self.results = {
            'original_size': 0,
            'tflite_size': 0,
            'size_reduction': 0,
            'conversion_success': False,
            'quantization_type': quantization,
            'output_files': []
        }
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_model(self):
        """
        Load the trained Keras model
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("🤖 Loading Keras Model")
        print("="*70)
        
        if not self.model_path.exists():
            print(f"❌ Model not found: {self.model_path}")
            print("   Please train the model first: python train_model.py")
            return False
        
        try:
            self.model = load_model(self.model_path)
            
            # Get original model size
            self.results['original_size'] = self.model_path.stat().st_size
            original_size_mb = self.results['original_size'] / (1024 * 1024)
            
            print(f"✅ Model loaded from {self.model_path}")
            print(f"   Input shape: {self.model.input_shape}")
            print(f"   Output shape: {self.model.output_shape}")
            print(f"   Original size: {original_size_mb:.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return False
    
    def create_representative_dataset(self, data_dir='dataset/test', num_samples=100):
        """
        Create a representative dataset for INT8 quantization
        
        Args:
            data_dir: Directory containing test images
            num_samples: Number of samples to use
        """
        print("\n" + "="*70)
        print("📊 Creating Representative Dataset")
        print("="*70)
        
        try:
            import cv2
            from pathlib import Path
            
            data_path = Path(data_dir)
            if not data_path.exists():
                print(f"⚠️ Test directory not found: {data_dir}")
                print("   Using random data for representative dataset")
                
                # Generate random data as fallback
                def representative_data_gen():
                    for _ in range(num_samples):
                        yield [np.random.rand(1, 224, 224, 3).astype(np.float32)]
                
                self.representative_dataset = representative_data_gen
                print("✅ Using random data for representative dataset")
                return
            
            # Collect images from all classes
            images = []
            for class_dir in data_path.iterdir():
                if class_dir.is_dir():
                    for img_path in list(class_dir.glob('*.jpg'))[:5]:
                        images.append(img_path)
            
            if len(images) == 0:
                print("⚠️ No images found, using random data")
                def representative_data_gen():
                    for _ in range(num_samples):
                        yield [np.random.rand(1, 224, 224, 3).astype(np.float32)]
                self.representative_dataset = representative_data_gen
                return
            
            # Select random subset
            import random
            selected_images = random.sample(images, min(num_samples, len(images)))
            
            def representative_data_gen():
                for img_path in selected_images:
                    # Load and preprocess image
                    img = cv2.imread(str(img_path))
                    if img is None:
                        continue
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img = cv2.resize(img, (224, 224))
                    img = img.astype(np.float32) / 255.0
                    img = np.expand_dims(img, axis=0)
                    yield [img]
            
            self.representative_dataset = representative_data_gen
            print(f"✅ Representative dataset created with {len(selected_images)} images")
            
        except Exception as e:
            print(f"⚠️ Error creating representative dataset: {str(e)}")
            print("   Using random data as fallback")
            
            def representative_data_gen():
                for _ in range(num_samples):
                    yield [np.random.rand(1, 224, 224, 3).astype(np.float32)]
            
            self.representative_dataset = representative_data_gen
    
    def convert_to_tflite(self):
        """
        Convert the model to TensorFlow Lite format
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("🔄 Converting to TensorFlow Lite")
        print("="*70)
        
        try:
            # Create converter
            self.converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
            
            # Set optimization based on quantization type
            if self.quantization == 'float16':
                print("📊 Using Float16 quantization")
                self.converter.optimizations = [tf.lite.Optimize.DEFAULT]
                self.converter.target_spec.supported_types = [tf.float16]
                
            elif self.quantization == 'int8':
                print("📊 Using INT8 quantization (full integer)")
                self.converter.optimizations = [tf.lite.Optimize.DEFAULT]
                self.converter.representative_dataset = self.representative_dataset
                self.converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
                self.converter.inference_input_type = tf.uint8
                self.converter.inference_output_type = tf.uint8
                
            elif self.quantization == 'dynamic':
                print("📊 Using Dynamic range quantization")
                self.converter.optimizations = [tf.lite.Optimize.DEFAULT]
                
            else:
                print("📊 No quantization (float32)")
                # No optimization
            
            # Convert the model
            print("\n⏳ Converting model...")
            self.tflite_model = self.converter.convert()
            
            # Save the model
            output_filename = f"plant_disease_model_{self.quantization}.tflite"
            if self.quantization == 'none':
                output_filename = "plant_disease_model_float32.tflite"
            
            output_path = self.output_dir / output_filename
            with open(output_path, 'wb') as f:
                f.write(self.tflite_model)
            
            # Get file size
            self.results['tflite_size'] = output_path.stat().st_size
            self.results['output_files'].append(str(output_path))
            
            # Calculate size reduction
            original_mb = self.results['original_size'] / (1024 * 1024)
            tflite_mb = self.results['tflite_size'] / (1024 * 1024)
            reduction = (1 - self.results['tflite_size'] / self.results['original_size']) * 100
            
            self.results['size_reduction'] = reduction
            self.results['conversion_success'] = True
            
            print(f"\n✅ Conversion successful!")
            print(f"   Output: {output_path}")
            print(f"   Size: {tflite_mb:.2f} MB (from {original_mb:.2f} MB)")
            print(f"   Reduction: {reduction:.1f}%")
            
            return True
            
        except Exception as e:
            print(f"❌ Conversion failed: {str(e)}")
            self.results['conversion_success'] = False
            return False
    
    def test_tflite_model(self):
        """
        Test the converted TFLite model with a sample input
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("🧪 Testing TFLite Model")
        print("="*70)
        
        if not self.tflite_model:
            print("❌ No TFLite model to test")
            return False
        
        try:
            # Create interpreter
            interpreter = tf.lite.Interpreter(model_content=self.tflite_model)
            interpreter.allocate_tensors()
            
            # Get input and output details
            input_details = interpreter.get_input_details()
            output_details = interpreter.get_output_details()
            
            print(f"\n📋 Input Details:")
            print(f"   Shape: {input_details[0]['shape']}")
            print(f"   Type: {input_details[0]['dtype']}")
            
            print(f"\n📋 Output Details:")
            print(f"   Shape: {output_details[0]['shape']}")
            print(f"   Type: {output_details[0]['dtype']}")
            
            # Create sample input
            input_shape = input_details[0]['shape']
            input_dtype = input_details[0]['dtype']
            
            if input_dtype == np.uint8:
                sample_input = np.random.randint(0, 255, size=input_shape, dtype=np.uint8)
            else:
                sample_input = np.random.rand(*input_shape).astype(np.float32)
            
            # Run inference
            interpreter.set_tensor(input_details[0]['index'], sample_input)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            
            print(f"\n✅ Test inference successful!")
            print(f"   Output shape: {output.shape}")
            print(f"   Output sample: {output[0][:5]}...")
            
            # Get prediction class
            predicted_class = np.argmax(output[0])
            confidence = np.max(output[0])
            
            print(f"\n📊 Sample Prediction:")
            print(f"   Predicted class index: {predicted_class}")
            print(f"   Confidence: {confidence:.4f}")
            
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False
    
    def create_model_info(self):
        """
        Create model information JSON file for the TFLite model
        """
        print("\n" + "="*70)
        print("📝 Creating Model Information File")
        print("="*70)
        
        info = {
            'version': '1.0.0',
            'created_at': datetime.now().isoformat(),
            'source_model': str(self.model_path),
            'quantization': self.quantization,
            'input_shape': [1, 224, 224, 3],
            'input_dtype': 'float32' if self.quantization == 'none' else 'float16' if self.quantization == 'float16' else 'uint8',
            'output_shape': [1, 29],
            'num_classes': 29,
            'class_names': self.CLASS_NAMES,
            'display_names': self.DISPLAY_NAMES,
            'original_size_mb': self.results['original_size'] / (1024 * 1024),
            'tflite_size_mb': self.results['tflite_size'] / (1024 * 1024),
            'size_reduction_percent': self.results['size_reduction'],
            'usage_instructions': {
                'python': '''
import tensorflow as tf
import numpy as np
import cv2

# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path="plant_disease_model.tflite")
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load and preprocess image
img = cv2.imread("leaf_image.jpg")
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img = cv2.resize(img, (224, 224))
img = img.astype(np.float32) / 255.0
img = np.expand_dims(img, axis=0)

# Run inference
interpreter.set_tensor(input_details[0]['index'], img)
interpreter.invoke()
output = interpreter.get_tensor(output_details[0]['index'])

# Get prediction
predicted_class = np.argmax(output[0])
confidence = np.max(output[0])
                ''',
                'android': 'Use the TensorFlow Lite Android Support Library',
                'ios': 'Use TensorFlow Lite Swift API'
            }
        }
        
        # Save info file
        info_filename = f"model_info_{self.quantization}.json"
        if self.quantization == 'none':
            info_filename = "model_info_float32.json"
        
        info_path = self.output_dir / info_filename
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"✅ Model info saved to {info_path}")
        self.results['output_files'].append(str(info_path))
    
    def create_all_quantizations(self):
        """
        Convert model to all quantization types for comparison
        """
        print("\n" + "="*70)
        print("🔄 Converting to All Quantization Types")
        print("="*70)
        
        quantizations = ['none', 'dynamic', 'float16', 'int8']
        results = {}
        
        for quant in quantizations:
            print(f"\n📊 Converting with {quant} quantization...")
            
            # Create converter for this quantization type
            converter = TFLiteConverter(
                model_path=self.model_path,
                output_dir=self.output_dir,
                quantization=quant
            )
            
            if not converter.load_model():
                continue
            
            if quant == 'int8':
                converter.create_representative_dataset()
            
            if converter.convert_to_tflite():
                converter.test_tflite_model()
                converter.create_model_info()
                
                results[quant] = {
                    'size_mb': converter.results['tflite_size'] / (1024 * 1024),
                    'reduction': converter.results['size_reduction']
                }
        
        # Print comparison
        print("\n" + "="*70)
        print("📊 Quantization Comparison")
        print("="*70)
        print(f"\n{'Type':<15} {'Size (MB)':<15} {'Reduction':<15}")
        print("-" * 45)
        
        for quant, data in results.items():
            display_quant = quant if quant != 'none' else 'float32'
            print(f"{display_quant:<15} {data['size_mb']:<15.2f} {data['reduction']:<15.1f}%")
        
        # Recommend best option
        print(f"\n💡 Recommendation:")
        if 'float16' in results:
            print(f"   For mobile deployment: float16 quantization ({results['float16']['size_mb']:.2f} MB)")
        if 'int8' in results:
            print(f"   For edge devices: int8 quantization ({results['int8']['size_mb']:.2f} MB)")
    
    def run_conversion(self):
        """
        Run the complete conversion pipeline
        """
        print("\n" + "="*70)
        print("🌾 FarmIntel AI - TensorFlow Lite Conversion")
        print("="*70)
        print(f"\n📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load model
        if not self.load_model():
            return False
        
        # Create representative dataset for INT8 quantization
        if self.quantization == 'int8':
            self.create_representative_dataset()
        
        # Convert to TFLite
        if not self.convert_to_tflite():
            return False
        
        # Test converted model
        self.test_tflite_model()
        
        # Create model info
        self.create_model_info()
        
        print(f"\n📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"\n✅ Conversion complete! Files saved to {self.output_dir}/")
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Convert Keras model to TensorFlow Lite')
    parser.add_argument('--model', '-m', default='models/plant_disease_model.h5',
                       help='Path to trained model (default: models/plant_disease_model.h5)')
    parser.add_argument('--output', '-o', default='models/tflite',
                       help='Output directory (default: models/tflite)')
    parser.add_argument('--quantization', '-q', default='float16',
                       choices=['none', 'dynamic', 'float16', 'int8', 'all'],
                       help='Quantization type (default: float16)')
    parser.add_argument('--data', '-d', default='dataset/test',
                       help='Test data directory for INT8 calibration (default: dataset/test)')
    
    args = parser.parse_args()
    
    if args.quantization == 'all':
        # Convert to all quantization types
        converter = TFLiteConverter(
            model_path=args.model,
            output_dir=args.output,
            quantization='float16'  # Placeholder
        )
        
        if not converter.load_model():
            print("\n❌ Failed to load model.")
            sys.exit(1)
        
        converter.create_all_quantizations()
        
    else:
        # Convert single quantization type
        converter = TFLiteConverter(
            model_path=args.model,
            output_dir=args.output,
            quantization=args.quantization
        )
        
        # Set data directory for INT8 calibration
        if args.quantization == 'int8':
            converter.create_representative_dataset(data_dir=args.data)
        
        success = converter.run_conversion()
        
        if not success:
            print("\n❌ Conversion failed.")
            sys.exit(1)
    
    print("\n🎉 Conversion complete!")


if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Train Model Script
Trains the plant disease detection model using transfer learning
Supports 29 disease classes across 9 crops
"""

import os
import sys
import argparse
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0, ResNet50, VGG16
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau,
    TensorBoard, CSVLogger, Callback
)
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
tf.random.set_seed(42)
np.random.seed(42)


class TrainingProgressCallback(Callback):
    """Custom callback to log training progress"""
    
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        print(f"\n📊 Epoch {epoch + 1}/{self.params['epochs']} - "
              f"loss: {logs.get('loss', 0):.4f} - "
              f"accuracy: {logs.get('accuracy', 0):.4f} - "
              f"val_loss: {logs.get('val_loss', 0):.4f} - "
              f"val_accuracy: {logs.get('val_accuracy', 0):.4f}")


class ModelTrainer:
    """
    Main class for training the plant disease detection model
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
    
    # Base model configurations
    BASE_MODELS = {
        'mobilenetv2': {
            'model': MobileNetV2,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'MobileNetV2 - Lightweight, fast training'
        },
        'efficientnetb0': {
            'model': EfficientNetB0,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'EfficientNetB0 - Better accuracy, slower training'
        },
        'resnet50': {
            'model': ResNet50,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'ResNet50 - High accuracy, slower training'
        },
        'vgg16': {
            'model': VGG16,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'VGG16 - Very slow, large model'
        }
    }
    
    def __init__(self, data_dir='dataset', model_dir='models', 
                 base_model='mobilenetv2', batch_size=32, epochs=50,
                 learning_rate=0.001, img_size=224, fine_tune=False):
        """
        Initialize the model trainer
        
        Args:
            data_dir: Path to dataset directory
            model_dir: Path to save models
            base_model: Base model architecture
            batch_size: Batch size for training
            epochs: Number of training epochs
            learning_rate: Initial learning rate
            img_size: Image size for training
            fine_tune: Whether to perform fine-tuning
        """
        self.data_dir = Path(data_dir)
        self.model_dir = Path(model_dir)
        self.base_model_name = base_model.lower()
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.img_size = (img_size, img_size)
        self.fine_tune = fine_tune
        
        # Create model directory
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize data generators
        self.train_generator = None
        self.val_generator = None
        self.test_generator = None
        self.model = None
        self.history = None
        self.num_classes = len(self.CLASS_NAMES)
        
        # Training stats
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_time': None,
            'best_accuracy': 0,
            'best_val_accuracy': 0,
            'final_accuracy': 0,
            'final_val_accuracy': 0
        }
    
    def load_data(self):
        """
        Load and prepare data for training
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("📊 Loading Dataset")
        print("="*70)
        
        # Check if dataset exists
        train_dir = self.data_dir / '../dataset/Train'
        val_dir = self.data_dir / '../dataset/Val'
        test_dir = self.data_dir / '../dataset/Test'
        
        if not train_dir.exists():
            print(f"❌ Training directory not found: {train_dir}")
            print("   Please run: python download_dataset.py first")
            return False
        
        # Data augmentation for training
        train_datagen = ImageDataGenerator(
            rescale=1./255,
            rotation_range=40,
            width_shift_range=0.2,
            height_shift_range=0.2,
            shear_range=0.2,
            zoom_range=0.2,
            horizontal_flip=True,
            fill_mode='nearest'
        )
        
        # Only rescaling for validation and test
        val_test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Load training data
        self.train_generator = train_datagen.flow_from_directory(
            train_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=True
        )
        
        # Load validation data
        if val_dir.exists():
            self.val_generator = val_test_datagen.flow_from_directory(
                val_dir,
                target_size=self.img_size,
                batch_size=self.batch_size,
                class_mode='categorical',
                shuffle=False
            )
        else:
            # Use 20% of training data for validation if validation folder doesn't exist
            print("⚠️ Validation directory not found. Splitting training data...")
            from sklearn.model_selection import train_test_split
            
            # Create validation generator with validation split
            self.train_generator = train_datagen.flow_from_directory(
                train_dir,
                target_size=self.img_size,
                batch_size=self.batch_size,
                class_mode='categorical',
                subset='training',
                validation_split=0.2
            )
            
            self.val_generator = val_test_datagen.flow_from_directory(
                train_dir,
                target_size=self.img_size,
                batch_size=self.batch_size,
                class_mode='categorical',
                subset='validation',
                validation_split=0.2,
                shuffle=False
            )
        
        # Load test data if available
        if test_dir.exists():
            self.test_generator = val_test_datagen.flow_from_directory(
                test_dir,
                target_size=self.img_size,
                batch_size=self.batch_size,
                class_mode='categorical',
                shuffle=False
            )
        
        # Print dataset info
        print(f"\n📊 Dataset Statistics:")
        print(f"   Training samples: {self.train_generator.samples}")
        print(f"   Validation samples: {self.val_generator.samples}")
        if self.test_generator:
            print(f"   Test samples: {self.test_generator.samples}")
        print(f"   Number of classes: {self.num_classes}")
        
        # Update num_classes from the generator
        self.num_classes = self.train_generator.num_classes
        
        return True
    
    def build_model(self):
        """
        Build the model architecture
        
        Returns:
            Model: Compiled Keras model
        """
        print("\n" + "="*70)
        print("🏗️ Building Model Architecture")
        print("="*70)
        
        # Get base model configuration
        base_config = self.BASE_MODELS.get(self.base_model_name, self.BASE_MODELS['mobilenetv2'])
        base_model_class = base_config['model']
        input_shape = base_config['input_shape']
        weights = base_config['weights']
        
        print(f"   Base Model: {self.base_model_name.upper()}")
        print(f"   Input Shape: {input_shape}")
        print(f"   Weights: {weights}")
        print(f"   Classes: {self.num_classes}")
        
        # Load base model with pre-trained weights
        base_model = base_model_class(
            input_shape=input_shape,
            include_top=False,
            weights=weights
        )
        
        # Freeze base model layers
        base_model.trainable = False
        
        # Build custom head
        self.model = Sequential([
            base_model,
            GlobalAveragePooling2D(),
            Dense(512, activation='relu'),
            BatchNormalization(),
            Dropout(0.5),
            Dense(256, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            Dense(128, activation='relu'),
            BatchNormalization(),
            Dropout(0.2),
            Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model
        optimizer = Adam(learning_rate=self.learning_rate)
        
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        # Print model summary
        print(f"\n📋 Model Summary:")
        print(f"   Total parameters: {self.model.count_params():,}")
        print(f"   Trainable parameters: {sum([tf.keras.backend.count_params(w) for w in self.model.trainable_weights]):,}")
        
        return self.model
    
    def setup_fine_tuning(self):
        """
        Setup fine-tuning by unfreezing some base model layers
        """
        # Get the base model (first layer)
        base_model = self.model.layers[0]
        base_model.trainable = True
        
        # Freeze all layers first
        for layer in base_model.layers:
            layer.trainable = False
        
        # Unfreeze the last 50 layers
        for layer in base_model.layers[-50:]:
            layer.trainable = True
        
        # Recompile with lower learning rate
        optimizer = Adam(learning_rate=self.learning_rate / 10)
        
        self.model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        print(f"\n🔄 Fine-tuning configured:")
        print(f"   Unfrozen layers: 50")
        print(f"   New learning rate: {self.learning_rate / 10}")
    
    def get_callbacks(self):
        """
        Create training callbacks
        
        Returns:
            list: List of callbacks
        """
        callbacks = []
        
        # Model checkpoint - save best model
        checkpoint = ModelCheckpoint(
            self.model_dir / 'best_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        callbacks.append(checkpoint)
        
        # Early stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True,
            verbose=1
        )
        callbacks.append(early_stop)
        
        # Reduce learning rate on plateau
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=5,
            min_lr=1e-7,
            verbose=1
        )
        callbacks.append(reduce_lr)
        
        # TensorBoard
        log_dir = self.model_dir / 'logs' / datetime.now().strftime("%Y%m%d-%H%M%S")
        tensorboard = TensorBoard(log_dir=str(log_dir), histogram_freq=1)
        callbacks.append(tensorboard)
        
        # CSV Logger
        csv_logger = CSVLogger(str(self.model_dir / 'training_log.csv'), append=True)
        callbacks.append(csv_logger)
        
        # Custom progress callback
        progress_callback = TrainingProgressCallback()
        callbacks.append(progress_callback)
        
        return callbacks
    
    def train(self):
        """
        Train the model
        
        Returns:
            History object
        """
        print("\n" + "="*70)
        print("🚀 Starting Training")
        print("="*70)
        print(f"\n   Epochs: {self.epochs}")
        print(f"   Batch Size: {self.batch_size}")
        print(f"   Learning Rate: {self.learning_rate}")
        print(f"   Fine-tuning: {self.fine_tune}")
        
        self.stats['start_time'] = datetime.now()
        
        # Phase 1: Train the head
        print("\n📚 Phase 1: Training the classification head...")
        
        callbacks = self.get_callbacks()
        
        self.history = self.model.fit(
            self.train_generator,
            validation_data=self.val_generator,
            epochs=self.epochs,
            callbacks=callbacks,
            verbose=0  # We'll use custom progress output
        )
        
        # Phase 2: Fine-tuning (optional)
        if self.fine_tune:
            print("\n📚 Phase 2: Fine-tuning the model...")
            self.setup_fine_tuning()
            
            callbacks = self.get_callbacks()
            
            history_fine = self.model.fit(
                self.train_generator,
                validation_data=self.val_generator,
                epochs=self.epochs,
                callbacks=callbacks,
                verbose=0
            )
            
            # Combine histories
            for key in self.history.history:
                if key in history_fine.history:
                    self.history.history[key].extend(history_fine.history[key])
        
        self.stats['end_time'] = datetime.now()
        self.stats['total_time'] = str(self.stats['end_time'] - self.stats['start_time'])
        
        # Update stats
        if 'accuracy' in self.history.history:
            self.stats['best_accuracy'] = max(self.history.history['accuracy'])
            self.stats['final_accuracy'] = self.history.history['accuracy'][-1]
        if 'val_accuracy' in self.history.history:
            self.stats['best_val_accuracy'] = max(self.history.history['val_accuracy'])
            self.stats['final_val_accuracy'] = self.history.history['val_accuracy'][-1]
        
        print(f"\n✅ Training completed!")
        print(f"   Total time: {self.stats['total_time']}")
        print(f"   Best validation accuracy: {self.stats['best_val_accuracy']:.4f}")
        
        return self.history
    
    def evaluate(self):
        """
        Evaluate the model on test data
        
        Returns:
            dict: Evaluation metrics
        """
        if self.test_generator is None:
            print("\n⚠️ No test data available for evaluation")
            return None
        
        print("\n" + "="*70)
        print("📊 Evaluating Model on Test Data")
        print("="*70)
        
        results = self.model.evaluate(self.test_generator, verbose=1)
        
        metrics = {
            'loss': results[0],
            'accuracy': results[1],
            'precision': results[2] if len(results) > 2 else None,
            'recall': results[3] if len(results) > 3 else None
        }
        
        print(f"\n📈 Test Results:")
        print(f"   Loss: {metrics['loss']:.4f}")
        print(f"   Accuracy: {metrics['accuracy']:.4f}")
        print(f"   Precision: {metrics['precision']:.4f}" if metrics['precision'] else "   Precision: N/A")
        print(f"   Recall: {metrics['recall']:.4f}" if metrics['recall'] else "   Recall: N/A")
        
        return metrics
    
    def save_model(self):
        """
        Save the trained model and metadata
        """
        print("\n" + "="*70)
        print("💾 Saving Model")
        print("="*70)
        
        # Save model in H5 format
        model_path = self.model_dir / 'plant_disease_model.h5'
        self.model.save(model_path)
        print(f"✅ Model saved to {model_path}")
        
        # Save model in Keras format
        keras_path = self.model_dir / 'plant_disease_model.keras'
        self.model.save(keras_path)
        print(f"✅ Model saved to {keras_path}")
        
        # Save class indices
        class_indices = {name: idx for idx, name in enumerate(self.CLASS_NAMES)}
        indices_path = self.model_dir / 'class_indices.json'
        with open(indices_path, 'w') as f:
            json.dump(class_indices, f, indent=2)
        print(f"✅ Class indices saved to {indices_path}")
        
        # Save model metadata
        metadata = {
            'model_path': str(model_path),
            'num_classes': self.num_classes,
            'class_names': self.CLASS_NAMES[:self.num_classes],
            'input_shape': list(self.img_size) + [3],
            'base_model': self.base_model_name,
            'batch_size': self.batch_size,
            'epochs': self.epochs,
            'learning_rate': self.learning_rate,
            'fine_tune': self.fine_tune,
            'training_date': datetime.now().isoformat(),
            'training_time': self.stats['total_time'],
            'best_accuracy': float(self.stats['best_accuracy']),
            'best_val_accuracy': float(self.stats['best_val_accuracy']),
            'final_accuracy': float(self.stats['final_accuracy']),
            'final_val_accuracy': float(self.stats['final_val_accuracy'])
        }
        
        metadata_path = self.model_dir / 'model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Model metadata saved to {metadata_path}")
    
    def plot_training_history(self):
        """
        Plot and save training history graphs
        """
        if self.history is None:
            return
        
        print("\n" + "="*70)
        print("📈 Generating Training Plots")
        print("="*70)
        
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Accuracy plot
        axes[0].plot(self.history.history['accuracy'], label='Training Accuracy', marker='o')
        axes[0].plot(self.history.history['val_accuracy'], label='Validation Accuracy', marker='o')
        axes[0].set_title('Model Accuracy')
        axes[0].set_xlabel('Epoch')
        axes[0].set_ylabel('Accuracy')
        axes[0].legend()
        axes[0].grid(True)
        
        # Loss plot
        axes[1].plot(self.history.history['loss'], label='Training Loss', marker='o')
        axes[1].plot(self.history.history['val_loss'], label='Validation Loss', marker='o')
        axes[1].set_title('Model Loss')
        axes[1].set_xlabel('Epoch')
        axes[1].set_ylabel('Loss')
        axes[1].legend()
        axes[1].grid(True)
        
        # Precision/Recall if available
        if 'precision' in self.history.history:
            axes[2].plot(self.history.history['precision'], label='Precision', marker='o')
            axes[2].plot(self.history.history['recall'], label='Recall', marker='o')
            if 'val_precision' in self.history.history:
                axes[2].plot(self.history.history['val_precision'], label='Val Precision', marker='o')
                axes[2].plot(self.history.history['val_recall'], label='Val Recall', marker='o')
            axes[2].set_title('Precision & Recall')
            axes[2].set_xlabel('Epoch')
            axes[2].set_ylabel('Score')
            axes[2].legend()
            axes[2].grid(True)
        else:
            axes[2].text(0.5, 0.5, 'Precision/Recall data not available', 
                        ha='center', va='center', transform=axes[2].transAxes)
            axes[2].set_title('Precision & Recall')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = self.model_dir / 'training_history.png'
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"✅ Training plots saved to {plot_path}")
        
        plt.close()
    
    def print_summary(self):
        """
        Print training summary
        """
        print("\n" + "="*70)
        print("🎉 Training Complete!")
        print("="*70)
        
        print(f"\n📊 Final Results:")
        print(f"   Training Accuracy: {self.stats['final_accuracy']:.4f}")
        print(f"   Validation Accuracy: {self.stats['final_val_accuracy']:.4f}")
        print(f"   Best Validation Accuracy: {self.stats['best_val_accuracy']:.4f}")
        print(f"   Total Training Time: {self.stats['total_time']}")
        
        print(f"\n📁 Model Location: {self.model_dir}")
        print(f"\n📋 Model Files:")
        print(f"   plant_disease_model.h5 - Trained model")
        print(f"   plant_disease_model.keras - Keras format model")
        print(f"   class_indices.json - Class mapping")
        print(f"   model_metadata.json - Model information")
        print(f"   training_history.png - Training plots")
        print(f"   training_log.csv - Training logs")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Test the model: python evaluate_model.py")
        print(f"   2. Convert to TFLite: python convert_to_tflite.py")
        print(f"   3. Start the backend: cd .. && python run.py")
    
    def run_full_pipeline(self):
        """
        Run the complete training pipeline
        """
        print("\n" + "="*70)
        print("🌾 FarmIntel AI - Model Training Pipeline")
        print("="*70)
        print(f"\n📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load data
        if not self.load_data():
            return False
        
        # Build model
        self.build_model()
        
        # Train model
        self.train()
        
        # Evaluate model
        self.evaluate()
        
        # Save model
        self.save_model()
        
        # Plot training history
        self.plot_training_history()
        
        # Print summary
        self.print_summary()
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Train plant disease detection model')
    parser.add_argument('--data', '-d', default='dataset',
                       help='Dataset directory (default: dataset)')
    parser.add_argument('--model-dir', '-m', default='models',
                       help='Model output directory (default: models)')
    parser.add_argument('--base-model', '-b', default='mobilenetv2',
                       choices=['mobilenetv2', 'efficientnetb0', 'resnet50', 'vgg16'],
                       help='Base model architecture (default: mobilenetv2)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training (default: 32)')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs (default: 50)')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Learning rate (default: 0.001)')
    parser.add_argument('--img-size', type=int, default=224,
                       help='Image size for training (default: 224)')
    parser.add_argument('--fine-tune', action='store_true',
                       help='Enable fine-tuning (unfreeze base model layers)')
    
    args = parser.parse_args()
    
    # Create trainer
    trainer = ModelTrainer(
        data_dir=args.data,
        model_dir=args.model_dir,
        base_model=args.base_model,
        batch_size=args.batch_size,
        epochs=args.epochs,
        learning_rate=args.lr,
        img_size=args.img_size,
        fine_tune=args.fine_tune
    )
    
    # Run training
    success = trainer.run_full_pipeline()
    
    if not success:
        print("\n❌ Training failed. Please check your dataset.")
        sys.exit(1)
    
    print("\n🎉 Model training complete! The model is ready for use.")


if __name__ == '__main__':
    main()
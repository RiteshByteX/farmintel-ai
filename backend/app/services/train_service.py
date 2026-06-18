"""
Train Service - Model Training Pipeline Service
Handles dataset loading, model training, evaluation, and saving
Supports 29 disease classes from PlantVillage dataset
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization, Input
from tensorflow.keras.applications import MobileNetV2, EfficientNetB0, ResNet50, VGG16, DenseNet121
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau,
    TensorBoard, CSVLogger, LearningRateScheduler
)
from flask import current_app
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, Tuple, Optional, List
import shutil
import math


class TrainService:
    """
    Service for training plant disease detection model
    Handles data loading, model architecture, training pipeline, and evaluation
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
    
    # Base model configurations
    BASE_MODELS = {
        'MobileNetV2': {
            'model': MobileNetV2,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'Lightweight, fast training'
        },
        'EfficientNetB0': {
            'model': EfficientNetB0,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'Better accuracy, slower'
        },
        'ResNet50': {
            'model': ResNet50,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'High accuracy, slow'
        },
        'VGG16': {
            'model': VGG16,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'Very slow, large model'
        },
        'DenseNet121': {
            'model': DenseNet121,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'Excellent accuracy'
        }
    }
    
    def __init__(self, config: Dict = None):
        """
        Initialize training service
        
        Args:
            config: Training configuration dictionary
        """
        self.config = config or {}
        self.model = None
        self.history = None
        self.class_indices = None
        self.num_classes = len(self.CLASS_NAMES)
        self.best_val_accuracy = 0.0
        
        # Default training parameters
        self.epochs = self.config.get('epochs', 50)
        self.batch_size = self.config.get('batch_size', 32)
        self.learning_rate = self.config.get('learning_rate', 0.001)
        self.base_model_name = self.config.get('base_model', 'MobileNetV2')
        self.validation_split = self.config.get('validation_split', 0.2)
        self.test_split = self.config.get('test_split', 0.1)
        self.random_seed = self.config.get('random_seed', 42)
        self.image_size = self.config.get('image_size', (224, 224))
        
        # Set random seeds
        self._set_seeds()
    
    def _set_seeds(self):
        """Set random seeds for reproducibility"""
        tf.random.set_seed(self.random_seed)
        np.random.seed(self.random_seed)
    
    def load_data(self, data_dir: str, use_subdirs: bool = True) -> Tuple:
        """
        Load and prepare data for training
        
        Args:
            data_dir: Path to dataset directory (should contain class subdirectories)
            use_subdirs: Whether dataset has train/val/test subdirectories
            
        Returns:
            Tuple of (train_generator, validation_generator, test_generator, class_indices)
        """
        try:
            self._set_seeds()
            
            # Check if dataset has train/val/test subdirectories
            train_dir = os.path.join(data_dir, 'train') if use_subdirs else data_dir
            val_dir = os.path.join(data_dir, 'val') if use_subdirs else None
            test_dir = os.path.join(data_dir, 'test') if use_subdirs else None
            
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
            
            # Only rescaling for validation/test
            val_test_datagen = ImageDataGenerator(rescale=1./255)
            
            # Load training data
            if os.path.exists(train_dir):
                train_generator = train_datagen.flow_from_directory(
                    train_dir,
                    target_size=self.image_size,
                    batch_size=self.batch_size,
                    class_mode='categorical',
                    shuffle=True,
                    seed=self.random_seed
                )
                print(f"✅ Training data: {train_generator.samples} images, {train_generator.num_classes} classes")
            else:
                raise FileNotFoundError(f"Training directory not found: {train_dir}")
            
            # Load validation data
            if val_dir and os.path.exists(val_dir):
                validation_generator = val_test_datagen.flow_from_directory(
                    val_dir,
                    target_size=self.image_size,
                    batch_size=self.batch_size,
                    class_mode='categorical',
                    shuffle=False,
                    seed=self.random_seed
                )
                print(f"✅ Validation data: {validation_generator.samples} images")
            else:
                # Use split from training data
                print("⚠️ No validation directory, using 80/20 split from training data")
                train_datagen_split = ImageDataGenerator(
                    rescale=1./255,
                    validation_split=self.validation_split,
                    rotation_range=40,
                    width_shift_range=0.2,
                    height_shift_range=0.2,
                    shear_range=0.2,
                    zoom_range=0.2,
                    horizontal_flip=True,
                    fill_mode='nearest'
                )
                
                train_generator = train_datagen_split.flow_from_directory(
                    data_dir,
                    target_size=self.image_size,
                    batch_size=self.batch_size,
                    class_mode='categorical',
                    subset='training',
                    shuffle=True,
                    seed=self.random_seed
                )
                
                validation_generator = train_datagen_split.flow_from_directory(
                    data_dir,
                    target_size=self.image_size,
                    batch_size=self.batch_size,
                    class_mode='categorical',
                    subset='validation',
                    shuffle=False,
                    seed=self.random_seed
                )
            
            # Load test data if available
            test_generator = None
            if test_dir and os.path.exists(test_dir):
                test_generator = val_test_datagen.flow_from_directory(
                    test_dir,
                    target_size=self.image_size,
                    batch_size=self.batch_size,
                    class_mode='categorical',
                    shuffle=False,
                    seed=self.random_seed
                )
                print(f"✅ Test data: {test_generator.samples} images")
            
            self.class_indices = train_generator.class_indices
            self.num_classes = train_generator.num_classes
            
            # Print class distribution
            print(f"\n📊 Dataset Statistics:")
            print(f"   Classes: {self.num_classes}")
            print(f"   Training samples: {train_generator.samples}")
            print(f"   Validation samples: {validation_generator.samples}")
            if test_generator:
                print(f"   Test samples: {test_generator.samples}")
            
            return train_generator, validation_generator, test_generator, self.class_indices
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            raise
    
    def build_model(self, fine_tune: bool = False) -> Model:
        """
        Build the model architecture using transfer learning
        
        Args:
            fine_tune: Whether to prepare for fine-tuning
            
        Returns:
            Compiled Keras model
        """
        try:
            # Get base model configuration
            base_config = self.BASE_MODELS.get(self.base_model_name, self.BASE_MODELS['MobileNetV2'])
            base_model_class = base_config['model']
            input_shape = base_config['input_shape']
            weights = base_config['weights']
            
            print(f"\n🏗️ Building model with base: {self.base_model_name}")
            print(f"   Input shape: {input_shape}")
            
            # Load base model with pre-trained weights
            base_model = base_model_class(
                input_shape=input_shape,
                include_top=False,
                weights=weights
            )
            
            # Freeze or unfreeze base model layers
            base_model.trainable = fine_tune
            
            # Build custom head
            inputs = Input(shape=input_shape)
            x = base_model(inputs, training=False)
            x = GlobalAveragePooling2D()(x)
            x = Dense(512, activation='relu')(x)
            x = BatchNormalization()(x)
            x = Dropout(0.5)(x)
            x = Dense(256, activation='relu')(x)
            x = BatchNormalization()(x)
            x = Dropout(0.3)(x)
            x = Dense(128, activation='relu')(x)
            x = BatchNormalization()(x)
            x = Dropout(0.2)(x)
            outputs = Dense(self.num_classes, activation='softmax')(x)
            
            model = Model(inputs=inputs, outputs=outputs)
            
            # Compile model
            optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)
            
            model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy', 'precision', 'recall', 'auc']
            )
            
            self.model = model
            
            # Count parameters
            trainable_params = sum([tf.keras.backend.count_params(w) for w in model.trainable_weights])
            non_trainable_params = sum([tf.keras.backend.count_params(w) for w in model.non_trainable_weights])
            
            print(f"\n📊 Model Statistics:")
            print(f"   Total parameters: {model.count_params():,}")
            print(f"   Trainable parameters: {trainable_params:,}")
            print(f"   Non-trainable parameters: {non_trainable_params:,}")
            
            return model
            
        except Exception as e:
            print(f"❌ Error building model: {str(e)}")
            raise
    
    def setup_fine_tuning(self, unfreeze_layers: int = 50):
        """
        Setup fine-tuning by unfreezing some base layers
        
        Args:
            unfreeze_layers: Number of layers to unfreeze from the end
        """
        try:
            # Get base model (first layer)
            base_model = self.model.layers[1] if hasattr(self.model, 'layers') and len(self.model.layers) > 1 else None
            
            if base_model is None:
                print("⚠️ Could not find base model for fine-tuning")
                return
            
            # Make base model trainable
            base_model.trainable = True
            
            # Freeze all layers first
            for layer in base_model.layers:
                layer.trainable = False
            
            # Unfreeze last 'unfreeze_layers' layers
            for layer in base_model.layers[-unfreeze_layers:]:
                layer.trainable = True
            
            trainable_layers = sum(1 for layer in base_model.layers if layer.trainable)
            
            print(f"\n🔧 Fine-tuning configuration:")
            print(f"   Total base layers: {len(base_model.layers)}")
            print(f"   Trainable layers: {trainable_layers}")
            print(f"   Unfrozen layers: {unfreeze_layers}")
            
            # Recompile with lower learning rate
            optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate / 10)
            
            self.model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy', 'precision', 'recall', 'auc']
            )
            
            print(f"   New learning rate: {self.learning_rate / 10}")
            
        except Exception as e:
            print(f"❌ Error setting up fine-tuning: {str(e)}")
            raise
    
    def _get_callbacks(self, phase: str = 'head') -> List:
        """
        Create training callbacks
        
        Args:
            phase: Training phase ('head' or 'fine_tune')
            
        Returns:
            List of callbacks
        """
        callbacks = []
        
        # Create directories
        os.makedirs('models', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Model checkpoint - save best model
        checkpoint = ModelCheckpoint(
            f'models/best_model_{phase}.h5',
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
        
        # CSV Logger
        csv_logger = CSVLogger(f'logs/training_log_{phase}.csv', append=True)
        callbacks.append(csv_logger)
        
        # TensorBoard
        tensorboard = TensorBoard(
            log_dir=f'logs/tensorboard/{phase}_{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            histogram_freq=1
        )
        callbacks.append(tensorboard)
        
        return callbacks
    
    def train(self, train_generator, validation_generator, 
              epochs: int = None, fine_tune: bool = False) -> Dict:
        """
        Train the model
        
        Args:
            train_generator: Training data generator
            validation_generator: Validation data generator
            epochs: Number of epochs (overrides default)
            fine_tune: Whether to perform fine-tuning after initial training
            
        Returns:
            Training history dictionary
        """
        if epochs is None:
            epochs = self.epochs
        
        try:
            # Phase 1: Train the head
            print("\n" + "="*60)
            print("🚀 PHASE 1: Training Classification Head")
            print("="*60)
            
            callbacks = self._get_callbacks(phase='head')
            
            history = self.model.fit(
                train_generator,
                validation_data=validation_generator,
                epochs=epochs // 2,
                callbacks=callbacks,
                verbose=1
            )
            
            # Phase 2: Fine-tuning (optional)
            if fine_tune:
                print("\n" + "="*60)
                print("🚀 PHASE 2: Fine-tuning")
                print("="*60)
                
                self.setup_fine_tuning()
                callbacks = self._get_callbacks(phase='fine_tune')
                
                history_fine = self.model.fit(
                    train_generator,
                    validation_data=validation_generator,
                    epochs=epochs // 2,
                    callbacks=callbacks,
                    verbose=1
                )
                
                # Combine histories
                for key in history.history:
                    if key in history_fine.history:
                        history.history[key].extend(history_fine.history[key])
            
            self.history = history
            
            # Get best validation accuracy
            if 'val_accuracy' in history.history:
                self.best_val_accuracy = max(history.history['val_accuracy'])
            
            print(f"\n✅ Training completed successfully!")
            print(f"   Best validation accuracy: {self.best_val_accuracy:.4f}")
            
            return history.history
            
        except Exception as e:
            print(f"❌ Error during training: {str(e)}")
            raise
    
    def evaluate(self, test_generator) -> Dict:
        """
        Evaluate the model on test data
        
        Args:
            test_generator: Test data generator
            
        Returns:
            Evaluation metrics dictionary
        """
        try:
            if test_generator is None:
                print("⚠️ No test data available for evaluation")
                return {}
            
            print("\n" + "="*60)
            print("📊 Model Evaluation")
            print("="*60)
            
            results = self.model.evaluate(test_generator, verbose=1)
            
            metrics = {
                'loss': results[0],
                'accuracy': results[1],
                'precision': results[2] if len(results) > 2 else 0,
                'recall': results[3] if len(results) > 3 else 0,
                'auc': results[4] if len(results) > 4 else 0
            }
            
            print(f"\n📈 Test Results:")
            print(f"   Loss: {metrics['loss']:.4f}")
            print(f"   Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
            print(f"   Precision: {metrics['precision']:.4f}")
            print(f"   Recall: {metrics['recall']:.4f}")
            print(f"   AUC: {metrics['auc']:.4f}")
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error during evaluation: {str(e)}")
            raise
    
    def save_model(self, save_path: str = 'models/plant_disease_model.h5'):
        """
        Save the trained model and artifacts
        
        Args:
            save_path: Path to save the model
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            # Save model in H5 format
            self.model.save(save_path)
            print(f"✅ Model saved to {save_path}")
            
            # Save model in Keras format
            keras_path = save_path.replace('.h5', '.keras')
            self.model.save(keras_path)
            print(f"✅ Model saved to {keras_path}")
            
            # Save class indices
            indices_path = os.path.join(os.path.dirname(save_path), 'class_indices.json')
            # Convert numpy ints to Python ints for JSON serialization
            serializable_indices = {k: int(v) for k, v in self.class_indices.items()}
            with open(indices_path, 'w') as f:
                json.dump(serializable_indices, f, indent=2)
            print(f"✅ Class indices saved to {indices_path}")
            
            # Save model metadata
            metadata = {
                'model_path': save_path,
                'num_classes': self.num_classes,
                'class_names': self.CLASS_NAMES,
                'display_names': self.DISPLAY_NAMES,
                'input_shape': list(self.image_size) + [3],
                'base_model': self.base_model_name,
                'training_date': datetime.now().isoformat(),
                'epochs': self.epochs,
                'batch_size': self.batch_size,
                'learning_rate': self.learning_rate,
                'best_val_accuracy': float(self.best_val_accuracy),
                'final_accuracy': float(self.history.history['accuracy'][-1]) if self.history and self.history.history.get('accuracy') else None,
                'final_val_accuracy': float(self.history.history['val_accuracy'][-1]) if self.history and self.history.history.get('val_accuracy') else None
            }
            
            metadata_path = os.path.join(os.path.dirname(save_path), 'model_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            print(f"✅ Metadata saved to {metadata_path}")
            
            # Save training history
            if self.history:
                history_path = os.path.join(os.path.dirname(save_path), 'training_history.json')
                serializable_history = {k: [float(x) for x in v] for k, v in self.history.history.items()}
                with open(history_path, 'w') as f:
                    json.dump(serializable_history, f, indent=2)
                print(f"✅ Training history saved to {history_path}")
            
        except Exception as e:
            print(f"❌ Error saving model: {str(e)}")
            raise
    
    def plot_training_history(self, save_path: str = 'models/training_curves.png'):
        """
        Plot training history curves
        
        Args:
            save_path: Path to save the plot
        """
        if not self.history:
            print("⚠️ No training history available")
            return
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            # Accuracy plot
            ax1 = axes[0, 0]
            ax1.plot(self.history.history['accuracy'], label='Training Accuracy', linewidth=2)
            ax1.plot(self.history.history['val_accuracy'], label='Validation Accuracy', linewidth=2)
            ax1.set_title('Model Accuracy', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Epoch')
            ax1.set_ylabel('Accuracy')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Loss plot
            ax2 = axes[0, 1]
            ax2.plot(self.history.history['loss'], label='Training Loss', linewidth=2)
            ax2.plot(self.history.history['val_loss'], label='Validation Loss', linewidth=2)
            ax2.set_title('Model Loss', fontsize=12, fontweight='bold')
            ax2.set_xlabel('Epoch')
            ax2.set_ylabel('Loss')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            # Precision plot
            ax3 = axes[1, 0]
            if 'precision' in self.history.history:
                ax3.plot(self.history.history['precision'], label='Training Precision', linewidth=2)
            if 'val_precision' in self.history.history:
                ax3.plot(self.history.history['val_precision'], label='Validation Precision', linewidth=2)
            ax3.set_title('Model Precision', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Epoch')
            ax3.set_ylabel('Precision')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # Recall plot
            ax4 = axes[1, 1]
            if 'recall' in self.history.history:
                ax4.plot(self.history.history['recall'], label='Training Recall', linewidth=2)
            if 'val_recall' in self.history.history:
                ax4.plot(self.history.history['val_recall'], label='Validation Recall', linewidth=2)
            ax4.set_title('Model Recall', fontsize=12, fontweight='bold')
            ax4.set_xlabel('Epoch')
            ax4.set_ylabel('Recall')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            plt.suptitle('Training History', fontsize=14, fontweight='bold')
            plt.tight_layout()
            
            # Save plot
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Training curves saved to {save_path}")
            
        except Exception as e:
            print(f"❌ Error plotting training history: {str(e)}")
    
    def run_full_pipeline(self, data_dir: str, save_path: str = 'models/plant_disease_model.h5',
                          fine_tune: bool = False, test_dir: str = None) -> Dict:
        """
        Run the complete training pipeline
        
        Args:
            data_dir: Path to dataset directory
            save_path: Path to save the model
            fine_tune: Whether to perform fine-tuning
            test_dir: Optional test directory
            
        Returns:
            Dictionary with training results
        """
        start_time = datetime.now()
        
        print("\n" + "="*60)
        print("🌾 FARMINTEL AI - TRAINING PIPELINE")
        print("="*60)
        print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Load data
            train_gen, val_gen, test_gen, class_indices = self.load_data(data_dir)
            
            # Build model
            self.build_model(fine_tune=False)
            
            # Train model
            history = self.train(train_gen, val_gen, fine_tune=fine_tune)
            
            # Evaluate on test set if available
            test_metrics = {}
            if test_gen or (test_dir and os.path.exists(test_dir)):
                if not test_gen and test_dir:
                    # Load test data
                    test_datagen = ImageDataGenerator(rescale=1./255)
                    test_gen = test_datagen.flow_from_directory(
                        test_dir,
                        target_size=self.image_size,
                        batch_size=self.batch_size,
                        class_mode='categorical',
                        shuffle=False
                    )
                test_metrics = self.evaluate(test_gen)
            
            # Save model
            self.save_model(save_path)
            
            # Plot training history
            self.plot_training_history()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "="*60)
            print("🎉 TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
            print("="*60)
            print(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Duration: {duration//60:.0f}m {duration%60:.0f}s")
            print(f"Best validation accuracy: {self.best_val_accuracy:.4f} ({self.best_val_accuracy*100:.2f}%)")
            if test_metrics:
                print(f"Test accuracy: {test_metrics.get('accuracy', 0):.4f} ({test_metrics.get('accuracy', 0)*100:.2f}%)")
            
            return {
                'success': True,
                'best_val_accuracy': float(self.best_val_accuracy),
                'test_accuracy': float(test_metrics.get('accuracy', 0)),
                'num_classes': self.num_classes,
                'total_epochs': len(history.get('accuracy', [])),
                'model_path': save_path,
                'history': history,
                'duration_seconds': duration
            }
            
        except Exception as e:
            print(f"\n❌ Training pipeline failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
train_service = TrainService()
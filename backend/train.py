#!/usr/bin/env python3
"""
FarmIntel AI - Complete Training Pipeline
=========================================
This script handles the entire model training process including:
- Dataset validation and preparation
- Data augmentation configuration
- Model architecture building (Transfer Learning)
- Training with callbacks (checkpoint, early stopping, reduce LR)
- Fine-tuning (optional)
- Model evaluation and testing
- Model export (H5, Keras, TFLite)
- Training visualization and reporting

Author: FarmIntel AI Team
Version: 1.0.0
"""

import os
import sys
import argparse
import json
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import time
import shutil
import warnings
warnings.filterwarnings('ignore')

# TensorFlow imports
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, callbacks
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import (
    Conv2D, MaxPooling2D, GlobalAveragePooling2D, Dense, Dropout, 
    BatchNormalization, Input, Flatten, Activation
)
from tensorflow.keras.applications import (
    MobileNetV2, EfficientNetB0, ResNet50, VGG16, InceptionV3, DenseNet121
)
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam, SGD, RMSprop
from tensorflow.keras.callbacks import (
    ModelCheckpoint, EarlyStopping, ReduceLROnPlateau,
    CSVLogger, TensorBoard, LearningRateScheduler, Callback
)
from tensorflow.keras.metrics import Accuracy, Precision, Recall, AUC

# Scikit-learn imports
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_curve, auc,
    ConfusionMatrixDisplay
)
from sklearn.utils.class_weight import compute_class_weight

# Set random seeds for reproducibility
def set_seeds(seed=42):
    """Set random seeds for reproducibility"""
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1'

set_seeds(42)

# Configure TensorFlow for memory growth (prevent OOM errors)
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        print(f"✅ GPU memory growth enabled for {len(gpus)} GPU(s)")
    except RuntimeError as e:
        print(f"⚠️ GPU memory growth configuration error: {e}")


# ============================================================================
# CONFIGURATION CLASS - UPDATED WITH CORRECT PATHS
# ============================================================================

class TrainingConfig:
    """Centralized configuration for training pipeline"""
    
    # ==================== DATASET PATHS (UPDATED) ====================
    # Base directory (relative to where train.py is run from)
    # Since train.py is in backend/ folder, we use relative paths
    BASE_DIR = '.'  # Current directory (backend/)
    
    # Dataset paths - Updated for your folder structure
    DATASET_PATH = os.path.join(BASE_DIR, 'dataset')  # ./dataset
    TRAIN_PATH = os.path.join(DATASET_PATH, 'Train')  # ./dataset/Train
    VALIDATION_PATH = os.path.join(DATASET_PATH, 'Val')  # ./dataset/Val
    TEST_PATH = os.path.join(DATASET_PATH, 'Test')  # ./dataset/Test
    
    # ==================== OUTPUT PATHS ====================
    MODEL_DIR = os.path.join(BASE_DIR, 'models')  # ./models
    LOG_DIR = os.path.join(BASE_DIR, 'logs')  # ./logs
    TENSORBOARD_DIR = os.path.join(LOG_DIR, 'tensorboard')
    
    # ==================== MODEL PARAMETERS ====================
    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32
    EPOCHS = 50
    INITIAL_EPOCHS = 25  # Phase 1: Train head only
    FINE_TUNE_EPOCHS = 25  # Phase 2: Fine-tuning
    
    # Optimization
    LEARNING_RATE = 0.001
    FINE_TUNE_LEARNING_RATE = 0.0001
    OPTIMIZER = 'adam'  # adam, sgd, rmsprop
    
    # Model architecture
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
            'description': 'VGG16 - Very slow, large model size'
        },
        'densenet121': {
            'model': DenseNet121,
            'input_shape': (224, 224, 3),
            'weights': 'imagenet',
            'description': 'DenseNet121 - Excellent accuracy, memory intensive'
        }
    }
    
    # Data augmentation settings
    AUGMENTATION = {
        'rotation_range': 40,
        'width_shift_range': 0.2,
        'height_shift_range': 0.2,
        'shear_range': 0.2,
        'zoom_range': 0.2,
        'horizontal_flip': True,
        'fill_mode': 'nearest'
    }
    
    # Callback settings
    EARLY_STOPPING_PATIENCE = 10
    REDUCE_LR_PATIENCE = 5
    REDUCE_LR_FACTOR = 0.2
    MIN_LR = 1e-7
    
    # Fine-tuning settings
    FINE_TUNE_LAYERS = 50  # Number of layers to unfreeze from the end
    
    # 29 Class Names (PlantVillage Dataset)
    CLASS_NAMES = [
        'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
        'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy',
        'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust',
        'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight',
        'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Peach___Bacterial_spot', 'Peach___healthy',
        'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight',
        'Strawberry___healthy', 'Strawberry___Leaf_scorch',
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


# ============================================================================
# CUSTOM CALLBACKS
# ============================================================================

class TimeHistory(Callback):
    """Callback to log training time per epoch"""
    
    def on_train_begin(self, logs=None):
        self.epoch_times = []
        self.total_start = time.time()
    
    def on_epoch_begin(self, epoch, logs=None):
        self.epoch_start = time.time()
    
    def on_epoch_end(self, epoch, logs=None):
        epoch_time = time.time() - self.epoch_start
        self.epoch_times.append(epoch_time)
        print(f" - {epoch_time:.2f}s/epoch")
    
    def on_train_end(self, logs=None):
        total_time = time.time() - self.total_start
        print(f"\n⏱️ Total training time: {total_time:.2f}s ({total_time/60:.2f}min)")


class ProgressCallback(Callback):
    """Custom callback to display progress in a user-friendly way"""
    
    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        accuracy = logs.get('accuracy', 0)
        val_accuracy = logs.get('val_accuracy', 0)
        loss = logs.get('loss', 0)
        val_loss = logs.get('val_loss', 0)
        
        # Create progress bar
        bar_length = 30
        progress = (epoch + 1) / self.params['epochs']
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\nEpoch {epoch+1}/{self.params['epochs']} {bar} {progress*100:.1f}%")
        print(f"  📈 Train - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")
        print(f"  📉 Val   - Loss: {val_loss:.4f}, Accuracy: {val_accuracy:.4f}")


# ============================================================================
# DATASET MANAGER
# ============================================================================

class DatasetManager:
    """Manages dataset loading, validation, and preprocessing"""
    
    def __init__(self, config):
        self.config = config
        self.train_generator = None
        self.val_generator = None
        self.test_generator = None
        self.num_classes = 0
        self.class_names = []
        self.class_indices = {}
    
    def validate_dataset(self):
        """Validate dataset structure and return status"""
        print("\n" + "="*70)
        print("📁 DATASET VALIDATION")
        print("="*70)
        
        issues = []
        warnings = []
        
        # Print paths being checked
        print(f"\n📂 Checking paths:")
        print(f"   Dataset root: {self.config.DATASET_PATH}")
        print(f"   Train path: {self.config.TRAIN_PATH}")
        print(f"   Validation path: {self.config.VALIDATION_PATH}")
        print(f"   Test path: {self.config.TEST_PATH}")
        
        # Check dataset directory
        if not os.path.exists(self.config.DATASET_PATH):
            issues.append(f"Dataset directory not found: {self.config.DATASET_PATH}")
        else:
            print(f"✅ Dataset directory exists")
        
        # Check train directory
        if not os.path.exists(self.config.TRAIN_PATH):
            issues.append(f"Training directory not found: {self.config.TRAIN_PATH}")
        else:
            # Count classes and images
            classes = [d for d in os.listdir(self.config.TRAIN_PATH) 
                      if os.path.isdir(os.path.join(self.config.TRAIN_PATH, d))]
            self.num_classes = len(classes)
            
            if self.num_classes == 0:
                issues.append("No class directories found in training folder")
            else:
                print(f"✅ Found {self.num_classes} classes in training set")
                
                # Expected classes (29)
                if self.num_classes != 29:
                    warnings.append(f"Expected 29 classes, found {self.num_classes}")
        
        # Check validation directory
        val_exists = os.path.exists(self.config.VALIDATION_PATH)
        test_exists = os.path.exists(self.config.TEST_PATH)
        
        print(f"✅ Validation directory: {'Found' if val_exists else 'Not found (will use split)'}")
        print(f"✅ Test directory: {'Found' if test_exists else 'Not found (will use split)'}")
        
        if issues:
            print("\n❌ Issues found:")
            for issue in issues:
                print(f"   • {issue}")
            return False
        
        if warnings:
            print("\n⚠️ Warnings:")
            for warning in warnings:
                print(f"   • {warning}")
        
        return True
    
    def load_data(self, use_augmentation=True):
        """Load data using ImageDataGenerator"""
        print("\n" + "="*70)
        print("📊 LOADING DATA")
        print("="*70)
        
        # Data augmentation for training
        if use_augmentation:
            train_datagen = ImageDataGenerator(
                rescale=1./255,
                rotation_range=self.config.AUGMENTATION['rotation_range'],
                width_shift_range=self.config.AUGMENTATION['width_shift_range'],
                height_shift_range=self.config.AUGMENTATION['height_shift_range'],
                shear_range=self.config.AUGMENTATION['shear_range'],
                zoom_range=self.config.AUGMENTATION['zoom_range'],
                horizontal_flip=self.config.AUGMENTATION['horizontal_flip'],
                fill_mode=self.config.AUGMENTATION['fill_mode']
            )
            print("✅ Training augmentation enabled")
        else:
            train_datagen = ImageDataGenerator(rescale=1./255)
            print("✅ Training augmentation disabled")
        
        # Only rescaling for validation/test
        val_test_datagen = ImageDataGenerator(rescale=1./255)
        
        # Check if validation folder exists
        if os.path.exists(self.config.VALIDATION_PATH):
            # Use separate validation folder
            print("📂 Using separate validation folder")
            
            self.train_generator = train_datagen.flow_from_directory(
                self.config.TRAIN_PATH,
                target_size=self.config.IMG_SIZE,
                batch_size=self.config.BATCH_SIZE,
                class_mode='categorical',
                shuffle=True
            )
            
            self.val_generator = val_test_datagen.flow_from_directory(
                self.config.VALIDATION_PATH,
                target_size=self.config.IMG_SIZE,
                batch_size=self.config.BATCH_SIZE,
                class_mode='categorical',
                shuffle=False
            )
            
        else:
            # Use train/validation split
            print("📂 Using 80/20 split from training data")
            
            train_datagen_split = ImageDataGenerator(
                rescale=1./255,
                validation_split=0.2,
                **self.config.AUGMENTATION
            )
            
            self.train_generator = train_datagen_split.flow_from_directory(
                self.config.TRAIN_PATH,
                target_size=self.config.IMG_SIZE,
                batch_size=self.config.BATCH_SIZE,
                class_mode='categorical',
                subset='training',
                shuffle=True
            )
            
            self.val_generator = train_datagen_split.flow_from_directory(
                self.config.TRAIN_PATH,
                target_size=self.config.IMG_SIZE,
                batch_size=self.config.BATCH_SIZE,
                class_mode='categorical',
                subset='validation',
                shuffle=False
            )
        
        # Load test data if available
        if os.path.exists(self.config.TEST_PATH):
            self.test_generator = val_test_datagen.flow_from_directory(
                self.config.TEST_PATH,
                target_size=self.config.IMG_SIZE,
                batch_size=self.config.BATCH_SIZE,
                class_mode='categorical',
                shuffle=False
            )
            print(f"✅ Test data loaded: {self.test_generator.samples} images")
        
        # Get class information
        self.num_classes = self.train_generator.num_classes
        self.class_indices = self.train_generator.class_indices
        self.class_names = list(self.class_indices.keys())
        
        print(f"\n📊 Dataset Statistics:")
        print(f"   Classes: {self.num_classes}")
        print(f"   Training samples: {self.train_generator.samples}")
        print(f"   Validation samples: {self.val_generator.samples}")
        
        return True
    
    def compute_class_weights(self):
        """Compute class weights for imbalanced dataset"""
        print("\n" + "="*70)
        print("⚖️ COMPUTING CLASS WEIGHTS")
        print("="*70)
        
        # Get class labels
        class_labels = self.train_generator.classes
        
        # Compute class weights
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(class_labels),
            y=class_labels
        )
        
        class_weight_dict = dict(enumerate(class_weights))
        
        print(f"Class weight range: {min(class_weights):.3f} - {max(class_weights):.3f}")
        
        # Display sample weights
        print("\nSample class weights:")
        for i, (class_name, weight) in enumerate(zip(self.class_names[:5], class_weights[:5])):
            display_name = self.config.DISPLAY_NAMES.get(class_name, class_name)
            print(f"   {display_name[:35]}: {weight:.3f}")
        
        if len(self.class_names) > 5:
            print(f"   ... and {len(self.class_names)-5} more")
        
        return class_weight_dict
    
    def get_class_distribution(self):
        """Get class distribution statistics"""
        distribution = {}
        for class_name, idx in self.class_indices.items():
            # Count images in training set for this class
            class_path = os.path.join(self.config.TRAIN_PATH, class_name)
            if os.path.exists(class_path):
                count = len([f for f in os.listdir(class_path) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                distribution[self.config.DISPLAY_NAMES.get(class_name, class_name)] = count
        
        return distribution


# ============================================================================
# MODEL BUILDER
# ============================================================================

class ModelBuilder:
    """Builds and compiles the model architecture"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.base_model = None
        self.base_model_name = 'mobilenetv2'
    
    def build_model(self, num_classes, base_model_name='mobilenetv2', fine_tune=False):
        """Build the model architecture using transfer learning"""
        print("\n" + "="*70)
        print("🏗️ BUILDING MODEL ARCHITECTURE")
        print("="*70)
        
        self.base_model_name = base_model_name
        
        # Get base model configuration
        base_config = self.config.BASE_MODELS.get(base_model_name, self.config.BASE_MODELS['mobilenetv2'])
        base_model_class = base_config['model']
        input_shape = base_config['input_shape']
        weights = base_config['weights']
        
        print(f"📋 Base Model: {base_model_name.upper()}")
        print(f"   Input shape: {input_shape}")
        print(f"   Pre-trained weights: {weights}")
        print(f"   Output classes: {num_classes}")
        
        # Load base model
        self.base_model = base_model_class(
            input_shape=input_shape,
            include_top=False,
            weights=weights
        )
        
        # Freeze base model layers
        if not fine_tune:
            self.base_model.trainable = False
            print(f"   Base model frozen (trainable=False)")
        
        # Build custom classification head
        self.model = Sequential([
            self.base_model,
            GlobalAveragePooling2D(name='global_avg_pool'),
            Dense(512, activation='relu', name='dense_1'),
            BatchNormalization(name='bn_1'),
            Dropout(0.5, name='dropout_1'),
            Dense(256, activation='relu', name='dense_2'),
            BatchNormalization(name='bn_2'),
            Dropout(0.3, name='dropout_2'),
            Dense(128, activation='relu', name='dense_3'),
            BatchNormalization(name='bn_3'),
            Dropout(0.2, name='dropout_3'),
            Dense(num_classes, activation='softmax', name='output')
        ])
        
        # Count parameters
        total_params = self.model.count_params()
        trainable_params = sum([tf.keras.backend.count_params(w) for w in self.model.trainable_weights])
        
        print(f"\n📊 Model Statistics:")
        print(f"   Total parameters: {total_params:,}")
        print(f"   Trainable parameters: {trainable_params:,}")
        print(f"   Non-trainable parameters: {total_params - trainable_params:,}")
        
        return self.model
    
    def compile_model(self, learning_rate=0.001, optimizer='adam'):
        """Compile the model"""
        print(f"\n🔧 Compiling model...")
        print(f"   Optimizer: {optimizer}")
        print(f"   Learning rate: {learning_rate}")
        
        if optimizer == 'adam':
            opt = Adam(learning_rate=learning_rate)
        elif optimizer == 'sgd':
            opt = SGD(learning_rate=learning_rate, momentum=0.9)
        elif optimizer == 'rmsprop':
            opt = RMSprop(learning_rate=learning_rate)
        else:
            opt = Adam(learning_rate=learning_rate)
        
        self.model.compile(
            optimizer=opt,
            loss='categorical_crossentropy',
            metrics=['accuracy', Precision(name='precision'), Recall(name='recall'), AUC(name='auc')]
        )
        
        print("✅ Model compiled successfully")
    
    def setup_fine_tuning(self, unfreeze_layers=50):
        """Setup fine-tuning by unfreezing some layers"""
        print("\n" + "="*70)
        print("🔧 SETTING UP FINE-TUNING")
        print("="*70)
        
        # Make base model trainable
        self.base_model.trainable = True
        
        # Freeze all layers first
        for layer in self.base_model.layers:
            layer.trainable = False
        
        # Unfreeze last 'unfreeze_layers' layers
        for layer in self.base_model.layers[-unfreeze_layers:]:
            layer.trainable = True
        
        trainable_layers = sum(1 for layer in self.base_model.layers if layer.trainable)
        
        print(f"   Total layers in base model: {len(self.base_model.layers)}")
        print(f"   Trainable layers after fine-tuning: {trainable_layers}")
        print(f"   Unfrozen layers: {unfreeze_layers}")
        
        # Recompile with lower learning rate
        fine_tune_lr = self.config.FINE_TUNE_LEARNING_RATE
        self.compile_model(learning_rate=fine_tune_lr, optimizer='adam')
        
        print(f"   New learning rate: {fine_tune_lr}")
        
        return self.model
    
    def get_model_summary(self):
        """Print model summary"""
        print("\n" + "="*70)
        print("📋 MODEL SUMMARY")
        print("="*70)
        self.model.summary()


# ============================================================================
# TRAINER
# ============================================================================

class Trainer:
    """Handles model training with callbacks"""
    
    def __init__(self, config):
        self.config = config
        self.history = None
        self.best_epoch = 0
        self.best_val_accuracy = 0
    
    def create_callbacks(self, model_dir='models', phase='head'):
        """Create training callbacks"""
        callbacks_list = []
        
        # Create directories
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(self.config.TENSORBOARD_DIR, exist_ok=True)
        
        # 1. Model Checkpoint - Save best model
        checkpoint = ModelCheckpoint(
            filepath=os.path.join(model_dir, f'best_model_{phase}.h5'),
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        )
        callbacks_list.append(checkpoint)
        
        # 2. Early Stopping
        early_stop = EarlyStopping(
            monitor='val_loss',
            patience=self.config.EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1
        )
        callbacks_list.append(early_stop)
        
        # 3. Reduce Learning Rate on Plateau
        reduce_lr = ReduceLROnPlateau(
            monitor='val_loss',
            factor=self.config.REDUCE_LR_FACTOR,
            patience=self.config.REDUCE_LR_PATIENCE,
            min_lr=self.config.MIN_LR,
            verbose=1
        )
        callbacks_list.append(reduce_lr)
        
        # 4. CSV Logger
        csv_logger = CSVLogger(
            filename=os.path.join(model_dir, f'training_log_{phase}.csv'),
            append=True
        )
        callbacks_list.append(csv_logger)
        
        # 5. TensorBoard
        tensorboard = TensorBoard(
            log_dir=os.path.join(self.config.TENSORBOARD_DIR, datetime.now().strftime("%Y%m%d-%H%M%S")),
            histogram_freq=1
        )
        callbacks_list.append(tensorboard)
        
        # 6. Time History
        time_history = TimeHistory()
        callbacks_list.append(time_history)
        
        # 7. Progress Callback (optional, can be verbose)
        progress_callback = ProgressCallback()
        callbacks_list.append(progress_callback)
        
        print(f"✅ Created {len(callbacks_list)} callbacks for {phase} phase")
        
        return callbacks_list
    
    def train_phase1(self, model, train_generator, val_generator, class_weight_dict=None):
        """Phase 1: Train only the classification head"""
        print("\n" + "="*70)
        print("🚀 PHASE 1: TRAINING CLASSIFICATION HEAD")
        print("="*70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Epochs: {self.config.INITIAL_EPOCHS}")
        print(f"Training samples: {train_generator.samples}")
        print(f"Validation samples: {val_generator.samples}")
        
        callbacks = self.create_callbacks(phase='head')
        
        history = model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=self.config.INITIAL_EPOCHS,
            callbacks=callbacks,
            class_weight=class_weight_dict,
            verbose=1
        )
        
        print(f"\n✅ Phase 1 completed!")
        print(f"   Best training accuracy: {max(history.history['accuracy']):.4f}")
        print(f"   Best validation accuracy: {max(history.history['val_accuracy']):.4f}")
        
        return history
    
    def train_phase2(self, model, train_generator, val_generator, class_weight_dict=None):
        """Phase 2: Fine-tuning"""
        print("\n" + "="*70)
        print("🚀 PHASE 2: FINE-TUNING")
        print("="*70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Epochs: {self.config.FINE_TUNE_EPOCHS}")
        print(f"Training samples: {train_generator.samples}")
        print(f"Validation samples: {val_generator.samples}")
        
        callbacks = self.create_callbacks(phase='fine_tune')
        
        history = model.fit(
            train_generator,
            validation_data=val_generator,
            epochs=self.config.FINE_TUNE_EPOCHS,
            callbacks=callbacks,
            class_weight=class_weight_dict,
            verbose=1
        )
        
        print(f"\n✅ Phase 2 completed!")
        
        return history
    
    def combine_history(self, history1, history2):
        """Combine histories from both phases"""
        combined = {}
        
        for key in history1.history.keys():
            if key in history2.history:
                combined[key] = history1.history[key] + history2.history[key]
            else:
                combined[key] = history1.history[key]
        
        # Find best validation accuracy
        val_acc = combined.get('val_accuracy', [])
        if val_acc:
            self.best_val_accuracy = max(val_acc)
            self.best_epoch = val_acc.index(self.best_val_accuracy) + 1
        
        return combined


# ============================================================================
# MODEL EVALUATOR
# ============================================================================

class ModelEvaluator:
    """Evaluates trained model performance"""
    
    def __init__(self, config):
        self.config = config
    
    def evaluate(self, model, test_generator):
        """Evaluate model on test data"""
        print("\n" + "="*70)
        print("📊 MODEL EVALUATION")
        print("="*70)
        
        if test_generator is None:
            print("⚠️ No test data available. Skipping evaluation.")
            return None
        
        # Get predictions
        print("🔍 Generating predictions...")
        predictions = model.predict(test_generator, verbose=1)
        predicted_classes = np.argmax(predictions, axis=1)
        true_classes = test_generator.classes
        
        # Calculate metrics
        accuracy = accuracy_score(true_classes, predicted_classes)
        precision = precision_score(true_classes, predicted_classes, average='weighted')
        recall = recall_score(true_classes, predicted_classes, average='weighted')
        f1 = f1_score(true_classes, predicted_classes, average='weighted')
        
        print(f"\n📈 Test Results:")
        print(f"   Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"   Precision: {precision:.4f}")
        print(f"   Recall:    {recall:.4f}")
        print(f"   F1-Score:  {f1:.4f}")
        
        # Generate classification report
        class_names = list(test_generator.class_indices.keys())
        display_names = [self.config.DISPLAY_NAMES.get(name, name) for name in class_names]
        
        report = classification_report(
            true_classes,
            predicted_classes,
            target_names=display_names,
            output_dict=True
        )
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'classification_report': report,
            'predictions': predictions,
            'predicted_classes': predicted_classes,
            'true_classes': true_classes
        }
    
    def plot_confusion_matrix(self, true_classes, predicted_classes, class_names, save_path='models/confusion_matrix.png'):
        """Plot and save confusion matrix"""
        cm = confusion_matrix(true_classes, predicted_classes)
        display_names = [self.config.DISPLAY_NAMES.get(name, name)[:20] for name in class_names]
        
        plt.figure(figsize=(18, 16))
        sns.heatmap(cm, annot=False, fmt='d', cmap='Blues',
                    xticklabels=display_names, yticklabels=display_names)
        plt.xlabel('Predicted Class', fontsize=12)
        plt.ylabel('True Class', fontsize=12)
        plt.title('Confusion Matrix', fontsize=14, fontweight='bold')
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(fontsize=8)
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Confusion matrix saved to {save_path}")


# ============================================================================
# MODEL SAVER
# ============================================================================

class ModelSaver:
    """Saves model and related artifacts"""
    
    def __init__(self, config):
        self.config = config
    
    def save_model(self, model, history, class_indices, model_dir='models'):
        """Save model and all related artifacts"""
        print("\n" + "="*70)
        print("💾 SAVING MODEL AND ARTIFACTS")
        print("="*70)
        
        os.makedirs(model_dir, exist_ok=True)
        
        # 1. Save model in H5 format
        h5_path = os.path.join(model_dir, 'plant_disease_model.h5')
        model.save(h5_path)
        print(f"✅ Model saved to {h5_path}")
        
        # 2. Save model in Keras format
        keras_path = os.path.join(model_dir, 'plant_disease_model.keras')
        model.save(keras_path)
        print(f"✅ Model saved to {keras_path}")
        
        # 3. Save class indices
        indices_path = os.path.join(model_dir, 'class_indices.json')
        with open(indices_path, 'w') as f:
            json.dump(class_indices, f, indent=2)
        print(f"✅ Class indices saved to {indices_path}")
        
        # 4. Save training history
        history_path = os.path.join(model_dir, 'training_history.json')
        serializable_history = {k: [float(x) for x in v] for k, v in history.items()}
        with open(history_path, 'w') as f:
            json.dump(serializable_history, f, indent=2)
        print(f"✅ Training history saved to {history_path}")
        
        # 5. Save model metadata
        metadata = {
            'model_name': 'Plant Disease Detection Model',
            'version': '1.0.0',
            'framework': f'TensorFlow {tf.__version__}',
            'tensorflow_version': tf.__version__,
            'python_version': sys.version,
            'training_date': datetime.now().isoformat(),
            'num_classes': len(class_indices),
            'class_names': list(class_indices.keys()),
            'input_shape': list(self.config.IMG_SIZE) + [3],
            'final_accuracy': float(history.get('accuracy', [0])[-1]),
            'final_val_accuracy': float(history.get('val_accuracy', [0])[-1]),
            'best_val_accuracy': max(history.get('val_accuracy', [0])),
            'total_epochs': len(history.get('accuracy', []))
        }
        
        metadata_path = os.path.join(model_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Model metadata saved to {metadata_path}")
        
        return metadata


# ============================================================================
# VISUALIZATION
# ============================================================================

class Visualizer:
    """Creates visualizations for training results"""
    
    def __init__(self, config):
        self.config = config
    
    def plot_training_curves(self, history, save_path='models/training_curves.png'):
        """Plot training and validation curves"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Accuracy plot
        ax1 = axes[0, 0]
        ax1.plot(history['accuracy'], label='Training Accuracy', linewidth=2)
        ax1.plot(history['val_accuracy'], label='Validation Accuracy', linewidth=2)
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Accuracy')
        ax1.set_title('Model Accuracy', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Loss plot
        ax2 = axes[0, 1]
        ax2.plot(history['loss'], label='Training Loss', linewidth=2)
        ax2.plot(history['val_loss'], label='Validation Loss', linewidth=2)
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Loss')
        ax2.set_title('Model Loss', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Precision plot
        ax3 = axes[1, 0]
        if 'precision' in history:
            ax3.plot(history['precision'], label='Training Precision', linewidth=2)
        if 'val_precision' in history:
            ax3.plot(history['val_precision'], label='Validation Precision', linewidth=2)
        ax3.set_xlabel('Epoch')
        ax3.set_ylabel('Precision')
        ax3.set_title('Model Precision', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Recall plot
        ax4 = axes[1, 1]
        if 'recall' in history:
            ax4.plot(history['recall'], label='Training Recall', linewidth=2)
        if 'val_recall' in history:
            ax4.plot(history['val_recall'], label='Validation Recall', linewidth=2)
        ax4.set_xlabel('Epoch')
        ax4.set_ylabel('Recall')
        ax4.set_title('Model Recall', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle('Training History', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Training curves saved to {save_path}")
    
    def plot_class_distribution(self, distribution, save_path='models/class_distribution.png'):
        """Plot class distribution"""
        classes = list(distribution.keys())
        counts = list(distribution.values())
        
        plt.figure(figsize=(14, 8))
        bars = plt.barh(classes, counts, color='#4F46E5')
        plt.xlabel('Number of Images')
        plt.title('Class Distribution in Training Set', fontsize=14, fontweight='bold')
        
        for bar, count in zip(bars, counts):
            plt.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2, 
                    f'{count:,}', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✅ Class distribution plot saved to {save_path}")


# ============================================================================
# MAIN TRAINING PIPELINE
# ============================================================================

class TrainingPipeline:
    """Main orchestration class for the entire training process"""
    
    def __init__(self, args):
        self.args = args
        self.config = TrainingConfig()
        self.start_time = None
        self.end_time = None
        
        # Override config with command line arguments
        if args.batch_size:
            self.config.BATCH_SIZE = args.batch_size
        if args.epochs:
            self.config.EPOCHS = args.epochs
            self.config.INITIAL_EPOCHS = args.epochs // 2
            self.config.FINE_TUNE_EPOCHS = args.epochs // 2
        if args.lr:
            self.config.LEARNING_RATE = args.lr
        if args.base_model:
            self.base_model_name = args.base_model
        
        # Initialize components
        self.dataset_manager = DatasetManager(self.config)
        self.model_builder = ModelBuilder(self.config)
        self.trainer = Trainer(self.config)
        self.evaluator = ModelEvaluator(self.config)
        self.model_saver = ModelSaver(self.config)
        self.visualizer = Visualizer(self.config)
        
        # Results storage
        self.model = None
        self.history = None
        self.evaluation_results = None
    
    def print_banner(self):
        """Print training banner"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🌾  F A R M I N T E L   A I  -  T R A I N I N G   P I P E L I N E  🌾     ║
║                                                                               ║
║                        Plant Disease Detection Model                          ║
║                           29 Classes | 9 Crops                                ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def print_configuration(self):
        """Print training configuration"""
        print("\n" + "="*70)
        print("📋 TRAINING CONFIGURATION")
        print("="*70)
        print(f"\n📁 Paths:")
        print(f"   Base directory: {self.config.BASE_DIR}")
        print(f"   Dataset: {self.config.DATASET_PATH}")
        print(f"   Train folder: {self.config.TRAIN_PATH}")
        print(f"   Validation folder: {self.config.VALIDATION_PATH}")
        print(f"   Test folder: {self.config.TEST_PATH}")
        print(f"   Model output: {self.config.MODEL_DIR}")
        print(f"   Logs: {self.config.LOG_DIR}")
        
        print(f"\n🖼️ Image Parameters:")
        print(f"   Image size: {self.config.IMG_SIZE}")
        print(f"   Batch size: {self.config.BATCH_SIZE}")
        print(f"   Data augmentation: Enabled")
        
        print(f"\n🤖 Model Parameters:")
        print(f"   Base model: {self.args.base_model}")
        print(f"   Total epochs: {self.config.EPOCHS}")
        print(f"   Phase 1 epochs: {self.config.INITIAL_EPOCHS}")
        print(f"   Phase 2 epochs: {self.config.FINE_TUNE_EPOCHS}")
        print(f"   Learning rate: {self.config.LEARNING_RATE}")
        print(f"   Fine-tune learning rate: {self.config.FINE_TUNE_LEARNING_RATE}")
        print(f"   Fine-tune layers: {self.config.FINE_TUNE_LAYERS}")
        
        print(f"\n📊 Callback Settings:")
        print(f"   Early stopping patience: {self.config.EARLY_STOPPING_PATIENCE}")
        print(f"   Reduce LR patience: {self.config.REDUCE_LR_PATIENCE}")
        print(f"   Reduce LR factor: {self.config.REDUCE_LR_FACTOR}")
    
    def run(self):
        """Execute the complete training pipeline"""
        self.print_banner()
        self.print_configuration()
        
        self.start_time = datetime.now()
        print(f"\n📅 Pipeline started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Step 1: Validate dataset
        if not self.dataset_manager.validate_dataset():
            print("\n❌ Dataset validation failed. Please check your dataset.")
            return False
        
        # Step 2: Load data
        if not self.dataset_manager.load_data(use_augmentation=True):
            print("\n❌ Data loading failed.")
            return False
        
        # Step 3: Compute class weights
        class_weight_dict = self.dataset_manager.compute_class_weights()
        
        # Step 4: Plot class distribution
        distribution = self.dataset_manager.get_class_distribution()
        self.visualizer.plot_class_distribution(distribution)
        
        # Step 5: Build model
        num_classes = self.dataset_manager.num_classes
        self.model = self.model_builder.build_model(
            num_classes, 
            base_model_name=self.args.base_model,
            fine_tune=False
        )
        self.model_builder.compile_model(learning_rate=self.config.LEARNING_RATE)
        self.model_builder.get_model_summary()
        
        # Step 6: Phase 1 training (head only)
        history1 = self.trainer.train_phase1(
            self.model,
            self.dataset_manager.train_generator,
            self.dataset_manager.val_generator,
            class_weight_dict
        )
        
        # Step 7: Setup fine-tuning
        if self.args.fine_tune:
            self.model_builder.setup_fine_tuning(unfreeze_layers=self.config.FINE_TUNE_LAYERS)
            
            # Step 8: Phase 2 training (fine-tuning)
            history2 = self.trainer.train_phase2(
                self.model,
                self.dataset_manager.train_generator,
                self.dataset_manager.val_generator,
                class_weight_dict
            )
            
            # Combine histories
            self.history = self.trainer.combine_history(history1, history2)
        else:
            self.history = history1.history
        
        # Step 9: Visualize training curves
        self.visualizer.plot_training_curves(self.history)
        
        # Step 10: Save model
        self.model_saver.save_model(
            self.model,
            self.history,
            self.dataset_manager.class_indices,
            self.args.model_dir
        )
        
        # Step 11: Evaluate model
        if self.dataset_manager.test_generator:
            self.evaluation_results = self.evaluator.evaluate(
                self.model,
                self.dataset_manager.test_generator
            )
            
            if self.evaluation_results:
                self.evaluator.plot_confusion_matrix(
                    self.evaluation_results['true_classes'],
                    self.evaluation_results['predicted_classes'],
                    self.dataset_manager.class_names
                )
        
        # Step 12: Save training report
        self.save_training_report()
        
        self.end_time = datetime.now()
        self.print_summary()
        
        return True
    
    def save_training_report(self):
        """Save comprehensive training report"""
        report = {
            'training_date': self.start_time.isoformat(),
            'completion_date': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': (self.end_time - self.start_time).total_seconds() if self.end_time else None,
            'configuration': {
                'base_model': self.args.base_model,
                'batch_size': self.config.BATCH_SIZE,
                'total_epochs': self.config.EPOCHS,
                'initial_epochs': self.config.INITIAL_EPOCHS,
                'fine_tune_epochs': self.config.FINE_TUNE_EPOCHS,
                'learning_rate': self.config.LEARNING_RATE,
                'fine_tune_learning_rate': self.config.FINE_TUNE_LEARNING_RATE,
                'image_size': list(self.config.IMG_SIZE),
                'fine_tune_enabled': self.args.fine_tune
            },
            'dataset': {
                'num_classes': self.dataset_manager.num_classes,
                'train_samples': self.dataset_manager.train_generator.samples,
                'val_samples': self.dataset_manager.val_generator.samples,
                'test_samples': self.dataset_manager.test_generator.samples if self.dataset_manager.test_generator else 0
            },
            'performance': {
                'best_val_accuracy': self.trainer.best_val_accuracy,
                'best_epoch': self.trainer.best_epoch,
                'final_train_accuracy': float(self.history.get('accuracy', [0])[-1]),
                'final_val_accuracy': float(self.history.get('val_accuracy', [0])[-1])
            }
        }
        
        if self.evaluation_results:
            report['test_performance'] = {
                'accuracy': self.evaluation_results['accuracy'],
                'precision': self.evaluation_results['precision'],
                'recall': self.evaluation_results['recall'],
                'f1_score': self.evaluation_results['f1_score']
            }
        
        report_path = os.path.join(self.args.model_dir, 'training_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Training report saved to {report_path}")
    
    def print_summary(self):
        """Print training summary"""
        duration = (self.end_time - self.start_time).total_seconds()
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        print("\n" + "="*70)
        print("🎉 TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        print(f"\n📊 Summary:")
        print(f"   Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   End time: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Duration: {hours}h {minutes}m {seconds}s")
        print(f"   Best validation accuracy: {self.trainer.best_val_accuracy:.4f} ({self.trainer.best_val_accuracy*100:.2f}%)")
        
        if self.evaluation_results:
            print(f"   Test accuracy: {self.evaluation_results['accuracy']:.4f} ({self.evaluation_results['accuracy']*100:.2f}%)")
        
        print(f"\n📁 Output files saved to: {self.args.model_dir}/")
        print(f"\n🚀 Next steps:")
        print(f"   1. Test the model: python scripts/predict.py --image path/to/leaf.jpg")
        print(f"   2. Convert to TFLite: python scripts/convert_to_tflite.py")
        print(f"   3. Start backend: python run.py")
        print(f"   4. Launch frontend: Open frontend/index.html")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='FarmIntel AI - Complete Training Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic training (50 epochs, MobileNetV2)
  python train.py
  
  # Training with custom parameters
  python train.py --epochs 100 --batch-size 64 --lr 0.0005
  
  # Training with fine-tuning
  python train.py --fine-tune --base-model efficientnetb0
  
  # Quick test (5 epochs)
  python train.py --quick-test
  
  # Custom model directory
  python train.py --model-dir my_models
        """
    )
    
    # Dataset arguments
    parser.add_argument('--data', '-d', default=None,
                       help='Dataset directory (optional, uses config default)')
    parser.add_argument('--model-dir', '-m', default='models',
                       help='Model output directory (default: models)')
    
    # Training arguments
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for training (default: 32)')
    parser.add_argument('--epochs', type=int, default=50,
                       help='Number of training epochs (default: 50)')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Initial learning rate (default: 0.001)')
    parser.add_argument('--base-model', '-b', default='mobilenetv2',
                       choices=['mobilenetv2', 'efficientnetb0', 'resnet50', 'vgg16', 'densenet121'],
                       help='Base model architecture (default: mobilenetv2)')
    parser.add_argument('--fine-tune', action='store_true',
                       help='Enable fine-tuning (unfreeze base model layers)')
    parser.add_argument('--quick-test', action='store_true',
                       help='Run quick test with fewer epochs (5 epochs)')
    
    # Hardware arguments
    parser.add_argument('--no-gpu', action='store_true',
                       help='Disable GPU usage (force CPU)')
    
    args = parser.parse_args()
    
    # Override dataset path if provided
    if args.data:
        TrainingConfig.DATASET_PATH = args.data
        TrainingConfig.TRAIN_PATH = os.path.join(args.data, 'Train')
        TrainingConfig.VALIDATION_PATH = os.path.join(args.data, 'Val')
        TrainingConfig.TEST_PATH = os.path.join(args.data, 'Test')
    
    # Quick test mode
    if args.quick_test:
        print("⚠️ Running in QUICK TEST mode (5 epochs only)")
        args.epochs = 5
    
    # Disable GPU if requested
    if args.no_gpu:
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        print("⚠️ GPU disabled. Using CPU only.")
    
    # Create and run pipeline
    pipeline = TrainingPipeline(args)
    success = pipeline.run()
    
    if not success:
        print("\n❌ Training pipeline failed.")
        sys.exit(1)
    
    print("\n✅ Training pipeline completed successfully!")
    sys.exit(0)


if __name__ == '__main__':
    main()
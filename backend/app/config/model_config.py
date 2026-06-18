"""
FarmIntel AI - Model Configuration
Hyperparameters and architecture settings for the plant disease detection model
Supports 29 disease classes from PlantVillage dataset
"""

import os


class ModelConfig:
    """Configuration for AI/ML model training and inference"""
    
    # ========================================
    # Dataset Information
    # ========================================
    NUM_CLASSES = 29  # Total disease classes (including healthy)
    
    # Dataset paths
    DATASET_PATH = 'dataset'
    TRAIN_PATH = os.path.join(DATASET_PATH, 'train')
    VALIDATION_PATH = os.path.join(DATASET_PATH, 'validation')
    TEST_PATH = os.path.join(DATASET_PATH, 'test')
    
    # Data split ratios
    TRAIN_SPLIT = 0.7
    VALIDATION_SPLIT = 0.2
    TEST_SPLIT = 0.1
    
    # ========================================
    # Model Architecture
    # ========================================
    BASE_MODEL = 'MobileNetV2'  # Options: 'MobileNetV2', 'EfficientNetB0', 'ResNet50', 'VGG16'
    INPUT_SHAPE = (224, 224, 3)  # Height, Width, Channels
    
    # Transfer learning settings
    USE_PRETRAINED_WEIGHTS = True
    PRETRAINED_WEIGHTS_SOURCE = 'imagenet'
    FREEZE_BASE_LAYERS = True
    FREEZE_UNTIL = None  # Layer index to freeze up to
    
    # Custom head architecture
    HEAD_LAYERS = [
        {'type': 'GlobalAveragePooling2D'},
        {'type': 'Dense', 'units': 256, 'activation': 'relu'},
        {'type': 'Dropout', 'rate': 0.5},
        {'type': 'Dense', 'units': 128, 'activation': 'relu'},
        {'type': 'Dropout', 'rate': 0.3},
        {'type': 'Dense', 'units': 29, 'activation': 'softmax'}  # 29 output classes
    ]
    
    # ========================================
    # Training Hyperparameters
    # ========================================
    OPTIMIZER = 'adam'
    LEARNING_RATE = 0.001
    LEARNING_RATE_DECAY = 0.96
    DECAY_STEPS = 1000
    USE_COSINE_DECAY = False
    
    LOSS = 'categorical_crossentropy'
    METRICS = ['accuracy', 'precision', 'recall', 'auc']
    
    BATCH_SIZE = 32
    VALIDATION_BATCH_SIZE = 32
    EPOCHS = 50
    INITIAL_EPOCH = 0
    
    # ========================================
    # Callbacks Settings
    # ========================================
    EARLY_STOPPING_PATIENCE = 10
    EARLY_STOPPING_MIN_DELTA = 0.001
    EARLY_STOPPING_RESTORE_BEST = True
    
    REDUCE_LR_PATIENCE = 5
    REDUCE_LR_FACTOR = 0.2
    REDUCE_LR_MIN_LR = 1e-7
    
    CHECKPOINT_MONITOR = 'val_accuracy'
    CHECKPOINT_MODE = 'max'
    CHECKPOINT_SAVE_BEST_ONLY = True
    CHECKPOINT_VERBOSE = 1
    
    # ========================================
    # Data Augmentation
    # ========================================
    AUGMENTATION_TRAIN = {
        'rotation_range': 40,
        'width_shift_range': 0.2,
        'height_shift_range': 0.2,
        'shear_range': 0.2,
        'zoom_range': 0.2,
        'horizontal_flip': True,
        'fill_mode': 'nearest',
        'rescale': 1./255
    }
    
    AUGMENTATION_VALIDATION = {
        'rescale': 1./255
    }
    
    AUGMENTATION_TEST = {
        'rescale': 1./255
    }
    
    # ========================================
    # Inference Settings
    # ========================================
    CONFIDENCE_THRESHOLD = 0.5
    SEVERITY_THRESHOLDS = {
        'severe': 85,
        'moderate': 70,
        'mild': 50,
        'low': 0
    }
    
    SEVERITY_MESSAGES = {
        'severe': 'Immediate action needed - Apply treatment today',
        'moderate': 'Action within 3 days - Monitor closely',
        'mild': 'Monitor and treat if spreads',
        'low': 'Retake clearer photo for accurate detection'
    }
    
    # ========================================
    # 29 Class Labels (PlantVillage Dataset)
    # ========================================
    CLASS_NAMES = [
        # Apple (4)
        'Apple___Apple_scab',
        'Apple___Black_rot',
        'Apple___Cedar_apple_rust',
        'Apple___healthy',
        
        # Bell Pepper (2)
        'Pepper,_bell___Bacterial_spot',
        'Pepper,_bell___healthy',
        
        # Cherry (2)
        'Cherry_(including_sour)___healthy',
        'Cherry_(including_sour)___Powdery_mildew',
        
        # Corn/Maize (4)
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust',
        'Corn_(maize)___healthy',
        'Corn_(maize)___Northern_Leaf_Blight',
        
        # Grape (4)
        'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)',
        'Grape___healthy',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        
        # Peach (2)
        'Peach___Bacterial_spot',
        'Peach___healthy',
        
        # Potato (3)
        'Potato___Early_blight',
        'Potato___healthy',
        'Potato___Late_blight',
        
        # Strawberry (2)
        'Strawberry___healthy',
        'Strawberry___Leaf_scorch',
        
        # Tomato (6)
        'Tomato___Bacterial_spot',
        'Tomato___Early_blight',
        'Tomato___healthy',
        'Tomato___Late_blight',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
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
        'Apple': ['Apple Scab', 'Apple Black Rot', 'Apple Cedar Rust', 'Apple Healthy'],
        'Bell Pepper': ['Bell Pepper Bacterial Spot', 'Bell Pepper Healthy'],
        'Cherry': ['Cherry Healthy', 'Cherry Powdery Mildew'],
        'Corn': ['Corn Cercospora Leaf Spot', 'Corn Common Rust', 'Corn Healthy', 'Corn Northern Leaf Blight'],
        'Grape': ['Grape Black Rot', 'Grape Esca', 'Grape Healthy', 'Grape Leaf Blight'],
        'Peach': ['Peach Bacterial Spot', 'Peach Healthy'],
        'Potato': ['Potato Early Blight', 'Potato Healthy', 'Potato Late Blight'],
        'Strawberry': ['Strawberry Healthy', 'Strawberry Leaf Scorch'],
        'Tomato': ['Tomato Bacterial Spot', 'Tomato Early Blight', 'Tomato Healthy', 
                   'Tomato Late Blight', 'Tomato Septoria Leaf Spot', 'Tomato Yellow Leaf Curl Virus']
    }
    
    # ========================================
    # Helper Methods
    # ========================================
    
    @classmethod
    def get_num_classes(cls):
        """Get number of output classes"""
        return cls.NUM_CLASSES
    
    @classmethod
    def get_input_shape(cls):
        """Get input shape for model"""
        return cls.INPUT_SHAPE
    
    @classmethod
    def get_training_config(cls):
        """Get training configuration as dictionary"""
        return {
            'batch_size': cls.BATCH_SIZE,
            'epochs': cls.EPOCHS,
            'learning_rate': cls.LEARNING_RATE,
            'optimizer': cls.OPTIMIZER,
            'loss': cls.LOSS,
            'metrics': cls.METRICS,
            'early_stopping_patience': cls.EARLY_STOPPING_PATIENCE,
            'reduce_lr_patience': cls.REDUCE_LR_PATIENCE,
            'validation_split': cls.VALIDATION_SPLIT
        }
    
    @classmethod
    def get_augmentation_config(cls, phase='train'):
        """Get augmentation configuration for specified phase"""
        if phase == 'train':
            return cls.AUGMENTATION_TRAIN
        elif phase == 'validation':
            return cls.AUGMENTATION_VALIDATION
        elif phase == 'test':
            return cls.AUGMENTATION_TEST
        return cls.AUGMENTATION_TRAIN
    
    @classmethod
    def get_display_name(cls, class_name):
        """Get user-friendly display name for a class"""
        return cls.DISPLAY_NAMES.get(class_name, class_name.replace('_', ' ').replace('___', ' - '))
    
    @classmethod
    def get_severity_level(cls, confidence):
        """Determine severity level based on confidence score"""
        if confidence >= cls.SEVERITY_THRESHOLDS['severe']:
            return 'severe'
        elif confidence >= cls.SEVERITY_THRESHOLDS['moderate']:
            return 'moderate'
        elif confidence >= cls.SEVERITY_THRESHOLDS['mild']:
            return 'mild'
        else:
            return 'low'
    
    @classmethod
    def get_severity_message(cls, severity):
        """Get message for severity level"""
        return cls.SEVERITY_MESSAGES.get(severity, 'Unknown severity')
    
    @classmethod
    def get_classes_by_crop(cls, crop):
        """Get disease classes for a specific crop"""
        return cls.CROP_GROUPS.get(crop, [])
    
    @classmethod
    def get_all_crops(cls):
        """Get list of all supported crops"""
        return list(cls.CROP_GROUPS.keys())
    
    @classmethod
    def validate_config(cls):
        """Validate configuration values"""
        assert cls.INPUT_SHAPE[0] == cls.INPUT_SHAPE[1], "Input shape must be square"
        assert cls.NUM_CLASSES == len(cls.CLASS_NAMES), f"Number of classes mismatch: {cls.NUM_CLASSES} vs {len(cls.CLASS_NAMES)}"
        assert 0 <= cls.TRAIN_SPLIT <= 1, "Invalid train split"
        assert 0 <= cls.VALIDATION_SPLIT <= 1, "Invalid validation split"
        assert 0 <= cls.TEST_SPLIT <= 1, "Invalid test split"
        total = cls.TRAIN_SPLIT + cls.VALIDATION_SPLIT + cls.TEST_SPLIT
        assert abs(total - 1.0) < 0.01, f"Splits must sum to 1.0 (current: {total})"
        
        return True
#!/usr/bin/env python3
"""
Evaluate Model Script
Evaluates the trained plant disease detection model on test data
Generates classification report, confusion matrix, and performance metrics
"""

import os
import sys
import argparse
import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


class ModelEvaluator:
    """
    Class for evaluating the trained plant disease detection model
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
                 data_dir='dataset', batch_size=32, img_size=224):
        """
        Initialize the model evaluator
        
        Args:
            model_path: Path to the trained model
            data_dir: Path to dataset directory
            batch_size: Batch size for evaluation
            img_size: Image size for evaluation
        """
        self.model_path = Path(model_path)
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.img_size = (img_size, img_size)
        
        self.model = None
        self.test_generator = None
        self.predictions = None
        self.true_labels = None
        self.pred_labels = None
        self.class_names = None
        
        # Results storage
        self.results = {
            'accuracy': 0,
            'precision': 0,
            'recall': 0,
            'f1_score': 0,
            'class_report': None,
            'confusion_matrix': None,
            'per_class_accuracy': {},
            'misclassified_samples': []
        }
    
    def load_model(self):
        """
        Load the trained model
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("🤖 Loading Model")
        print("="*70)
        
        if not self.model_path.exists():
            print(f"❌ Model not found: {self.model_path}")
            print("   Please train the model first: python train_model.py")
            return False
        
        try:
            self.model = load_model(self.model_path)
            print(f"✅ Model loaded from {self.model_path}")
            print(f"   Input shape: {self.model.input_shape}")
            print(f"   Output shape: {self.model.output_shape}")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return False
    
    def load_test_data(self):
        """
        Load test data for evaluation
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("\n" + "="*70)
        print("📊 Loading Test Data")
        print("="*70)
        
        test_dir = self.data_dir / 'test'
        
        if not test_dir.exists():
            print(f"❌ Test directory not found: {test_dir}")
            print("   Please ensure dataset is properly split")
            return False
        
        # Data generator for test data
        test_datagen = ImageDataGenerator(rescale=1./255)
        
        self.test_generator = test_datagen.flow_from_directory(
            test_dir,
            target_size=self.img_size,
            batch_size=self.batch_size,
            class_mode='categorical',
            shuffle=False
        )
        
        # Get class names from generator
        self.class_names = list(self.test_generator.class_indices.keys())
        
        print(f"\n📈 Test Data Statistics:")
        print(f"   Test samples: {self.test_generator.samples}")
        print(f"   Number of classes: {len(self.class_names)}")
        print(f"   Batch size: {self.batch_size}")
        
        return True
    
    def evaluate(self):
        """
        Run evaluation on test data
        
        Returns:
            dict: Evaluation results
        """
        print("\n" + "="*70)
        print("🔍 Running Evaluation")
        print("="*70)
        
        # Get predictions
        print("\n📊 Generating predictions...")
        predictions = self.model.predict(self.test_generator, verbose=1)
        
        # Convert predictions to class labels
        self.pred_labels = np.argmax(predictions, axis=1)
        self.true_labels = self.test_generator.classes
        
        # Calculate metrics
        self.results['accuracy'] = accuracy_score(self.true_labels, self.pred_labels)
        self.results['precision'] = precision_score(self.true_labels, self.pred_labels, average='weighted')
        self.results['recall'] = recall_score(self.true_labels, self.pred_labels, average='weighted')
        self.results['f1_score'] = f1_score(self.true_labels, self.pred_labels, average='weighted')
        
        # Generate classification report
        self.results['class_report'] = classification_report(
            self.true_labels, 
            self.pred_labels,
            target_names=[self.DISPLAY_NAMES.get(name, name) for name in self.class_names],
            output_dict=True
        )
        
        # Generate confusion matrix
        self.results['confusion_matrix'] = confusion_matrix(self.true_labels, self.pred_labels)
        
        # Calculate per-class accuracy
        for i, class_name in enumerate(self.class_names):
            class_mask = (self.true_labels == i)
            if np.sum(class_mask) > 0:
                class_accuracy = np.sum(self.pred_labels[class_mask] == i) / np.sum(class_mask)
                self.results['per_class_accuracy'][class_name] = class_accuracy
        
        # Find misclassified samples
        misclassified_indices = np.where(self.true_labels != self.pred_labels)[0]
        for idx in misclassified_indices[:50]:  # Limit to first 50
            self.results['misclassified_samples'].append({
                'index': idx,
                'true_class': self.class_names[self.true_labels[idx]],
                'true_display': self.DISPLAY_NAMES.get(self.class_names[self.true_labels[idx]], self.class_names[self.true_labels[idx]]),
                'pred_class': self.class_names[self.pred_labels[idx]],
                'pred_display': self.DISPLAY_NAMES.get(self.class_names[self.pred_labels[idx]], self.class_names[self.pred_labels[idx]])
            })
        
        # Print results
        self.print_results()
        
        return self.results
    
    def print_results(self):
        """
        Print evaluation results
        """
        print("\n" + "="*70)
        print("📊 Evaluation Results")
        print("="*70)
        
        print(f"\n📈 Overall Metrics:")
        print(f"   Accuracy:  {self.results['accuracy']:.4f} ({self.results['accuracy']*100:.2f}%)")
        print(f"   Precision: {self.results['precision']:.4f}")
        print(f"   Recall:    {self.results['recall']:.4f}")
        print(f"   F1 Score:  {self.results['f1_score']:.4f}")
        
        print(f"\n📋 Per-Class Accuracy:")
        # Sort by accuracy (lowest first to identify problem classes)
        sorted_classes = sorted(self.results['per_class_accuracy'].items(), key=lambda x: x[1])
        
        print(f"\n   {'Class':<40} {'Accuracy':<10}")
        print(f"   {'-'*40} {'-'*10}")
        
        for class_name, accuracy in sorted_classes:
            display_name = self.DISPLAY_NAMES.get(class_name, class_name)
            status = "⚠️" if accuracy < 0.7 else "✅" if accuracy > 0.9 else "📋"
            print(f"   {status} {display_name:<38} {accuracy:.4f}")
        
        # Print worst performing classes
        worst_classes = sorted_classes[:5]
        if worst_classes:
            print(f"\n⚠️ Worst Performing Classes (need improvement):")
            for class_name, accuracy in worst_classes:
                display_name = self.DISPLAY_NAMES.get(class_name, class_name)
                print(f"   • {display_name}: {accuracy:.4f} ({accuracy*100:.1f}%)")
        
        # Print best performing classes
        best_classes = sorted_classes[-5:][::-1]
        if best_classes:
            print(f"\n✅ Best Performing Classes:")
            for class_name, accuracy in best_classes:
                display_name = self.DISPLAY_NAMES.get(class_name, class_name)
                print(f"   • {display_name}: {accuracy:.4f} ({accuracy*100:.1f}%)")
        
        # Print misclassification summary
        total_misclassified = len(self.results['misclassified_samples'])
        total_samples = len(self.true_labels)
        print(f"\n📊 Misclassification Summary:")
        print(f"   Total Misclassified: {total_misclassified}/{total_samples} ({total_misclassified/total_samples*100:.2f}%)")
        
        if self.results['misclassified_samples']:
            print(f"\n   Sample Misclassifications (first 10):")
            for i, sample in enumerate(self.results['misclassified_samples'][:10]):
                print(f"   {i+1}. True: {sample['true_display']} → Pred: {sample['pred_display']}")
    
    def plot_confusion_matrix(self, save_path='models/confusion_matrix.png', normalize=True, figsize=(20, 18)):
        """
        Plot and save confusion matrix
        
        Args:
            save_path: Path to save the plot
            normalize: Whether to normalize the confusion matrix
            figsize: Figure size
        """
        print("\n" + "="*70)
        print("📊 Generating Confusion Matrix")
        print("="*70)
        
        # Get display names for classes
        display_names = [self.DISPLAY_NAMES.get(name, name) for name in self.class_names]
        
        # Compute confusion matrix
        cm = self.results['confusion_matrix']
        
        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            title = 'Normalized Confusion Matrix'
            fmt = '.2f'
        else:
            title = 'Confusion Matrix'
            fmt = 'd'
        
        # Create plot
        plt.figure(figsize=figsize)
        
        # Use seaborn for better visualization
        sns.heatmap(cm, annot=True, fmt=fmt, cmap='Blues',
                    xticklabels=display_names, yticklabels=display_names,
                    annot_kws={'size': 8})
        
        plt.title(title, fontsize=16)
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.xticks(rotation=90, fontsize=8)
        plt.yticks(rotation=0, fontsize=8)
        
        plt.tight_layout()
        
        # Save plot
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Confusion matrix saved to {save_path}")
        
        plt.close()
    
    def plot_per_class_accuracy(self, save_path='models/per_class_accuracy.png', figsize=(14, 10)):
        """
        Plot per-class accuracy bar chart
        
        Args:
            save_path: Path to save the plot
            figsize: Figure size
        """
        print("\n" + "="*70)
        print("📊 Generating Per-Class Accuracy Chart")
        print("="*70)
        
        # Prepare data
        classes = [self.DISPLAY_NAMES.get(name, name) for name in self.class_names]
        accuracies = [self.results['per_class_accuracy'][name] for name in self.class_names]
        
        # Sort by accuracy
        sorted_indices = np.argsort(accuracies)
        classes_sorted = [classes[i] for i in sorted_indices]
        accuracies_sorted = [accuracies[i] for i in sorted_indices]
        
        # Create plot
        plt.figure(figsize=figsize)
        
        # Color based on accuracy
        colors = ['#EF4444' if acc < 0.7 else '#F59E0B' if acc < 0.85 else '#10B981' for acc in accuracies_sorted]
        
        bars = plt.barh(classes_sorted, accuracies_sorted, color=colors)
        
        # Add value labels
        for bar, acc in zip(bars, accuracies_sorted):
            width = bar.get_width()
            plt.text(width + 0.01, bar.get_y() + bar.get_height()/2, 
                    f'{acc:.3f} ({acc*100:.1f}%)', 
                    ha='left', va='center', fontsize=9)
        
        # Add threshold lines
        plt.axvline(x=0.7, color='#EF4444', linestyle='--', alpha=0.5, label='Warning Threshold (70%)')
        plt.axvline(x=0.85, color='#F59E0B', linestyle='--', alpha=0.5, label='Good Threshold (85%)')
        
        plt.xlabel('Accuracy', fontsize=12)
        plt.ylabel('Disease Class', fontsize=12)
        plt.title('Per-Class Accuracy', fontsize=16)
        plt.xlim(0, 1.05)
        plt.legend(loc='lower right')
        plt.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        # Save plot
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"✅ Per-class accuracy chart saved to {save_path}")
        
        plt.close()
    
    def save_results(self, save_path='models/evaluation_results.json'):
        """
        Save evaluation results to JSON file
        
        Args:
            save_path: Path to save results
        """
        print("\n" + "="*70)
        print("💾 Saving Evaluation Results")
        print("="*70)
        
        # Prepare serializable results
        serializable_results = {
            'timestamp': datetime.now().isoformat(),
            'model_path': str(self.model_path),
            'test_samples': self.test_generator.samples,
            'num_classes': len(self.class_names),
            'accuracy': float(self.results['accuracy']),
            'precision': float(self.results['precision']),
            'recall': float(self.results['recall']),
            'f1_score': float(self.results['f1_score']),
            'per_class_accuracy': {
                self.DISPLAY_NAMES.get(k, k): float(v) 
                for k, v in self.results['per_class_accuracy'].items()
            },
            'misclassified_count': len(self.results['misclassified_samples']),
            'misclassified_samples': self.results['misclassified_samples'][:20]  # Limit to 20
        }
        
        # Add classification report (convert numpy types to Python types)
        class_report = {}
        for class_name, metrics in self.results['class_report'].items():
            if isinstance(metrics, dict):
                class_report[class_name] = {
                    k: float(v) if isinstance(v, (np.float32, np.float64)) else v
                    for k, v in metrics.items()
                }
            else:
                class_report[class_name] = float(metrics) if isinstance(metrics, (np.float32, np.float64)) else metrics
        
        serializable_results['classification_report'] = class_report
        
        # Save to file
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"✅ Evaluation results saved to {save_path}")
    
    def generate_report(self, output_dir='models'):
        """
        Generate comprehensive evaluation report
        
        Args:
            output_dir: Directory to save report files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Plot confusion matrix
        self.plot_confusion_matrix(save_path=output_dir / 'confusion_matrix.png')
        
        # Plot per-class accuracy
        self.plot_per_class_accuracy(save_path=output_dir / 'per_class_accuracy.png')
        
        # Save results as JSON
        self.save_results(save_path=output_dir / 'evaluation_results.json')
        
        # Generate HTML report
        self.generate_html_report(output_dir / 'evaluation_report.html')
        
        print(f"\n✅ All evaluation files saved to {output_dir}/")
    
    def generate_html_report(self, output_path='models/evaluation_report.html'):
        """
        Generate HTML evaluation report
        
        Args:
            output_path: Path to save HTML report
        """
        print("\n" + "="*70)
        print("📄 Generating HTML Report")
        print("="*70)
        
        # Get top 5 best and worst performing classes
        sorted_classes = sorted(self.results['per_class_accuracy'].items(), key=lambda x: x[1])
        worst_classes = sorted_classes[:5]
        best_classes = sorted_classes[-5:][::-1]
        
        # Calculate additional stats
        total_misclassified = len(self.results['misclassified_samples'])
        total_samples = len(self.true_labels)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FarmIntel AI - Model Evaluation Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: #F3F4F6;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #4F46E5;
        }}
        
        .metric-label {{
            color: #6B7280;
            margin-top: 10px;
        }}
        
        .section {{
            margin-bottom: 30px;
        }}
        
        .section-title {{
            font-size: 1.5em;
            color: #1F2937;
            border-bottom: 3px solid #4F46E5;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .class-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .class-item {{
            background: #F9FAFB;
            border-radius: 10px;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .class-name {{
            font-weight: 500;
        }}
        
        .class-accuracy {{
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        
        .accuracy-high {{
            background: #D1FAE5;
            color: #065F46;
        }}
        
        .accuracy-medium {{
            background: #FEF3C7;
            color: #92400E;
        }}
        
        .accuracy-low {{
            background: #FEE2E2;
            color: #991B1B;
        }}
        
        .images-row {{
            display: flex;
            justify-content: center;
            gap: 20px;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        
        .image-card {{
            text-align: center;
            max-width: 300px;
        }}
        
        .image-card img {{
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .footer {{
            background: #1F2937;
            color: #9CA3AF;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .metrics-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌾 FarmIntel AI</h1>
            <p>Model Evaluation Report</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <!-- Metrics Grid -->
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{self.results['accuracy']*100:.1f}%</div>
                    <div class="metric-label">Overall Accuracy</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{self.results['precision']:.3f}</div>
                    <div class="metric-label">Precision (Weighted)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{self.results['recall']:.3f}</div>
                    <div class="metric-label">Recall (Weighted)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{self.results['f1_score']:.3f}</div>
                    <div class="metric-label">F1 Score (Weighted)</div>
                </div>
            </div>
            
            <!-- Best Performing Classes -->
            <div class="section">
                <h2 class="section-title">🏆 Best Performing Classes</h2>
                <div class="class-list">
        """
        
        for class_name, accuracy in best_classes:
            display_name = self.DISPLAY_NAMES.get(class_name, class_name)
            html_content += f"""
                    <div class="class-item">
                        <span class="class-name">✅ {display_name}</span>
                        <span class="class-accuracy accuracy-high">{accuracy*100:.1f}%</span>
                    </div>
            """
        
        html_content += """
                </div>
            </div>
            
            <!-- Worst Performing Classes -->
            <div class="section">
                <h2 class="section-title">⚠️ Classes Needing Improvement</h2>
                <div class="class-list">
        """
        
        for class_name, accuracy in worst_classes:
            display_name = self.DISPLAY_NAMES.get(class_name, class_name)
            accuracy_class = 'accuracy-low' if accuracy < 0.7 else 'accuracy-medium'
            html_content += f"""
                    <div class="class-item">
                        <span class="class-name">⚠️ {display_name}</span>
                        <span class="class-accuracy {accuracy_class}">{accuracy*100:.1f}%</span>
                    </div>
            """
        
        html_content += f"""
                </div>
            </div>
            
            <!-- Misclassification Summary -->
            <div class="section">
                <h2 class="section-title">📊 Misclassification Summary</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_misclassified}</div>
                        <div class="metric-label">Misclassified Images</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_misclassified/total_samples*100:.1f}%</div>
                        <div class="metric-label">Error Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_samples}</div>
                        <div class="metric-label">Total Test Images</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>FarmIntel AI - Empowering Farmers with AI Technology</p>
            <p>Model trained on PlantVillage Dataset • 29 Disease Classes • 9 Crops</p>
        </div>
    </div>
</body>
</html>
        """
        
        # Save HTML report
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        print(f"✅ HTML report saved to {output_path}")
    
    def run_full_evaluation(self):
        """
        Run the complete evaluation pipeline
        """
        print("\n" + "="*70)
        print("🌾 FarmIntel AI - Model Evaluation Pipeline")
        print("="*70)
        print(f"\n📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load model
        if not self.load_model():
            return False
        
        # Load test data
        if not self.load_test_data():
            return False
        
        # Run evaluation
        self.evaluate()
        
        # Generate visualizations and report
        self.generate_report()
        
        print(f"\n📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Evaluate plant disease detection model')
    parser.add_argument('--model', '-m', default='models/plant_disease_model.h5',
                       help='Path to trained model (default: models/plant_disease_model.h5)')
    parser.add_argument('--data', '-d', default='dataset',
                       help='Dataset directory (default: dataset)')
    parser.add_argument('--batch-size', type=int, default=32,
                       help='Batch size for evaluation (default: 32)')
    parser.add_argument('--img-size', type=int, default=224,
                       help='Image size for evaluation (default: 224)')
    parser.add_argument('--output', '-o', default='models',
                       help='Output directory for results (default: models)')
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = ModelEvaluator(
        model_path=args.model,
        data_dir=args.data,
        batch_size=args.batch_size,
        img_size=args.img_size
    )
    
    # Run evaluation
    success = evaluator.run_full_evaluation()
    
    if not success:
        print("\n❌ Evaluation failed. Please check your model and dataset.")
        sys.exit(1)
    
    print("\n🎉 Evaluation complete!")


if __name__ == '__main__':
    main()
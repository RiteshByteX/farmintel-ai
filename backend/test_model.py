"""
Test script to verify model loading and prediction
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.ml_service import model_service

def test_model():
    """Test the model loading and prediction"""
    
    print("\n" + "="*60)
    print("🧪 TESTING PLANT DISEASE MODEL")
    print("="*60)
    
    # Load model
    print("\n📦 Loading model...")
    success = model_service.load_model()
    
    if not success:
        print("❌ Failed to load model!")
        return
    
    # Get model info
    info = model_service.get_model_info()
    print(f"\n✅ Model loaded successfully!")
    print(f"   Classes: {info['num_classes']}")
    print(f"   Input shape: {info['input_shape']}")
    
    # Test with a sample image (if available)
    sample_image = "../frontend/assets/images/samples/tomato_healthy.jpg"
    
    if os.path.exists(sample_image):
        print(f"\n🔍 Testing prediction on: {sample_image}")
        result = model_service.predict(sample_image)
        
        if result and result.get('success'):
            print(f"\n📊 Prediction Results:")
            print(f"   Disease: {result['disease_name']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"\n   Top 3 predictions:")
            for i, pred in enumerate(result['top_3_predictions'], 1):
                print(f"   {i}. {pred['disease']} ({pred['confidence']*100:.2f}%)")
        else:
            print(f"❌ Prediction failed: {result.get('error') if result else 'Unknown error'}")
    else:
        print(f"\n⚠️ Sample image not found: {sample_image}")
        print("   Skipping prediction test")
    
    print("\n" + "="*60)
    print("✅ Model test completed!")
    print("="*60)

if __name__ == "__main__":
    test_model()
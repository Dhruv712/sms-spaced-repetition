#!/usr/bin/env python3
"""
Simple test of SM-2 algorithm
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def test_sm2_simple():
    """Test SM-2 algorithm with simple scenarios"""
    
    print("🧪 Testing SM-2 algorithm...")
    
    try:
        from services.scheduler import compute_sm2_next_review
        
        # Test 1: First review, correct answer
        print("\n📝 Test 1: First review, correct answer")
        result = compute_sm2_next_review(
            repetition_count=0,
            ease_factor=2.5,
            interval_days=0,
            was_correct=True,
            confidence_score=0.8
        )
        print(f"   Result: rep={result[0]}, ease={result[1]:.2f}, interval={result[2]} days")
        
        # Test 2: Second review, correct answer
        print("\n📝 Test 2: Second review, correct answer")
        result = compute_sm2_next_review(
            repetition_count=1,
            ease_factor=2.5,
            interval_days=1,
            was_correct=True,
            confidence_score=0.9
        )
        print(f"   Result: rep={result[0]}, ease={result[1]:.2f}, interval={result[2]} days")
        
        # Test 3: Incorrect answer
        print("\n📝 Test 3: Incorrect answer")
        result = compute_sm2_next_review(
            repetition_count=2,
            ease_factor=2.5,
            interval_days=6,
            was_correct=False,
            confidence_score=0.3
        )
        print(f"   Result: rep={result[0]}, ease={result[1]:.2f}, interval={result[2]} days")
        
        print("\n✅ SM-2 algorithm tests completed!")
        
    except Exception as e:
        print(f"❌ Error testing SM-2: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sm2_simple()

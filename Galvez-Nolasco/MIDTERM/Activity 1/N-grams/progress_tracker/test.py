def test_imports():
    try:
        from .tracker import ProgressTracker, TypingTestResult, save_typing_result
        from .dashboard import ProgressDashboard, show_quick_progress
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    try:
        from .tracker import ProgressTracker
        
        # Create tracker
        tracker = ProgressTracker("test_progress.json")
        print("✅ Tracker created successfully")
        
        # Test data loading
        data = tracker._load_data()
        print("✅ Data loading successful")
        
        # Clean up test file
        import os
        if os.path.exists("test_progress.json"):
            os.remove("test_progress.json")
        
        return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Progress Tracker Package")
    print("=" * 40)
    
    test1 = test_imports()
    test2 = test_basic_functionality()
    
    if test1 and test2:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed.")

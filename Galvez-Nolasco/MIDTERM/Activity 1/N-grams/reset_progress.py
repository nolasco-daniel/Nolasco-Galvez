#!/usr/bin/env python3
"""
Quick script to reset typing progress data
"""

def reset_progress():
    """Reset the typing progress data"""
    try:
        from progress_tracker.tracker import ProgressTracker
        
        print("🗑️  RESET TYPING PROGRESS DATA")
        print("=" * 40)
        
        confirm = input("Are you sure you want to reset ALL progress data? (type 'YES' to confirm): ").strip()
        
        if confirm == "YES":
            tracker = ProgressTracker()
            tracker.reset_progress()
            print("✅ Progress data has been reset successfully!")
        else:
            print("❌ Reset cancelled.")
            
    except Exception as e:
        print(f"❌ Error resetting progress: {e}")

if __name__ == "__main__":
    reset_progress()

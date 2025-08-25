import os
import datetime
from typing import Dict, List
from .tracker import ProgressTracker, get_typing_progress

class ProgressDashboard:
    def __init__(self):
        self.tracker = ProgressTracker()
    
    def display_main_dashboard(self):
        os.system('cls' if os.name == 'nt' else 'clear')    
        print("=" * 80)
        print("                    📊 TYPING PROGRESS DASHBOARD 📊")
        print("=" * 80)

        try:
            summary = self.tracker.get_progress_summary()
            difficulty_stats = self.tracker.get_difficulty_stats()
            
            # Overall Statistics
            print("\n🎯 OVERALL STATISTICS")
            print("-" * 50)
            print(f"Total Tests Taken:     {summary['total_tests']:>8}")
            print(f"Best WPM:              {summary['best_wpm']:>8.1f}")
            print(f"Best Accuracy:         {summary['best_accuracy']:>8.1f}%")
            print(f"Average WPM:           {summary['average_wpm']:>8.1f}")
            print(f"Average Accuracy:      {summary['average_accuracy']:>8.1f}%")
            print(f"Total Characters:      {summary['total_characters']:>8,}")
            print(f"Total Time:            {summary['total_time']/60:>8.1f} minutes")
            
            # Recent Performance
            print(f"\n📈 RECENT PERFORMANCE (Last 10 Tests)")
            print("-" * 50)
            print(f"Recent Average WPM:    {summary['recent_average_wpm']:>8.1f}")
            print(f"Recent Average Accuracy: {summary['recent_average_accuracy']:>8.1f}%")
            
            # Difficulty Breakdown
            print(f"\n🎮 DIFFICULTY BREAKDOWN")
            print("-" * 50)
            for diff in ['easy', 'medium', 'hard']:
                stats = difficulty_stats.get(diff, {})
                if stats['count'] > 0:
                    print(f"{diff.capitalize():>8}: {stats['count']:>3} tests | "
                          f"Avg WPM: {stats['average_wpm']:>5.1f} | "
                          f"Best: {stats['best_wpm']:>5.1f} | "
                          f"Accuracy: {stats['average_accuracy']:>5.1f}%")
                else:
                    print(f"{diff.capitalize():>8}: No tests taken yet")
            
            # Recent Test History
            if summary['test_history']:
                print(f"\n📝 RECENT TEST HISTORY (Last 10 Tests)")
                print("-" * 80)
                print(f"{'Date':<12} {'WPM':<6} {'Accuracy':<10} {'Chars':<8} {'Time':<8} {'Difficulty':<10}")
                print("-" * 80)
                
                for test in summary['test_history'][-10:]:
                    date = test['date_taken']  # Already in YYYY-MM-DD format
                    wpm = f"{test['wpm']:.1f}"
                    accuracy = f"{test['accuracy']:.1f}%"
                    chars = f"{test['characters_typed']}/{test.get('total_characters', '?')}"
                    time = f"{test['time_taken']:.1f}s"
                    diff = test['difficulty'].capitalize()
                    
                    print(f"{date:<12} {wpm:<6} {accuracy:<10} {chars:<8} {time:<8} {diff:<10}")
            
            # File Information
            file_info = self.tracker.get_file_info()
            print(f"\n💾 DATA FILE INFORMATION")
            print("-" * 50)
            print(f"File Location:         {file_info.get('file_path', 'Unknown')}")
            print(f"File Size:             {file_info.get('file_size', 0):>8} bytes")
            print(f"Last Modified:         {file_info.get('last_modified', 'Unknown')}")
            
        except Exception as e:
            print(f"Error loading progress data: {e}")
            print("Progress tracking may not be working properly.")
    
    def display_detailed_history(self, num_tests: int = 50):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print(f"                    📋 DETAILED TEST HISTORY ({num_tests} Tests)")
        print("=" * 80)
        
        try:
            summary = self.tracker.get_progress_summary()
            
            if not summary['test_history']:
                print("\nNo test history available yet.")
                return
            
            print(f"\n📊 SUMMARY")
            print("-" * 30)
            print(f"Total Tests: {summary['total_tests']}")
            print(f"Best WPM: {summary['best_wpm']:.1f}")
            print(f"Best Accuracy: {summary['best_accuracy']:.1f}%")
            
            print(f"\n📝 TEST DETAILS")
            print("-" * 100)
            print(f"{'Date':<12} {'WPM':<6} {'Accuracy':<10} {'Chars':<8} {'Time':<8} {'Difficulty':<10} {'N-Gram':<8}")
            print("-" * 100)
            
            # Show most recent tests first
            for test in reversed(summary['test_history'][-num_tests:]):
                date = test['date_taken']  # Already in YYYY-MM-DD format
                wpm = f"{test['wpm']:.1f}"
                accuracy = f"{test['accuracy']:.1f}%"
                chars = f"{test['characters_typed']}/{test.get('total_characters', '?')}"
                time = f"{test['time_taken']:.1f}s"
                diff = test['difficulty'].capitalize()
                ngram = f"{test['n_gram_order']}"
                
                print(f"{date:<12} {wpm:<6} {accuracy:<10} {chars:<8} {time:<8} {diff:<10} {ngram:<8}")
                
        except Exception as e:
            print(f"Error loading detailed history: {e}")
    
    def display_difficulty_analysis(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 80)
        print("                    🎯 DIFFICULTY ANALYSIS")
        print("=" * 80)
        
        try:
            difficulty_stats = self.tracker.get_difficulty_stats()
            
            for diff in ['easy', 'medium', 'hard']:
                stats = difficulty_stats.get(diff, {})
                
                print(f"\n🎮 {diff.upper()} DIFFICULTY")
                print("-" * 40)
                
                if stats['count'] > 0:
                    print(f"Tests Taken:           {stats['count']:>8}")
                    print(f"Average WPM:           {stats['average_wpm']:>8.1f}")
                    print(f"Best WPM:              {stats['best_wpm']:>8.1f}")
                    print(f"Average Accuracy:      {stats['average_accuracy']:>8.1f}%")
                    print(f"Best Accuracy:         {stats['best_accuracy']:>8.1f}%")
                    
                    # Calculate improvement potential
                    if stats['count'] >= 5:
                        print(f"Consistency:           {'Good' if stats['average_accuracy'] > 90 else 'Needs Improvement'}")
                else:
                    print("No tests taken yet in this difficulty level.")
                    print("Try taking some tests to see your performance!")
            
            # Overall recommendations
            print(f"\n💡 RECOMMENDATIONS")
            print("-" * 40)
            
            total_tests = sum(stats['count'] for stats in difficulty_stats.values())
            if total_tests < 10:
                print("• Take more tests to get better insights into your performance")
            else:
                best_diff = max(difficulty_stats.items(), key=lambda x: x[1]['average_wpm'] if x[1]['count'] > 0 else 0)
                worst_diff = min(difficulty_stats.items(), key=lambda x: x[1]['average_accuracy'] if x[1]['count'] > 0 else 100)
                
                if best_diff[1]['count'] > 0:
                    print(f"• Your strongest area: {best_diff[0].capitalize()} difficulty")
                if worst_diff[1]['count'] > 0:
                    print(f"• Focus on improving: {worst_diff[0].capitalize()} difficulty")
                
                print("• Practice regularly to maintain and improve your skills")
                
        except Exception as e:
            print(f"Error loading difficulty analysis: {e}")
    
    def export_data_menu(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 60)
        print("                    📤 EXPORT PROGRESS DATA")
        print("=" * 60)
        
        print("\nChoose export format:")
        print("1. CSV Export (for Excel/Google Sheets)")
        print("2. JSON Export (for data analysis)")
        print("3. Back to Dashboard")
        
        choice = input("\nYour choice > ").strip()
        
        if choice == "1":
            filename = input("Enter CSV filename (default: typing_progress.csv): ").strip()
            if not filename:
                filename = "typing_progress.csv"
            
            if self.tracker.export_to_csv(filename):
                print(f"\n✅ Data exported successfully to {filename}")
            else:
                print("\n❌ Export failed. Check file permissions.")
            
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            filename = input("Enter JSON filename (default: typing_progress_export.json): ").strip()
            if not filename:
                filename = "typing_progress_export.json"
            
            try:
                import json
                data = self.tracker._load_data()
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n✅ Data exported successfully to {filename}")
            except Exception as e:
                print(f"\n❌ Export failed: {e}")
            
            input("\nPress Enter to continue...")
    
    def reset_progress_data(self):
        """Reset all progress data"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("=" * 60)
        print("                    🗑️  RESET PROGRESS DATA")
        print("=" * 60)
        
        print("\n⚠️  WARNING: This will permanently delete ALL your progress data!")
        print("This action cannot be undone.")
        
        confirm = input("\nType 'YES' to confirm deletion: ").strip()
        
        if confirm == "YES":
            try:
                self.tracker.reset_progress()
                print("\n✅ Progress data has been reset successfully!")
                print("All test history, statistics, and scores have been cleared.")
            except Exception as e:
                print(f"\n❌ Error resetting progress: {e}")
        else:
            print("\n❌ Reset cancelled. Your data is safe.")
        
        input("\nPress Enter to return to dashboard...")
    
    def run_dashboard(self):
        while True:
            self.display_main_dashboard()
            
            print(f"\n🔧 DASHBOARD OPTIONS")
            print("-" * 30)
            print("1. View Detailed History")
            print("2. Difficulty Analysis")
            print("3. Export Data")
            print("4. Refresh Dashboard")
            print("5. Reset Progress Data")
            print("6. Back to Main Menu")
            
            choice = input("\nYour choice > ").strip()
            
            if choice == "1":
                num_tests = input("How many tests to show? (default: 50): ").strip()
                try:
                    num_tests = int(num_tests) if num_tests else 50
                except ValueError:
                    num_tests = 50
                
                self.display_detailed_history(num_tests)
                input("\nPress Enter to return to dashboard...")
                
            elif choice == "2":
                self.display_difficulty_analysis()
                input("\nPress Enter to return to dashboard...")
                
            elif choice == "3":
                self.export_data_menu()
                
            elif choice == "4":
                continue  # Refresh dashboard
                
            elif choice == "5":
                self.reset_progress_data()
                
            elif choice == "6":
                break
                
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")


def show_quick_progress():
    try:
        summary = get_typing_progress()
        
        print("\n📊 QUICK PROGRESS SUMMARY")
        print("-" * 40)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Best WPM: {summary['best_wpm']:.1f}")
        print(f"Best Accuracy: {summary['best_accuracy']:.1f}%")
        print(f"Recent Avg WPM: {summary['recent_average_wpm']:.1f}")
        
    except Exception as e:
        print(f"Could not load progress: {e}")


if __name__ == "__main__":
    dashboard = ProgressDashboard()
    dashboard.run_dashboard()

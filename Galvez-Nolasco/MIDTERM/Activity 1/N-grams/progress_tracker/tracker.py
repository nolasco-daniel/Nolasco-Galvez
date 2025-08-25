import json
import os
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class TypingTestResult:
    wpm: float
    accuracy: float
    characters_typed: int  # Correctly typed characters (matches game display)
    total_characters: int  # Total available characters in the test
    time_taken: float
    date_taken: str
    difficulty: str
    n_gram_order: int
    test_duration: int  


class ProgressTracker:    
    def __init__(self, data_file: str = "typing_progress.json"):
        self.data_file = data_file
        self._ensure_data_file_exists()
    
    def _ensure_data_file_exists(self):
        if not os.path.exists(self.data_file):
            # Create initial data structure
            initial_data = {
                "version": "1.0",
                "created_date": datetime.datetime.now().strftime('%Y-%m-%d'),
                "total_tests": 0,
                "best_wpm": 0.0,
                "best_accuracy": 0.0,
                "average_wpm": 0.0,
                "average_accuracy": 0.0,
                "total_characters": 0,
                "total_time": 0.0,
                "test_history": []
            }
            self._save_data(initial_data)
    
    def _load_data(self) -> Dict:
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create fresh data if corrupted
            self._ensure_data_file_exists()
            return self._load_data()
    
    def _save_data(self, data: Dict):
        try:
            temp_file = f"{self.data_file}.tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            os.replace(temp_file, self.data_file)
            
        except Exception as e:
            print(f"Error saving progress data: {e}")
    
    def save_test_result(self, result: TypingTestResult):
        data = self._load_data()
        
        # Round values to 1 decimal place
        result.wpm = round(result.wpm, 1)
        result.accuracy = round(result.accuracy, 1)
        
        # Add new result to history
        data["test_history"].append(asdict(result))
        
        # Update statistics
        data["total_tests"] += 1
        data["total_characters"] += result.characters_typed
        data["total_time"] += result.time_taken
        
        # Update best scores
        if result.wpm > data["best_wpm"]:
            data["best_wpm"] = result.wpm
        
        if result.accuracy > data["best_accuracy"]:
            data["best_accuracy"] = result.accuracy
        
        # Calculate averages and round to 1 decimal place
        all_wpms = [test["wpm"] for test in data["test_history"]]
        all_accuracies = [test["accuracy"] for test in data["test_history"]]
        
        data["average_wpm"] = round(sum(all_wpms) / len(all_wpms), 1)
        data["average_accuracy"] = round(sum(all_accuracies) / len(all_accuracies), 1)
        
        if len(data["test_history"]) > 1000:
            data["test_history"] = data["test_history"][-1000:]
        
        data["last_modified"] = datetime.datetime.now().strftime('%Y-%m-%d')
        
        self._save_data(data)
    
    def get_progress_summary(self) -> Dict:
        data = self._load_data()
        
        recent_tests = data["test_history"][-10:] if data["test_history"] else []
        recent_wpms = [test["wpm"] for test in recent_tests]
        recent_accuracies = [test["accuracy"] for test in recent_tests]
        
        summary = {
            "total_tests": data["total_tests"],
            "best_wpm": data["best_wpm"],
            "best_accuracy": data["best_accuracy"],
            "average_wpm": data["average_wpm"],
            "average_accuracy": data["average_accuracy"],
            "total_characters": data["total_characters"],
            "total_time": data["total_time"],
            "recent_average_wpm": round(sum(recent_wpms) / len(recent_wpms), 1) if recent_wpms else 0,
            "recent_average_accuracy": round(sum(recent_accuracies) / len(recent_accuracies), 1) if recent_accuracies else 0,
            "test_history": data["test_history"][-50:]  # Last 50 tests for detailed view
        }
        
        return summary
    
    def get_difficulty_stats(self) -> Dict:
        data = self._load_data()
        
        difficulty_stats = {"easy": [], "medium": [], "hard": []}
        
        for test in data["test_history"]:
            diff = test["difficulty"].lower()
            if diff in difficulty_stats:
                difficulty_stats[diff].append(test)
        
        result = {}
        for diff, tests in difficulty_stats.items():
            if tests:
                wpms = [test["wpm"] for test in tests]
                accuracies = [test["accuracy"] for test in tests]
                result[diff] = {
                    "count": len(tests),
                    "average_wpm": round(sum(wpms) / len(wpms), 1),
                    "average_accuracy": round(sum(accuracies) / len(accuracies), 1),
                    "best_wpm": max(wpms),
                    "best_accuracy": max(accuracies)
                }
            else:
                result[diff] = {"count": 0, "average_wpm": 0, "average_accuracy": 0, "best_wpm": 0, "best_accuracy": 0}
        
        return result
    
    def export_to_csv(self, filename: str = "typing_progress.csv"):
        try:
            import csv
            data = self._load_data()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date_taken', 'wpm', 'accuracy', 'characters_typed', 'total_characters', 'time_taken', 'difficulty', 'n_gram_order', 'test_duration']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for test in data["test_history"]:
                    writer.writerow(test)
            
            print(f"Progress data exported to {filename}")
            return True
            
        except ImportError:
            print("CSV export requires the 'csv' module (built-in)")
            return False
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def get_progress_chart_data(self) -> Dict:
        data = self._load_data()
        
        recent_tests = data["test_history"][-30:] if data["test_history"] else []
        
        chart_data = {
            "dates": [test["date_taken"] for test in recent_tests],
            "wpms": [test["wpm"] for test in recent_tests],
            "accuracies": [test["accuracy"] for test in recent_tests],
            "characters": [test["characters_typed"] for test in recent_tests]
        }
        
        return chart_data
    
    def reset_progress(self):
        confirm = input("Are you sure you want to reset ALL progress data? (type 'YES' to confirm): ")
        if confirm == "YES":
            # Create fresh empty data structure
            fresh_data = {
                "version": "1.0",
                "created_date": datetime.datetime.now().strftime('%Y-%m-%d'),
                "total_tests": 0,
                "best_wpm": 0.0,
                "best_accuracy": 0.0,
                "average_wpm": 0.0,
                "average_accuracy": 0.0,
                "total_characters": 0,
                "total_time": 0.0,
                "test_history": []
            }
            self._save_data(fresh_data)
            print("Progress data has been reset.")
        else:
            print("Progress reset cancelled.")
    
    def get_file_info(self) -> Dict:
        try:
            stat = os.stat(self.data_file)
            return {
                "file_size": stat.st_size,
                "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d'),
                "file_path": os.path.abspath(self.data_file)
            }
        except Exception as e:
            return {"error": str(e)}


def save_typing_result(wpm: float, accuracy: float, characters_typed: int, 
                      total_characters: int, time_taken: float, difficulty: str, 
                      n_gram_order: int, test_duration: int):
    tracker = ProgressTracker()
    result = TypingTestResult(
        wpm=wpm,
        accuracy=accuracy,
        characters_typed=characters_typed,
        total_characters=total_characters,
        time_taken=time_taken,
        date_taken=datetime.datetime.now().strftime('%Y-%m-%d'),
        difficulty=difficulty,
        n_gram_order=n_gram_order,
        test_duration=test_duration
    )
    tracker.save_test_result(result)
    return result


def get_typing_progress():
    tracker = ProgressTracker()
    return tracker.get_progress_summary()

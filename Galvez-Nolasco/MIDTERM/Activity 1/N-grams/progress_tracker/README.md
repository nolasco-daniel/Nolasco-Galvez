# 📊 Progress Tracker Package

This package contains all the progress tracking functionality for the N-grams typing application, organized in a clean, modular structure.

## 📁 Package Structure

```
progress_tracker/
├── __init__.py          # Package initialization and exports
├── tracker.py           # Core progress tracking functionality
├── dashboard.py         # Progress dashboard and display
├── test.py             # Package testing
└── README.md           # This file
```

## 🔧 Modules

### `tracker.py`
- **ProgressTracker**: Main class for managing progress data
- **TypingTestResult**: Data class for storing test results
- **save_typing_result()**: Quick function to save results
- **get_typing_progress()**: Quick function to get progress summary

### `dashboard.py`
- **ProgressDashboard**: Interactive dashboard for viewing progress
- **show_quick_progress()**: Quick progress summary display

### `__init__.py`
- Package initialization
- Exports all public functions and classes
- Version information

## 🚀 Usage

### Basic Progress Tracking
```python
from progress_tracker.tracker import save_typing_result

# Save a typing test result
save_typing_result(
    wpm=45.5,
    accuracy=95.2,
    characters_typed=150,
    time_taken=45.0,
    difficulty="medium",
    n_gram_order=3,
    test_duration=60
)
```

### View Progress Dashboard
```python
from progress_tracker.dashboard import ProgressDashboard

dashboard = ProgressDashboard()
dashboard.run_dashboard()
```

### Quick Progress Summary
```python
from progress_tracker.tracker import get_typing_progress

summary = get_typing_progress()
print(f"Best WPM: {summary['best_wpm']:.1f}")
```

## 📊 Data Format

### Simplified Numbers
- **WPM**: Rounded to 1 decimal place (e.g., 45.5 instead of 45.523456)
- **Accuracy**: Rounded to 1 decimal place (e.g., 95.2 instead of 95.23529411764706)

### Date Format
- **Simple Format**: YYYY-MM-DD (e.g., 2025-08-23)
- **No Time**: Only date, no time information

### Single File Storage
- **Main File**: `typing_progress.json`
- **No Backup**: Single file approach for simplicity
- **Automatic Recovery**: Handles corruption gracefully

## 🔄 Integration

The package is automatically integrated with:
- **Main Menu**: Progress dashboard options
- **Typing Game**: Automatic result saving
- **Quick Access**: Fast progress summary

## 🧪 Testing

Run the package tests:
```bash
cd progress_tracker
python -m test
```

## 📈 Features

- ✅ **Automatic Data Collection**: Saves results after every test
- ✅ **Simplified Numbers**: Clean, readable statistics
- ✅ **Simple Dates**: YYYY-MM-DD format
- ✅ **Single File**: No backup complexity
- ✅ **Organized Code**: Clean package structure
- ✅ **Easy Integration**: Simple import statements

## 🎯 Benefits of Organization

1. **Clean Structure**: All progress tracking code in one place
2. **Easy Maintenance**: Modular design for easy updates
3. **Clear Imports**: Simple `from progress_tracker.tracker import ...`
4. **Package Management**: Proper Python package structure
5. **Testing**: Dedicated test module for the package

---

**Note**: This package automatically handles all the complexity of progress tracking while providing a simple, clean interface for the main application.

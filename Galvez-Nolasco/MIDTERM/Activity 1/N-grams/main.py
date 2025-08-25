from ngrams import Ngrams, print_menu, prompt
from typing_test import run_typing_test_with_ngrams


def main():
    print("N-Grams WPM")
    print("Generate text phrases using n-gram language models with difficulty levels!\n")
    
    while True:
        try:
            print_menu("Choose difficulty", [
                "Easy (basic/common words)",
                "Medium (moderately difficult words)",
                "Hard (complex/deep words)",
                "Custom settings",
                "Show difficulty statistics",
                "Verify corpora & generation",
                "Start typing test (30/60/120s)",
                "Corpus management (create/update)",
                "Exit"
            ])
            
            choice = prompt("\nYour choice > ")
        except KeyboardInterrupt:
            print("\n\nGoodbye! Happy learning!")
            return
        except EOFError:
            print("\n\nGoodbye! Happy learning!")
            return
        
        if choice == "1":
            difficulty = "easy"
            n, phrases = 2, 5
        elif choice == "2":
            difficulty = "medium"
            n, phrases = 3, 8
        elif choice == "3":
            difficulty = "hard"
            n, phrases = 4, 10
        elif choice == "4":
            custom_settings = get_custom_settings()
            if custom_settings is None:
                continue
            n, phrases, difficulty = custom_settings
        elif choice == "5":
            show_difficulty_stats()
            continue
        elif choice == "6":
            verify_corpora_and_generation()
            continue
        elif choice == "7":
            start_typing_test()
            continue
        elif choice == "8":
            manage_corpus()
            continue
        elif choice == "9":
            print("Goodbye! Happy learning!")
            return
        else:
            print("Invalid choice, defaulting to Medium")
            difficulty = "medium"
            n, phrases = 3, 8
        
        generate_phrases(n, phrases, difficulty)


def get_custom_settings():
    print("\n=== CUSTOM SETTINGS ===")
    
    try:
        print("\nChoose difficulty level:")
        print("1. Easy (basic/common words)")
        print("2. Medium (moderately difficult words)")
        print("3. Hard (complex/deep words)")
        
        diff_choice = prompt("Difficulty choice (1-3): ").strip()
        if diff_choice == "1":
            difficulty = "easy"
        elif diff_choice == "2":
            difficulty = "medium"
        elif diff_choice == "3":
            difficulty = "hard"
        else:
            print("Invalid difficulty choice, defaulting to Medium")
            difficulty = "medium"
        
        n_input = prompt("Enter n-gram order (2-5): ").strip()
        if not n_input.isdigit():
            print("Please enter a valid number for n-gram order")
            return None
        n = int(n_input)
        if n < 2 or n > 5:
            print("N-gram order must be between 2 and 5")
            return None
            
        phrases_input = prompt("Enter number of phrases (3-15): ").strip()
        if not phrases_input.isdigit():
            print("Please enter a valid number for phrases")
            return None
        phrases = int(phrases_input)
        if phrases < 3 or phrases > 15:
            print("Number of phrases must be between 3 and 15")
            return None
            
        return n, phrases, difficulty
        
    except ValueError:
        print("Please enter valid numbers")
        return None
    except KeyboardInterrupt:
        print("\nSettings cancelled")
        return None


def show_difficulty_stats():
    print("\n DIFFICULTY STATISTICS (per mode)")
    print("Analyzing each corpora section for word complexity...")
    try:
        for diff in ("easy", "medium", "hard"):
            ngrams_obj = Ngrams(corpus_file=["corpora/corpora.pkl"], difficulty=diff)
            stats = ngrams_obj.get_difficulty_stats()
            print(f"\n— {diff.capitalize()} section —")
            print(f"Easy-like:   {stats['easy']['count']} | Sample: {', '.join(stats['easy']['sample_words'])}")
            print(f"Medium-like: {stats['medium']['count']} | Sample: {', '.join(stats['medium']['sample_words'])}")
            print(f"Hard-like:   {stats['hard']['count']} | Sample: {', '.join(stats['hard']['sample_words'])}")
    except Exception as e:
        print(f" Error getting difficulty statistics: {e}")


def verify_corpora_and_generation():
    print("\n Verifying corpora sections and generation integrity...")
    import pickle
    import re

    def normalize(text: str) -> str:
        text = re.sub(r"\s+", " ", text.strip())
        text = re.sub(r"[\-–—_]+", " ", text)
        text = re.sub(r"[^A-Za-z0-9\s]", "", text)
        return text.lower()

    try:
        with open("corpora/corpora.pkl", "rb") as f:
            data = pickle.load(f)
        if not isinstance(data, dict):
            data = {}
        lower_map = {str(k).lower(): k for k in data.keys()}

        def get_list_for(key_aliases):
            for alias in key_aliases:
                if alias in lower_map:
                    val = data[lower_map[alias]]
                    if isinstance(val, (list, tuple)):
                        return [str(x) for x in val]
                    if isinstance(val, str):
                        return [s for s in val.splitlines() if s.strip()]
            return []

        easy_list = get_list_for(["easy", "basic", "simple", "short"])
        med_list = get_list_for(["medium", "moderate"])
        hard_list = get_list_for(["hard", "difficult", "deep", "long"])

        easy_set = {normalize(w) for w in easy_list}
        med_set = {normalize(w) for w in med_list}
        hard_set = {normalize(w) for w in hard_list}

        med_easy_overlap = med_set & easy_set
        hard_easy_overlap = hard_set & easy_set
        hard_med_overlap = hard_set & med_set

        print(f"\n Corpora sizes (unique, normalized):")
        print(f"   • Easy:   {len(easy_set)}")
        print(f"   • Medium: {len(med_set)}")
        print(f"   • Hard:   {len(hard_set)}")

        def show_overlap(name, items):
            if items:
                sample = ", ".join(list(items)[:5])
                print(f"   • Overlap {name}: {len(items)} (e.g., {sample})")
            else:
                print(f"   • Overlap {name}: 0 ✅")

        print("\n Overlaps (by normalized text):")
        show_overlap("Medium ∩ Easy", med_easy_overlap)
        show_overlap("Hard ∩ Easy", hard_easy_overlap)
        show_overlap("Hard ∩ Medium", hard_med_overlap)

        print("\n Generation validation (words must belong to the selected section):")
        for diff, allowed_set in [("easy", easy_set), ("medium", med_set), ("hard", hard_set)]:
            try:
                ngrams_obj = Ngrams(corpus_file=["corpora/corpora.pkl"], n=3, num_phrases=6, difficulty=diff)
                phrases = ngrams_obj.generate_phrases()
                text = " ".join(phrases)
                words = re.findall(r"[A-Za-z]+", text)
                used = {normalize(w) for w in words}
                outside = {w for w in used if w not in allowed_set}
                if outside:
                    sample = ", ".join(list(outside)[:8])
                    print(f"   • {diff.capitalize()}:  {len(outside)} words outside section (e.g., {sample})")
                else:
                    print(f"   • {diff.capitalize()}:  all words within section")
            except Exception as e:
                print(f"   • {diff.capitalize()}: Error during generation: {e}")
    except Exception as e:
        print(f" Verification failed: {e}")


def start_typing_test():
    print("\n⌛ Start Typing Test (Countdown)")
    print("Choose time limit:")
    print("1. 30 seconds")
    print("2. 60 seconds")
    print("3. 120 seconds")
    time_choice = prompt("Time choice (1-3): ").strip()
    if time_choice == "1":
        time_limit = 30
    elif time_choice == "2":
        time_limit = 60
    elif time_choice == "3":
        time_limit = 120
    else:
        print(" Invalid time choice, using 60 seconds")
        time_limit = 60

    print("\nChoose difficulty:")
    print("1. Easy (short words)")
    print("2. Medium (5-7 letters)")
    print("3. Hard (8+ letters)")
    diff_choice = prompt("Difficulty choice (1-3): ").strip()
    if diff_choice == "1":
        difficulty = "easy"
    elif diff_choice == "2":
        difficulty = "medium"
    elif diff_choice == "3":
        difficulty = "hard"
    else:
        print(" Invalid difficulty choice, defaulting to Medium")
        difficulty = "medium"

    try:
        run_typing_test_with_ngrams(difficulty=difficulty, time_limit=time_limit)
    except Exception as e:
        print(f" Error running typing test: {e}")


def show_progress_dashboard():
    """Display the progress dashboard"""
    try:
        from progress_tracker.dashboard import ProgressDashboard
        dashboard = ProgressDashboard()
        dashboard.run_dashboard()
    except ImportError:
        print("Progress dashboard not available. Make sure progress_tracker package exists.")
    except Exception as e:
        print(f"Error loading progress dashboard: {e}")
        print("You can still view basic progress with the quick summary option.")
        
        # Fallback to quick progress summary
        try:
            from progress_tracker.dashboard import show_quick_progress
            show_quick_progress()
        except:
            print("Progress tracking is not working. No data available.")


def show_quick_progress_summary():
    """Show a quick summary of typing progress"""
    try:
        from progress_tracker.dashboard import show_quick_progress
        show_quick_progress()
        input("\nPress Enter to continue...")
    except ImportError:
        print("Progress tracking not available. Make sure progress_tracker package exists.")
    except Exception as e:
        print(f"Error loading progress: {e}")
        input("\nPress Enter to continue...")


def generate_phrases(n, phrases, difficulty):
    print(f"\n Generating {difficulty.capitalize()} difficulty phrases...")
    print(f"   • N-gram order: {n}")
    print(f"   • Number of phrases: {phrases}")
    print(f"   • Difficulty level: {difficulty.capitalize()}")
    
    try:
        import random
        random.seed()
        
        ngrams_obj = Ngrams(corpus_file=["corpora/corpora.pkl"], n=n, num_phrases=phrases, difficulty=difficulty)
        
        print("\n Generating phrases...")
        test_phrases = ngrams_obj.generate_phrases()
        
        if not test_phrases or all(not phrase.strip() for phrase in test_phrases):
            print(" Error: Could not generate valid phrases")
            print("The corpus might be too small for the selected n-gram order.")
            return
        
        print(f"\n Generated {difficulty.capitalize()} phrases:")
        print("=" * 50)
        for i, phrase in enumerate(test_phrases, 1):
            if phrase.strip():
                print(f"{i}. {phrase}")
        
        print("=" * 50)
        print(f" Successfully generated {len([p for p in test_phrases if p.strip()])} phrases")
        
        model_stats = ngrams_obj.get_model_stats()
        print(f"\n Model Statistics:")
        print(f"   • Total tokens in corpus: {model_stats['total_tokens']}")
        print(f"   • Unique words: {model_stats['unique_words']}")
        print(f"   • Vocabulary size: {model_stats['vocabulary_size']}")
        
        ngrams_obj.clear_cache()
        
    except FileNotFoundError:
        print(" Error: corpora/corpora.pkl file not found!")
        print("Please make sure the pickle corpus file exists in the 'corpora' directory.")
    except Exception as e:
        print(f" Error generating phrases: {e}")


def manage_corpus():
    print("\n=== CORPUS MANAGEMENT (READ & WRITE) ===")
    print("1. Create corpus from text files (wb)")
    print("2. View corpus information (rb)")
    print("3. Update corpus section (rb + wb)")
    print("4. Add text to corpus section (rb + wb)")
    print("5. Back to main menu")
    
    choice = prompt("\nYour choice > ")
    
    if choice == "1":
        create_corpus_from_files()
    elif choice == "2":
        view_corpus_info()
    elif choice == "3":
        update_corpus_section()
    elif choice == "4":
        add_text_to_corpus()
    elif choice == "5":
        return
    else:
        print("Invalid choice")


def create_corpus_from_files():
    print("\n📁 Creating corpus from text files (using wb)...")
    ngrams_obj = Ngrams()
    success = ngrams_obj.create_corpus_from_text_files()
    if success:
        print("✅ Corpus created successfully using wb (write binary)!")
    else:
        print("❌ Failed to create corpus")


def view_corpus_info():
    print("\n📊 Corpus Information (using rb):")
    ngrams_obj = Ngrams()
    info = ngrams_obj.get_corpus_info()
    
    if "error" in info:
        print(f"❌ {info['error']}")
        return
    
    print(f"📁 File: {info['filename']}")
    print(f"📏 Total size: {info['total_size']:,} characters")
    print("\n📋 Sections:")
    
    for section, data in info['sections'].items():
        print(f"   • {section.capitalize()}:")
        print(f"     - Words: {data['word_count']:,}")
        print(f"     - Characters: {data['char_count']:,}")
        print(f"     - Sample: {data['sample']}")
        print()


def update_corpus_section():
    print("\n✏️ Update Corpus Section (rb + wb)")
    print("Choose difficulty:")
    print("1. Easy")
    print("2. Medium") 
    print("3. Hard")
    
    diff_choice = prompt("Difficulty choice (1-3): ")
    if diff_choice == "1":
        difficulty = "easy"
    elif diff_choice == "2":
        difficulty = "medium"
    elif diff_choice == "3":
        difficulty = "hard"
    else:
        print("Invalid choice")
        return
    
    print(f"\nEnter new text for {difficulty} section:")
    print("(Type 'END' on a new line to finish)")
    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    new_text = "\n".join(lines)
    if new_text.strip():
        ngrams_obj = Ngrams()
        success = ngrams_obj.update_corpus_section(difficulty, new_text)
        if success:
            print(f"✅ {difficulty} section updated successfully using rb + wb!")
        else:
            print(f"❌ Failed to update {difficulty} section")
    else:
        print("❌ No text provided")


def add_text_to_corpus():
    print("\n➕ Add Text to Corpus Section (rb + wb)")
    print("Choose difficulty:")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    
    diff_choice = prompt("Difficulty choice (1-3): ")
    if diff_choice == "1":
        difficulty = "easy"
    elif diff_choice == "2":
        difficulty = "medium"
    elif diff_choice == "3":
        difficulty = "hard"
    else:
        print("Invalid choice")
        return
    
    print(f"\nEnter additional text for {difficulty} section:")
    print("(Type 'END' on a new line to finish)")
    
    lines = []
    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)
    
    additional_text = "\n".join(lines)
    if additional_text.strip():
        ngrams_obj = Ngrams()
        success = ngrams_obj.add_text_to_corpus(difficulty, additional_text)
        if success:
            print(f"✅ Text added to {difficulty} section successfully using rb + wb!")
        else:
            print(f"❌ Failed to add text to {difficulty} section")
    else:
        print("❌ No text provided")


if __name__ == "__main__":
    main()
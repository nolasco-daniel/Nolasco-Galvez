import random
import math
import re
import pickle
from collections import Counter
from typing import List, Tuple, Union, Optional, Dict


class Ngrams:
    def __init__(self, corpus_file: Union[str, list, None] = None, n: int = 3, num_phrases: int = 5, difficulty: str = "medium"):
        if corpus_file is None:
            corpus_file = ["corpora/corpora.pkl"]
        self.corpus_file = corpus_file
        self.n = n
        self.num_phrases = num_phrases
        self.difficulty = difficulty.lower()
        
        self._text_cache: Optional[str] = None
        self._tokens_cache: Optional[List[str]] = None
        self._word_difficulty_cache: Dict[str, str] = {}
        self._tokens_analyzed: List[str] = []
        self._difficulty_words_cache: Optional[List[str]] = None
        
        self._difficulty_lengths = {"easy": 6, "medium": 8, "hard": 10}

    def save_corpus(self, data: dict, filename: str = "corpora/corpora.pkl") -> bool:
        try:
            with open(filename, "wb") as f:
                pickle.dump(data, f)
            print(f"✅ Corpus saved successfully to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving corpus: {e}")
            return False

    def create_corpus_from_text_files(self, output_file: str = "corpora/corpora.pkl") -> bool:
        try:
            corpus_data = {
                "easy": "",
                "medium": "", 
                "hard": ""
            }
            
            text_files = {
                "easy": "corpora/short-texts.txt",
                "medium": "corpora/medium-texts.txt",
                "hard": "corpora/long-texts.txt"
            }
            
            for difficulty, file_path in text_files.items():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        corpus_data[difficulty] = f.read()
                    print(f"📖 Loaded {difficulty} text from {file_path}")
                except FileNotFoundError:
                    print(f"⚠️ Warning: {file_path} not found, skipping...")
                    corpus_data[difficulty] = f"Sample {difficulty} text for typing practice."
            
            return self.save_corpus(corpus_data, output_file)
            
        except Exception as e:
            print(f"❌ Error creating corpus: {e}")
            return False

    def update_corpus_section(self, difficulty: str, new_text: str, filename: str = "corpora/corpora.pkl") -> bool:
        try:
            existing_data = {}
            try:
                with open(filename, "rb") as f:
                    existing_data = pickle.load(f)
            except FileNotFoundError:
                existing_data = {"easy": "", "medium": "", "hard": ""}
            
            existing_data[difficulty.lower()] = new_text
            
            return self.save_corpus(existing_data, filename)
            
        except Exception as e:
            print(f"❌ Error updating corpus section: {e}")
            return False

    def add_text_to_corpus(self, difficulty: str, additional_text: str, filename: str = "corpora/corpora.pkl") -> bool:
        try:
            existing_data = {}
            try:
                with open(filename, "rb") as f:
                    existing_data = pickle.load(f)
            except FileNotFoundError:
                existing_data = {"easy": "", "medium": "", "hard": ""}
            
            current_text = existing_data.get(difficulty.lower(), "")
            if current_text:
                updated_text = current_text + "\n\n" + additional_text
            else:
                updated_text = additional_text
            
            existing_data[difficulty.lower()] = updated_text
            
            return self.save_corpus(existing_data, filename)
            
        except Exception as e:
            print(f"❌ Error adding text to corpus: {e}")
            return False

    def get_corpus_info(self, filename: str = "corpora/corpora.pkl") -> dict:
        try:
            with open(filename, "rb") as f:
                data = pickle.load(f)
            
            info = {
                "filename": filename,
                "sections": {},
                "total_size": 0
            }
            
            for section, text in data.items():
                if isinstance(text, str):
                    word_count = len(text.split())
                    char_count = len(text)
                    sample = text[:100] + "..." if len(text) > 100 else text
                elif isinstance(text, (list, tuple)):
                    word_count = sum(len(str(item).split()) for item in text)
                    char_count = sum(len(str(item)) for item in text)
                    sample = str(text[:3]) + "..." if len(text) > 3 else str(text)
                else:
                    word_count = 0
                    char_count = len(str(text))
                    sample = str(text)[:100] + "..." if len(str(text)) > 100 else str(text)
                
                info["sections"][section] = {
                    "word_count": word_count,
                    "char_count": char_count,
                    "sample": sample
                }
                info["total_size"] += char_count
            
            return info
            
        except FileNotFoundError:
            return {"error": "Corpus file not found"}
        except Exception as e:
            return {"error": f"Error reading corpus: {e}"}

    def _extract_section_text(self, data: Union[str, List, tuple, dict], section: Optional[str]) -> str:
        if section and isinstance(data, dict):
            lower_map = {str(k).lower(): k for k in data.keys()}
            canonical = section.lower()
            synonym_map = {
                "easy": ["easy", "basic", "simple", "short"],
                "medium": ["medium", "moderate"],
                "hard": ["hard", "difficult", "deep", "long"]
            }
            candidates = synonym_map.get(canonical, [canonical])
            for cand in candidates:
                if cand in lower_map:
                    target_key = lower_map[cand]
                    target_val = data[target_key]
                    if isinstance(target_val, (list, tuple)):
                        target_list = [str(item) for item in target_val]
                        easier_sections = []
                        if canonical == "medium":
                            easier_sections = ["easy", "basic", "simple", "short"]
                        elif canonical == "hard":
                            easier_sections = ["easy", "basic", "simple", "short", "medium", "moderate"]
                        def _norm(s: str) -> str:
                            return " ".join(s.split()).strip().lower()
                        to_remove = set()
                        for ez in easier_sections:
                            if ez in lower_map and isinstance(data[lower_map[ez]], (list, tuple)):
                                to_remove.update(_norm(str(item)) for item in data[lower_map[ez]])
                        seen_norm = set()
                        exclusive_items = []
                        for s in target_list:
                            n = _norm(s)
                            if n in to_remove or n in seen_norm:
                                continue
                            seen_norm.add(n)
                            exclusive_items.append(s)
                        exclusive = exclusive_items
                        return "\n".join(exclusive)
                    if isinstance(target_val, str):
                        return target_val
        
        if isinstance(data, str):
            return data
        if isinstance(data, (list, tuple)):
            return "\n".join(str(item) for item in data)
        if isinstance(data, dict):
            collected_parts = []
            for value in data.values():
                if isinstance(value, str):
                    collected_parts.append(value)
                elif isinstance(value, (list, tuple)):
                    collected_parts.append("\n".join(str(item) for item in value))
            return "\n".join(collected_parts)
        raise ValueError("Unsupported data type in corpus.")

    def _load_text(self, corpus_file: str, difficulty_section: Optional[str] = None) -> str:
        try:
            if corpus_file.lower().endswith(".pkl"):
                with open(corpus_file, "rb") as f:
                    data = pickle.load(f)
                    content = self._extract_section_text(data, difficulty_section)
            else:
                with open(corpus_file, "r", encoding="utf-8") as f:
                    content = f.read()
            
            if not content or not str(content).strip():
                raise ValueError("Corpus file is empty.")

            return str(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"Corpus file '{corpus_file}' not found! Please ensure the file exists in the corpora directory.")
        except pickle.PickleError as e:
            raise ValueError(f"Invalid pickle file format: {e}. The corpus file may be corrupted.")
        except PermissionError:
            raise RuntimeError(f"Permission denied accessing '{corpus_file}'. Please check file permissions.")
        except Exception as e:
            raise RuntimeError(f"Error loading corpus file: {e}")

    def _tokenize(self, text: str, special_tokens: bool = True) -> List[str]:
        if not text or not text.strip():
            return []
        
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        tokens = []
        
        for sent in sentences:
            if not sent:
                continue
            
            if special_tokens:
                tokens.append("<START>")
            
            words = re.findall(r"\w+|[^\w\s]", sent)
            tokens.extend(words)
            
            if special_tokens:
                tokens.append("<END>")
        
        return tokens

    def _get_tokens(self, corpus_file: Union[str, List[str]], difficulty_section: Optional[str] = None) -> List[str]:
        if self._tokens_cache is not None:
            return self._tokens_cache
        
        if isinstance(corpus_file, (list, tuple)):
            combined_text_parts: List[str] = []
            for path in corpus_file:
                try:
                    part = self._load_text(str(path), difficulty_section=difficulty_section)
                    if part:
                        combined_text_parts.append(str(part))
                except FileNotFoundError:
                    continue
            text = "\n".join(combined_text_parts)
        else:
            text = self._load_text(corpus_file, difficulty_section=difficulty_section)
        
        tokens = self._tokenize(text, special_tokens=True)
        
        if random.random() < 0.2:
            shuffled_tokens = []
            current_sentence = []
            for token in tokens:
                if token == "<START>":
                    if current_sentence:
                        random.shuffle(current_sentence)
                        shuffled_tokens.extend(current_sentence)
                        current_sentence = []
                    shuffled_tokens.append(token)
                elif token == "<END>":
                    current_sentence.append(token)
                    random.shuffle(current_sentence)
                    shuffled_tokens.extend(current_sentence)
                    current_sentence = []
                else:
                    current_sentence.append(token)
            
            if current_sentence:
                random.shuffle(current_sentence)
                shuffled_tokens.extend(current_sentence)
            
            tokens = shuffled_tokens
        
        self._tokens_cache = tokens
        return tokens

    def _analyze_word_difficulty(self, tokens: List[str]) -> Dict[str, str]:
        if self._word_difficulty_cache and self._tokens_analyzed == tokens:
            return self._word_difficulty_cache

        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"] and len(token) > 1]
        
        word_counts = Counter(filtered_tokens)
        word_scores = self._calculate_word_complexity_scores(word_counts)
        word_difficulty = self._categorize_words_by_difficulty(word_scores)
        
        self._word_difficulty_cache = word_difficulty
        self._tokens_analyzed = tokens[:]
        return word_difficulty
    
    def _calculate_word_complexity_scores(self, word_counts: Counter) -> dict:
        word_scores = {}
        
        for word, count in word_counts.items():
            if len(word) < 2:
                continue
                
            length_score = self._calculate_length_score(word)
            freq_score = self._calculate_frequency_score(word, count, word_counts)
            complexity_score = self._calculate_pattern_complexity_score(word)
            syllable_score = self._calculate_syllable_score(word)
            
            total_score = length_score + freq_score + complexity_score + syllable_score
            word_scores[word] = total_score
        
        return word_scores
    
    def _calculate_length_score(self, word: str) -> float:
        return len(word) * 0.3
    
    def _calculate_frequency_score(self, word: str, count: int, word_counts: Counter) -> float:
        total_words = sum(word_counts.values())
        return (1 - (count / total_words)) * 5
    
    def _calculate_pattern_complexity_score(self, word: str) -> float:
        complexity_score = 0.0
        consonants = 0
        
        for char in word.lower():
            if char in 'aeiou':
                consonants = 0
            elif char.isalpha():
                consonants += 1
                if consonants >= 3:
                    complexity_score += 1.0
            else:
                complexity_score += 0.5
        
        return complexity_score
    
    def _calculate_syllable_score(self, word: str) -> float:
        consonants = sum(1 for char in word.lower() if char.isalpha() and char not in 'aeiou')
        vowels = sum(1 for char in word.lower() if char in 'aeiou')
        
        syllable_count = max(1, (consonants + vowels) // 3)
        return syllable_count * 0.5
    
    def _categorize_words_by_difficulty(self, word_scores: dict) -> dict:
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1])
        total_words = len(sorted_words)
        
        easy_threshold = int(total_words * 0.4)
        medium_threshold = int(total_words * 0.8)
        
        word_difficulty = {}
        for i, (word, score) in enumerate(sorted_words):
            if i < easy_threshold:
                word_difficulty[word] = "easy"
            elif i < medium_threshold:
                word_difficulty[word] = "medium"
            else:
                word_difficulty[word] = "hard"
        
        return word_difficulty

    def generate_phrases(self) -> List[str]:
        self.clear_cache()
        
        random.seed()
        
        tokens = self._get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        return self._generate_phrases(tokens, self.num_phrases)

    def _generate_phrases(self, tokens: List[str], num_phrases: int) -> List[str]:
        if len(tokens) < max(2, self.n):
            return self._generate_fallback_phrases(tokens, num_phrases)

        self._analyze_word_difficulty(tokens)

        models_by_order, unigram_counts = self._build_ngram_model(tokens)

        def in_length_range(length: int) -> bool:
            if self.difficulty == "easy":
                return length <= 4
            if self.difficulty == "medium":
                return 5 <= length <= 7
            return length >= 8

        phrases: List[str] = []
        used_phrases = set()
        
        for _ in range(num_phrases):
            target_len = self._get_target_phrase_length()
            max_attempts = 10
            
            for attempt in range(max_attempts):
                phrase_words = self._generate_phrase_with_model(models_by_order, unigram_counts, target_len, in_length_range)
                if not phrase_words:
                    fallback_phrase = self._generate_fallback_phrases(tokens, 1)[0]
                    if fallback_phrase not in used_phrases:
                        phrases.append(fallback_phrase)
                        used_phrases.add(fallback_phrase)
                    break
                else:
                    phrase = " ".join(phrase_words)
                    if phrase not in used_phrases:
                        phrases.append(phrase)
                        used_phrases.add(phrase)
                        break
                    if attempt < max_attempts - 1:
                        target_len = self._get_target_phrase_length()
                        continue
                    else:
                        variation = self._create_phrase_variation(phrase_words)
                        if variation not in used_phrases:
                            phrases.append(variation)
                            used_phrases.add(variation)
                        break
        
        return phrases

    def _build_ngram_model(self, tokens: List[str]) -> Tuple[Dict[int, Dict[Tuple[str, ...], Counter]], Counter]:
        cleaned: List[str] = []
        for t in tokens:
            if t in ("<START>", "<END>"):
                cleaned.append(t)
            elif t.isalpha():
                cleaned.append(t)
        n = max(2, int(self.n))
        models_by_order: Dict[int, Dict[Tuple[str, ...], Counter]] = {k: {} for k in range(2, n + 1)}
        unigram_counts: Counter = Counter()

        context: List[str] = []
        for tok in cleaned:
            if tok == "<START>":
                context = ["<START>"] * (n - 1)
                continue
            if not context:
                context = ["<START>"] * (n - 1)

            if tok != "<START>":
                unigram_counts[tok] += 1

            for order in range(2, n + 1):
                ctx_tuple = tuple(context[-(order - 1):]) if order > 1 else tuple()
                bucket = models_by_order[order]
                bucket.setdefault(ctx_tuple, Counter())[tok] += 1

            context.append(tok)
            if tok == "<END>":
                context = []

        if "<END>" not in unigram_counts:
            unigram_counts["<END>"] = 1

        return models_by_order, unigram_counts

    def _generate_phrase_with_model(
        self,
        models_by_order: Dict[int, Dict[Tuple[str, ...], Counter]],
        unigram_counts: Counter,
        target_words: int,
        in_length_range_fn,
    ) -> List[str]:
        n = max(2, int(self.n))
        words: List[str] = []
        
        if random.random() < 0.3:
            all_words = [tok for tok in unigram_counts.keys() if tok.isalpha() and tok not in ["<START>", "<END>"]]
            if all_words:
                random_start = random.choice(all_words)
                context = [random_start] + ["<START>"] * (n - 2) if n > 2 else [random_start]
            else:
                context = ["<START>"] * (n - 1)
        else:
            context = ["<START>"] * (n - 1)
        
        max_steps = target_words * 3

        for _ in range(max_steps):
            ctx_tuple = tuple(context[-(n - 1):]) if n > 1 else tuple()
            next_token = self._sample_next_token(ctx_tuple, models_by_order, unigram_counts, in_length_range_fn)
            if next_token is None:
                break
            if next_token == "<END>":
                if len(words) >= max(1, target_words // 2):
                    break
                continue
            
            if next_token.isalpha():
                if in_length_range_fn(len(next_token)):
                    words.append(next_token)
            context.append(next_token)
            if len(words) >= target_words:
                break
        return words

    def _sample_next_token(
        self,
        ctx: Tuple[str, ...],
        models_by_order: Dict[int, Dict[Tuple[str, ...], Counter]],
        unigram_counts: Counter,
        in_length_range_fn,
    ) -> Optional[str]:
        n = max(2, int(self.n))
        lambdas = self._get_interpolation_weights(n)

        candidates = list(unigram_counts.keys())
        if not candidates:
            return None

        total_unigrams = sum(unigram_counts.values()) or 1

        ctx_lists: Dict[int, Tuple[str, ...]] = {}
        for order in range(2, n + 1):
            ctx_lists[order] = tuple(ctx[-(order - 1):]) if (order - 1) > 0 else tuple()

        scores: Dict[str, float] = {}
        for tok in candidates:
            p = lambdas[1] * (unigram_counts.get(tok, 0) / total_unigrams)
            for order in range(2, n + 1):
                weight = lambdas[order]
                if weight <= 0:
                    continue
                dist = models_by_order.get(order, {}).get(ctx_lists[order])
                if dist:
                    denom = sum(dist.values()) or 1
                    p += weight * (dist.get(tok, 0) / denom)
            p += random.uniform(0, 0.01)
            scores[tok] = p

        good_tokens = [t for t in candidates if t == "<END>" or (t.isalpha() and in_length_range_fn(len(t)))]
        pool = good_tokens if good_tokens else candidates

        temperature = 1.2 + random.uniform(0, 0.3)
        
        if temperature != 1.0:
            for tok in pool:
                scores[tok] = scores.get(tok, 0.0) ** (1.0 / temperature)

        total = sum(scores.get(t, 0.0) for t in pool)
        if total <= 0:
            return random.choice(pool)

        if random.random() < 0.1:
            return random.choice(pool)

        r = random.random() * total
        upto = 0.0
        for t in pool:
            upto += scores.get(t, 0.0)
            if upto >= r:
                return t
        return pool[-1]

    def _get_interpolation_weights(self, n: int) -> Dict[int, float]:
        if n <= 2:
            return {1: 0.3, 2: 0.7}
        if n == 3:
            return {1: 0.1, 2: 0.3, 3: 0.6}
        if n == 4:
            return {1: 0.1, 2: 0.15, 3: 0.3, 4: 0.45}
        weights: Dict[int, float] = {}
        remaining = 1.0
        high = 0.45
        step = (high - 0.1) / max(1, n - 2)
        for order in range(n, 1, -1):
            w = max(0.1, min(high, 0.1 + step * (order - 2)))
            weights[order] = w
            remaining -= w
        weights[1] = max(0.05, remaining)
        s = sum(weights.values()) or 1.0
        for k in list(weights.keys()):
            weights[k] = weights[k] / s
        return weights

    def _generate_wordlist_phrases_unique(self, words: List[str], num_phrases: int) -> List[str]:
        phrases: List[str] = []
        used_words = set()
        for _ in range(num_phrases):
            target_len = self._get_target_phrase_length()
            available = [w for w in words if w not in used_words]
            if len(available) >= target_len:
                sampled = random.sample(available, target_len)
            elif available:
                sampled = available[:]
                remaining = target_len - len(sampled)
                pool = words
                while remaining > 0 and pool:
                    candidate = random.choice(pool)
                    if sampled and candidate == sampled[-1]:
                        continue
                    sampled.append(candidate)
                    remaining -= 1
            else:
                sampled = []
                for _i in range(target_len):
                    candidate = random.choice(words)
                    if sampled and candidate == sampled[-1]:
                        continue
                    sampled.append(candidate)
            for w in sampled:
                used_words.add(w)
            phrases.append(" ".join(sampled))
        return phrases

    def _generate_fallback_phrases(self, tokens: List[str], num_phrases: int) -> List[str]:
        tokens_copy = tokens[:]
        random.shuffle(tokens_copy)
        fallback = " ".join(tokens_copy[:10]) if tokens_copy else ""
        return [fallback for _ in range(num_phrases)]

    def _get_target_phrase_length(self) -> int:
        base_length = self._difficulty_lengths.get(self.difficulty, 8)
        return base_length + random.randint(0, 3)
    
    def _create_phrase_variation(self, phrase_words: List[str]) -> str:
        if not phrase_words:
            return ""
        
        if len(phrase_words) > 1 and random.random() < 0.3:
            shuffled = phrase_words[:]
            random.shuffle(shuffled)
            return " ".join(shuffled)
        elif len(phrase_words) > 2 and random.random() < 0.4:
            start = random.randint(0, len(phrase_words) - 2)
            end = random.randint(start + 1, len(phrase_words))
            return " ".join(phrase_words[start:end])
        else:
            return " ".join(phrase_words) + " " + random.choice(["now", "here", "there", "then", "soon"])

    def get_word_frequencies(self, top_k: int = 20) -> List[Tuple[str, int]]:
        tokens = self._get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"]]
        word_counts = Counter(filtered_tokens)
        return word_counts.most_common(top_k)

    def get_difficulty_stats(self) -> dict:
        tokens = self._get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        self._analyze_word_difficulty(tokens)
        return self._get_difficulty_stats()

    def _get_difficulty_stats(self) -> Dict[str, Dict]:
        if not self._word_difficulty_cache:
            raise ValueError("No word difficulty analysis performed yet. Call analyze_word_difficulty() first.")
        
        easy_words = [word for word, diff in self._word_difficulty_cache.items() if diff == "easy"]
        medium_words = [word for word, diff in self._word_difficulty_cache.items() if diff == "medium"]
        hard_words = [word for word, diff in self._word_difficulty_cache.items() if diff == "hard"]
        
        return {
            "easy": {
                "count": len(easy_words),
                "sample_words": easy_words[:10]
            },
            "medium": {
                "count": len(medium_words),
                "sample_words": medium_words[:10]
            },
            "hard": {
                "count": len(hard_words),
                "sample_words": hard_words[:10]
            }
        }

    def get_model_stats(self) -> dict:
        tokens = self._get_tokens(self.corpus_file, difficulty_section=self.difficulty)
        
        filtered_tokens = [token for token in tokens 
                          if token not in ["<START>", "<END>"]]
        
        return {
            "total_tokens": len(tokens),
            "unique_words": len(set(filtered_tokens)),
            "n_gram_order": self.n,
            "vocabulary_size": len(set(filtered_tokens)),
            "difficulty": self.difficulty,
            "difficulty_stats": self.get_difficulty_stats()
        }
    
    def clear_cache(self):
        self._text_cache = None
        self._tokens_cache = None
        self._word_difficulty_cache.clear()
        self._tokens_analyzed.clear()
        self._difficulty_words_cache = None


def print_menu(title: str, options: List[str]) -> None:
    print(f"\n--- {title} ---")
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

def prompt(message: str) -> str:
    return input(message)

def format_frequency_table(word_freqs: List[tuple], title: str = "Word Frequencies") -> str:
    if not word_freqs:
        return f"{title}\nNo data available."
        
    max_word_len = max(len(word) for word, _ in word_freqs)
    
    table = f"\n=== {title} ===\n"
    table += f"{'Word':<{max_word_len + 2}} {'Frequency':<12} {'Percentage':<12}\n"
    table += "-" * (max_word_len + 30) + "\n"
    
    total_freq = sum(freq for _, freq in word_freqs)
    
    for word, freq in word_freqs:
        percentage = (freq / total_freq) * 100 if total_freq > 0 else 0
        table += f"{word:<{max_word_len + 2}} {freq:<12} {percentage:.1f}%\n"
        
    table += f"\nTotal frequency: {total_freq}"
    return table

def validate_input(text: str, min_length: int = 1) -> bool:
    if not text:
        return False
    s = text.strip()
    return len(s) >= min_length

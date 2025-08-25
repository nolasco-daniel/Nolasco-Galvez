import re
import json
import os
import random

class Tokenizer:
    def __init__(self):
        self.pattern = re.compile(r"\w+|[^\w\s]|\s+", re.IGNORECASE)

    def tokenize(self, text):
        return self.pattern.findall(text)

class JejemonNormalizer:
    def __init__(self):
        data_path = os.path.join(os.path.dirname(__file__), 'data.json')
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.word_map = data["word_map"]
        self.reverse_word_map = {v: k for k, v in self.word_map.items()}
        self.char_map = {
            replacement: letter
            for letter, replacements in data["char_map"].items()
            for replacement in replacements
        }
        self.original_char_map = data["char_map"]

    def preserve_casing(self, original, converted):
        if original.isupper():
            return converted.upper()
        elif original[0].isupper():
            return converted.capitalize()
        return converted

    def remove_vowels(self, word):
        return ''.join([c for c in word if c.lower() not in 'aeiou'])

    def normalize_token(self, token):
        if token.strip() == "":
            return token

        lowered = token.lower()

        if len(lowered) <= 2 and lowered not in self.word_map:
            replaced = self._multi_replace(lowered, self.char_map)
            return self.preserve_casing(token, replaced)

        if lowered in self.word_map:
            normalized = self.word_map[lowered]
            return self.preserve_casing(token, normalized)

        token_no_vowels = self.remove_vowels(lowered)
        for jej_word, tag_word in self.word_map.items():
            if self.remove_vowels(jej_word) == token_no_vowels:
                return self.preserve_casing(token, tag_word)

        corrected, dist = find_closest_word(lowered, self.word_map.keys(), max_distance=1)
        if corrected:
            normalized = self.word_map[corrected]
            return self.preserve_casing(token, normalized)

        normalized = self._multi_replace(lowered, self.char_map)
        return self.preserve_casing(token, normalized)

    def _multi_replace(self, text, replace_map):
        for key in sorted(replace_map, key=len, reverse=True):
            text = text.replace(key, replace_map[key])
        return text

    def normalize(self, text, tokenizer=None, max_passes=3):
        if tokenizer is None:
            tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(text)

        for i in range(max_passes):
            new_tokens = [self.normalize_token(tok) for tok in tokens]
            if new_tokens == tokens:
                break
            tokens = new_tokens

        return "".join(tokens)

    def jejemonize_token(self, token, seed=None):
        if token.strip() == "":
            return token

        if seed is not None:
            random.seed(seed)

        lowered = token.lower()

        if lowered in self.reverse_word_map:
            jej = self.reverse_word_map[lowered]
        else:
            jej = ""
            for c in lowered:
                if c in self.original_char_map:
                    jej += random.choice(self.original_char_map[c])
                else:
                    jej += c

        return self.preserve_casing(token, jej)

    def jejemonize(self, text, tokenizer=None, seed=None):
        if tokenizer is None:
            tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(text)
        return "".join([self.jejemonize_token(tok, seed=seed) for tok in tokens])

def edit_distance(s1, s2):
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insert = previous_row[j + 1] + 1
            delete = current_row[j] + 1
            substitute = previous_row[j] + (c1 != c2)
            current_row.append(min(insert, delete, substitute))
        previous_row = current_row
    return previous_row[-1]

def find_closest_word(word, word_list, max_distance=1):
    closest_word = None
    closest_distance = None
    for candidate in word_list:
        dist = edit_distance(word, candidate)
        if closest_distance is None or dist < closest_distance:
            closest_word = candidate
            closest_distance = dist
    if closest_distance is not None and closest_distance <= max_distance:
        return closest_word, closest_distance
    return None, None

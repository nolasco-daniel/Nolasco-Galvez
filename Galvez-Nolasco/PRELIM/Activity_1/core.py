import json
import os
import re
import random

class ChatbotCore:
    def __init__(self, db_path="chatbot_database.json"):
        self.db_path = db_path
        self.user_name = "friend"
        self.bot_name = "Buddy"
        self.total_messages = 0
        self.knowledge_patterns = []

        self.stop_words_list = [
            "i", "me", "my", "myself", "we", "our", "ours", "ourselves",
            "you", "your", "yours", "yourself", "yourselves", "he", "him",
            "his", "himself", "she", "her", "hers", "herself", "it", "its",
            "itself", "they", "them", "their", "theirs", "themselves", "what",
            "which", "who", "whom", "this", "that", "these", "those", "am",
            "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "having", "do", "does", "did", "doing", "a", "an", "the",
            "and", "but", "if", "or", "because", "as", "until", "while", "of",
            "at", "by", "for", "with", "about", "against", "between", "into",
            "through", "during", "before", "after", "above", "below", "to",
            "from", "up", "down", "in", "out", "on", "off", "over", "under",
            "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "any", "both", "each", "few", "more", "most",
            "other", "some", "such", "no", "nor", "not", "only", "own", "same",
            "so", "than", "too", "very", "can", "will", "just", "don", "should", "now"
        ]

        self.positive_words = ["happy", "great", "awesome", "love", "good", "fantastic", "cool", "fun"]
        self.negative_words = ["sad", "angry", "hate", "bad", "terrible", "depressed", "cry", "lonely"]

        self.load_database()

    def create_default_database(self):
        return {
            "patterns": [],
            "total_messages": 0
        }

    def load_database(self):
        if not os.path.exists(self.db_path):
            data = self.create_default_database()
        else:
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Error loading database: {e}. Creating new database.")
                data = self.create_default_database()

        self.knowledge_patterns = data.get("patterns", [])
        self.total_messages = data.get("total_messages", 0)

    def save_database(self):
        try:
            with open(self.db_path, "w", encoding="utf-8") as f:
                json.dump({
                    "patterns": self.knowledge_patterns,
                    "total_messages": self.total_messages
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to save database: {e}")

    def map_synonym(self, word):
        synonyms = {
            "hi": "hello", "hey": "hello", "yo": "hello", "sup": "hello", "greetings": "hello",
            "name": "identity", "who": "identity"
        }
        return synonyms.get(word, word)

    def tokenize_and_match(self, text, pattern=None):
        cleaned = re.sub(r"[^\w\s']", "", text.lower())
        raw_tokens = re.findall(r'\b\w{2,}\b', cleaned)
        tokens = [self.map_synonym(t) for t in raw_tokens if t not in self.stop_words_list]

        if pattern:
            return tokens, re.search(pattern, cleaned)
        else:
            return tokens, None

    def detect_sentiment(self, tokens):
        pos = sum(1 for w in tokens if w in self.positive_words)
        neg = sum(1 for w in tokens if w in self.negative_words)
        return "positive" if pos > neg else "negative" if neg > pos else "neutral"

    def fallback_suggestion(self):
        suggestions = [
            "Try asking me how I'm feeling 😊",
            "You can ask me to tell a joke!",
            "I can remember your name if you tell me 😊",
            "Try saying 'help' or 'what can you do?'"
        ]
        return random.choice(suggestions)

    def get_bot_response(self, user_input):
        if not user_input.strip():
            return "Please say something! 😊"

        self.total_messages += 1

        lower_input = user_input.lower()
        bot_name_patterns = ["who are you", "what is your name", "what's your name"]
        user_name_patterns = ["who am i", "what is my name", "what's my name"]
        if any(p in lower_input for p in bot_name_patterns) and any(p in lower_input for p in user_name_patterns):
            return f"I'm {self.bot_name} and your name is {self.user_name}!"

        tokens, match = self.tokenize_and_match(user_input, r"\bmy name is ([a-zA-Z]+)\b")
        if match:
            self.user_name = match.group(1).capitalize()
            return f"Nice to meet you, {self.user_name}! 😊"

        _, match = self.tokenize_and_match(user_input, r"\b(what's my name|who am i)\b")
        if match:
            return f"You're {self.user_name}! 😄" if self.user_name != "friend" else "I don't know your name yet! Say 'My name is [your name]' 😊"

        matched_patterns = []
        for pattern in self.knowledge_patterns:
            try:
                regex = re.compile(pattern["pattern"], re.IGNORECASE)
                if regex.search(user_input):
                    matched_patterns.append(pattern)
            except Exception as e:
                print(f"⚠️ Regex failed: {e}")

        if matched_patterns:
            pattern_strings = [p["pattern"] for p in matched_patterns]
            if len(set(pattern_strings)) == 1:
                p = matched_patterns[0]
                response = p["response"]
                chosen_response = random.choice(response) if isinstance(response, list) else response
                return chosen_response.format(bot_name=self.bot_name, user_name=self.user_name)

            responses = []
            for p in matched_patterns:
                response = p["response"]
                chosen_response = random.choice(response) if isinstance(response, list) else response
                responses.append(chosen_response)
            unique_responses = list(dict.fromkeys(responses))
            formatted_responses = [r.format(bot_name=self.bot_name, user_name=self.user_name) for r in unique_responses]
            return " ".join(formatted_responses)

        print(f"❓ No pattern matched: {user_input}")
        return f"I'm not sure about that, {self.user_name}. Try asking something else! 🤔"

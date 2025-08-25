from core import Tokenizer, JejemonNormalizer

class JejemonTranslator:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.normalizer = JejemonNormalizer()

    def is_jejemon(self, text):
        word_map = self.normalizer.word_map
        tokens = self.tokenizer.tokenize(text)
        return any(any(c.isdigit() or c in "@" for c in tok) or tok.lower() in word_map for tok in tokens)

    def normalize(self, text):
        tokens = self.tokenizer.tokenize(text)
        normalized_tokens = [self.normalizer.normalize_token(tok) for tok in tokens]
        return "".join(token for token in normalized_tokens if token is not None)

    def jejemonize(self, text):
        return self.normalizer.jejemonize(text, self.tokenizer)

import pygame

from typing_game import TypingGame


def run_typing_test_with_ngrams(difficulty: str = "medium", time_limit: int = 60):
    try:
        game = TypingGame()
        if difficulty.lower() == "easy":
            game.difficulty = "Easy"
        elif difficulty.lower() == "medium":
            game.difficulty = "Medium"
        elif difficulty.lower() == "hard":
            game.difficulty = "Hard"
        game.time_limit = time_limit
        if hasattr(game, "custom_button"):
            game.custom_button.text = f"Time: {time_limit}s"
        game.run()
    except Exception as e:
        print(f"Error starting typing test: {e}")
        print("Make sure pygame is installed: pip install pygame")


if __name__ == "__main__":
    game = TypingGame()
    game.run()




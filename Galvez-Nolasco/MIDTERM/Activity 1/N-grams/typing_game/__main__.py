try:
    from . import TypingGame
except Exception:
    from typing_game import TypingGame


def main() -> None:
    game = TypingGame()
    game.run()


if __name__ == "__main__":
    main()



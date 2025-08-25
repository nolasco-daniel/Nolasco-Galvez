## N-Grams Typing Challenge

A modern typing test that generates practice text using N-gram language models with difficulty levels. Built with Python and Pygame.

### Features

- **N-gram generator**: Easy, Medium, Hard word selections from `corpora/corpora.pkl`
- **Modern UI**: Animated buttons, gradient background, particle effects
- **Typing metrics**: WPM, accuracy, progress bar, results screen
- **Flexible timing**: 15/30/60/120 seconds
- **CLI and GUI**: Use the console menu or launch the typing game directly

### Requirements

- Python 3.9+
- Pygame

Install dependencies:

```bash
pip install pygame
```

### Quick Start

- Run the interactive console menu:

```bash
python main.py
```

- Launch the typing game directly:

```bash
python typing_test.py
```

### Project Structure

```text
N-grams/
  corpora/
    corpora.pkl            # Pickled corpus with easy/medium/hard sections
    eng_sentences.txt      # (Optional) raw text sources
    long-texts.txt
    medium-texts.txt
    short-texts.txt
  multimedia/
    bg.png
  typing_game/
    __init__.py
    constants.py           # Sizes, colors, states
    particles.py           # Particle effect
    ui.py                  # Buttons and UI widgets
    game.py                # TypingGame class (main logic)
  ngrams.py                # N-gram model and helpers
  typing_test.py           # Entry point for GUI; keeps a public wrapper function
  main.py                  # Console menu that can launch the GUI
  README.md
```

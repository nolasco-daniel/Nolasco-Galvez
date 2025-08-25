import time
import random
from typing import Tuple, List

import pygame

from .constants import (
    MENU_WIDTH,
    MENU_HEIGHT,
    GAME_WIDTH,
    GAME_HEIGHT,
    FPS,
    BLACK,
    WHITE,
    PRIMARY_BLUE,
    SECONDARY_BLUE,
    ACCENT_BLUE,
    SUCCESS_GREEN,
    SUCCESS_DARK,
    WARNING_ORANGE,
    WARNING_DARK,
    ERROR_RED,
    NEUTRAL_GRAY,
    NEUTRAL_DARK,
    BG_DARKEST,
    BG_DARK,
    BG_MEDIUM,
    GRADIENT_START,
    GRADIENT_END,
    MENU,
    GAME,
    RESULTS,
)
from .particles import Particle
from .ui import ModernButton, OutlineButton
from ngrams import Ngrams


class TypingGame:
    def __init__(self):
        if not pygame.get_init():
            pygame.init()
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception:
            pass

        self.current_width = MENU_WIDTH
        self.current_height = MENU_HEIGHT
        self.screen = pygame.display.set_mode((self.current_width, self.current_height))
        pygame.display.set_caption("Grammytype - Test your skills here")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 84)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.font_tiny = pygame.font.Font(None, 28)
        try:
            self.menu_background = pygame.image.load("multimedia/bg.png")
            self.menu_background = pygame.transform.scale(self.menu_background, (MENU_WIDTH, MENU_HEIGHT))
        except Exception:
            self.menu_background = None
        self.state = MENU
        self.particles: List[Particle] = []
        self.background_particles: List[Particle] = []
        self.typing_text = ""
        self.target_text = ""
        self.start_time = 0.0
        self.is_typing = False
        self.current_char_index = 0
        self.correct_chars = 0
        self.total_chars = 0
        self.wpm = 0.0
        self.accuracy = 0.0
        self.elapsed_time = 0.0
        self.difficulty = "Medium"
        self.n_gram = 3
        self.num_phrases = 8
        self.time_limit = 60
        self.time_remaining = self.time_limit
        self.base_target_len = 8
        self.avg_word_len = 6.0
        self.ngrams_obj = None
        self.render_start_index = 0
        self.setup_ui()
        self.generate_background_particles()
        self.menu_animation_time = 0
        self.title_glow = 0
        self.background_shift = 0

    def setup_ui(self):
        row_button_width, row_button_height = 260, 54
        gap = 40
        start_x = MENU_WIDTH // 2 - (3 * row_button_width + 2 * gap) // 2
        row_y = 360
        self.easy_button = OutlineButton(start_x, row_y, row_button_width, row_button_height, "Easy Mode", SUCCESS_GREEN, 26)
        self.medium_button = OutlineButton(start_x + row_button_width + gap, row_y, row_button_width, row_button_height, "Medium Mode", PRIMARY_BLUE, 26)
        self.hard_button = OutlineButton(start_x + (row_button_width + gap) * 2, row_y, row_button_width, row_button_height, "Hard Mode", ERROR_RED, 26)

        second_gap = 80
        start_x2 = MENU_WIDTH // 2 - (2 * row_button_width + second_gap) // 2
        row2_y = row_y + 90
        self.custom_button = OutlineButton(start_x2, row2_y, row_button_width, row_button_height, f"Time: {self.time_limit}s", ACCENT_BLUE, 26)
        self.exit_button = OutlineButton(start_x2 + row_button_width + second_gap, row2_y, row_button_width, row_button_height, "Exit", NEUTRAL_GRAY, 26)

        self.restart_button = ModernButton(60, 60, 140, 50, "Restart", WARNING_ORANGE, WARNING_DARK)
        self.menu_button = ModernButton(210, 60, 140, 50, "Menu", NEUTRAL_GRAY, NEUTRAL_DARK)

        results_button_width, results_button_height = 220, 50
        spacing = 40
        total_width = results_button_width * 2 + spacing
        start_x = GAME_WIDTH // 2 - total_width // 2
        y = GAME_HEIGHT - 150

        self.play_again_button = ModernButton(start_x, y, results_button_width, results_button_height, "Play Again", SUCCESS_GREEN, SUCCESS_DARK)
        self.back_to_menu_button = ModernButton(start_x + results_button_width + spacing, y, results_button_width, results_button_height, "Back to Menu", PRIMARY_BLUE, SECONDARY_BLUE)

    def resize_window(self, width: int, height: int):
        self.current_width = width
        self.current_height = height
        self.screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
        self.background_particles.clear()
        self.generate_background_particles()

    def generate_background_particles(self):
        for _ in range(60):
            x = random.randint(0, self.current_width)
            y = random.randint(0, self.current_height)
            colors = [PRIMARY_BLUE, SUCCESS_GREEN, ACCENT_BLUE, WARNING_ORANGE]
            color = random.choice(colors)
            vx = random.uniform(-0.2, 0.2)
            vy = random.uniform(-0.2, 0.2)
            particle = Particle(x, y, color, (vx, vy))
            particle.life = random.uniform(0.3, 0.7)
            self.background_particles.append(particle)

    def create_particles(self, x: int, y: int, color: Tuple[int, int, int], count: int = 12):
        for _ in range(count):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            particle = Particle(x, y, color, (vx, vy))
            self.particles.append(particle)

    def update_particles(self):
        for particle in self.background_particles:
            particle.update()
            if particle.life <= 0:
                particle.x = random.randint(0, self.current_width)
                particle.y = random.randint(0, self.current_height)
                particle.life = random.uniform(0.3, 0.7)
        self.particles = [p for p in self.particles if p.life > 0]
        for particle in self.particles:
            particle.update()

    def draw_particles(self):
        for particle in self.background_particles:
            particle.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)

    def draw_modern_background(self):
        self.menu_animation_time += 0.008
        self.background_shift += 0.002
        self.screen.fill(BG_DARKEST)
        for y in range(0, self.current_height, 2):
            ratio = y / self.current_height
            time_offset = random.random() * 0.0 + 0.0
            r = int(GRADIENT_START[0] * (1 - ratio + time_offset) + GRADIENT_END[0] * (ratio - time_offset))
            g = int(GRADIENT_START[1] * (1 - ratio + time_offset) + GRADIENT_END[1] * (ratio - time_offset))
            b = int(GRADIENT_START[2] * (1 - ratio + time_offset) + GRADIENT_END[2] * (ratio - time_offset))
            r = max(8, min(25, r))
            g = max(12, min(35, g))
            b = max(18, min(45, b))
            color = (r, g, b)
            pygame.draw.line(self.screen, color, (0, y), (self.current_width, y))
        for i in range(3):
            offset = (self.background_shift + i * 0.3) % self.current_width
            alpha = 30 - i * 8
            accent_surf = pygame.Surface((200, 2), pygame.SRCALPHA)
            pygame.draw.rect(accent_surf, (*PRIMARY_BLUE, alpha), accent_surf.get_rect())
            self.screen.blit(accent_surf, (offset, 100 + i * 200))

    def draw_menu(self):
        if self.current_width != MENU_WIDTH or self.current_height != MENU_HEIGHT:
            self.resize_window(MENU_WIDTH, MENU_HEIGHT)
        if self.menu_background:
            self.screen.blit(self.menu_background, (0, 0))
        else:
            self.draw_modern_background()
            self.draw_particles()
        mouse_pos = pygame.mouse.get_pos()
        self.easy_button.update(mouse_pos)
        self.medium_button.update(mouse_pos)
        self.hard_button.update(mouse_pos)
        self.custom_button.update(mouse_pos)
        self.exit_button.update(mouse_pos)
        self.easy_button.draw(self.screen)
        self.medium_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        self.custom_button.draw(self.screen)
        self.exit_button.draw(self.screen)

    def draw_game(self):
        if self.current_width != GAME_WIDTH or self.current_height != GAME_HEIGHT:
            self.resize_window(GAME_WIDTH, GAME_HEIGHT)

        self.draw_modern_background()
        self.draw_particles()

        header_rect = pygame.Rect(0, 0, GAME_WIDTH, 140)
        header_surf = pygame.Surface((GAME_WIDTH, 140), pygame.SRCALPHA)
        pygame.draw.rect(header_surf, (*BG_DARK, 200), header_surf.get_rect())
        pygame.draw.rect(header_surf, (*WHITE, 20), header_surf.get_rect(), 1)
        self.screen.blit(header_surf, header_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.update(mouse_pos)
        self.menu_button.update(mouse_pos)
        self.restart_button.draw(self.screen)
        self.menu_button.draw(self.screen)

        if self.is_typing:
            elapsed = time.time() - self.start_time
            self.time_remaining = max(0, self.time_limit - elapsed)
            if self.time_remaining <= 0:
                self.end_game()

        panel_width = 180
        panel_height = 35
        panel_spacing = 10
        start_x = GAME_WIDTH - (panel_width * 3 + panel_spacing * 2 + 20)
        panel_y = 60
        info_panels = [
            (f" {self.difficulty}", PRIMARY_BLUE, start_x, panel_y),
            (f" {self.time_remaining:.1f}s" if self.is_typing else " Start typing", SECONDARY_BLUE, start_x + panel_width + panel_spacing, panel_y),
        ]
        if self.is_typing:
            typed_chars = len(self.typing_text)
            if typed_chars > 0:
                accuracy = (self.correct_chars / typed_chars) * 100
                info_panels.append((f" {accuracy:.1f}%", SUCCESS_GREEN, start_x + (panel_width + panel_spacing) * 2, panel_y))
        for text, color, x, y in info_panels:
            panel_rect = pygame.Rect(x, y, panel_width, panel_height)
            panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            pygame.draw.rect(panel_surf, (*BG_DARK, 220), panel_surf.get_rect(), border_radius=12)
            pygame.draw.rect(panel_surf, (*color, 100), panel_surf.get_rect(), 2, border_radius=12)
            self.screen.blit(panel_surf, panel_rect)
            text_surface = self.font_tiny.render(text, True, WHITE)
            text_rect = text_surface.get_rect(center=panel_rect.center)
            self.screen.blit(text_surface, text_rect)

        typing_area = pygame.Rect(10, 160, GAME_WIDTH - 20, 360)
        typing_surf = pygame.Surface((typing_area.width, typing_area.height), pygame.SRCALPHA)
        pygame.draw.rect(typing_surf, (*BG_MEDIUM, 180), typing_surf.get_rect(), border_radius=25)
        pygame.draw.rect(typing_surf, (*WHITE, 30), typing_surf.get_rect(), 2, border_radius=25)
        inner_rect = pygame.Rect(15, 15, typing_area.width - 30, typing_area.height - 30)
        pygame.draw.rect(typing_surf, (*BG_DARK, 100), inner_rect, border_radius=20)
        self.screen.blit(typing_surf, typing_area)

        if self.target_text:
            self.draw_target_text(typing_area)

        if self.total_chars > 0:
            progress = self.correct_chars / self.total_chars
            progress_width = (GAME_WIDTH - 120) * progress
            progress_bg_rect = pygame.Rect(60, 700, GAME_WIDTH - 120, 30)
            progress_bg_surf = pygame.Surface((progress_bg_rect.width, progress_bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(progress_bg_surf, (*BG_DARK, 200), progress_bg_surf.get_rect(), border_radius=15)
            pygame.draw.rect(progress_bg_surf, (*WHITE, 30), progress_bg_surf.get_rect(), 2, border_radius=15)
            self.screen.blit(progress_bg_surf, progress_bg_rect)
            if progress > 0:
                progress_rect = pygame.Rect(60, 700, progress_width, 30)
                progress_surf = pygame.Surface((progress_width, 30), pygame.SRCALPHA)
                for x in range(int(progress_width)):
                    ratio = x / progress_width if progress_width > 0 else 0
                    r = int(SUCCESS_GREEN[0] * (1 - ratio) + PRIMARY_BLUE[0] * ratio)
                    g = int(SUCCESS_GREEN[1] * (1 - ratio) + PRIMARY_BLUE[1] * ratio)
                    b = int(SUCCESS_GREEN[2] * (1 - ratio) + PRIMARY_BLUE[2] * ratio)
                    pygame.draw.line(progress_surf, (r, g, b), (x, 0), (x, 30))
                self.screen.blit(progress_surf, progress_rect)
            progress_text = f"Progress: {self.correct_chars}/{self.total_chars} ({progress*100:.1f}%)"
            progress_surface = self.font_tiny.render(progress_text, True, WHITE)
            self.screen.blit(progress_surface, (60, 740))

    def draw_target_text(self, area: pygame.Rect):
        margin_x = 40
        margin_y = 40
        x0 = area.x + margin_x
        y0 = area.y + margin_y
        max_x = area.x + area.width - margin_x
        max_y = area.y + area.height - margin_y
        line_step = 70
        caret_index = min(len(self.typing_text), len(self.target_text))
        if self.render_start_index > caret_index:
            self.render_start_index = max(0, caret_index - 50)

        def simulate(start_idx: int):
            x = x0
            y = y0
            line_starts = [start_idx]
            caret_pos = None
            for abs_idx in range(start_idx, len(self.target_text)):
                ch = self.target_text[abs_idx]
                char_surface = self.font_medium.render(ch, True, WHITE)
                w = char_surface.get_width()
                if x + w > max_x:
                    x = x0
                    y += line_step
                    line_starts.append(abs_idx)
                    if y + self.font_medium.get_height() > max_y:
                        break
                if abs_idx == caret_index:
                    caret_pos = (x, y)
                x += w
                if y + self.font_medium.get_height() > max_y:
                    break
            return line_starts, caret_pos

        line_starts, caret_pos = simulate(self.render_start_index)
        if caret_pos is None or (caret_pos[1] + self.font_medium.get_height() > max_y):
            probe_start = max(0, caret_index - 200)
            self.render_start_index = probe_start
            for _ in range(12):
                ls, cp = simulate(self.render_start_index)
                if cp is None:
                    break
                if cp[1] + self.font_medium.get_height() <= max_y:
                    break
                if len(ls) >= 2:
                    self.render_start_index = ls[1]
                else:
                    self.render_start_index += 5
            line_starts, caret_pos = simulate(self.render_start_index)

        x = x0
        y = y0
        cursor_drawn = False
        for abs_idx in range(self.render_start_index, len(self.target_text)):
            ch = self.target_text[abs_idx]
            if abs_idx < len(self.typing_text):
                color = SUCCESS_GREEN if self.typing_text[abs_idx] == ch else ERROR_RED
            else:
                color = (100, 100, 100)
            char_surface = self.font_medium.render(ch, True, color)
            shadow_surface = self.font_medium.render(ch, True, (*BLACK, 80))
            w = char_surface.get_width()
            if x + w > max_x:
                x = x0
                y += line_step
                if y + self.font_medium.get_height() > max_y:
                    break
            self.screen.blit(shadow_surface, (x + 1, y + 1))
            self.screen.blit(char_surface, (x, y))
            if not cursor_drawn and abs_idx == caret_index and self.is_typing:
                cursor_time = time.time() * 2
                if int(cursor_time) % 2 == 0:
                    cursor_height = self.font_medium.get_height()
                    pygame.draw.line(self.screen, PRIMARY_BLUE, (x, y), (x, y + cursor_height), 3)
                cursor_drawn = True
            x += w
            if y + self.font_medium.get_height() > max_y:
                break
        if not cursor_drawn and self.is_typing:
            cursor_time = time.time() * 2
            if int(cursor_time) % 2 == 0:
                cursor_height = self.font_medium.get_height()
                pygame.draw.line(self.screen, PRIMARY_BLUE, (x0, y0), (x0, y0 + cursor_height), 3)

    def draw_results(self):
        if self.current_width != GAME_WIDTH or self.current_height != GAME_HEIGHT:
            self.resize_window(GAME_WIDTH, GAME_HEIGHT)
        self.draw_modern_background()
        self.draw_particles()

        panel_rect = pygame.Rect(80, 60, GAME_WIDTH - 160, GAME_HEIGHT - 120)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (*BG_MEDIUM, 220), panel_surf.get_rect(), border_radius=40)
        pygame.draw.rect(panel_surf, (*WHITE, 80), panel_surf.get_rect(), 6, border_radius=40)
        inner_rect = pygame.Rect(25, 25, panel_rect.width - 50, panel_rect.height - 50)
        pygame.draw.rect(panel_surf, (*BG_DARK, 80), inner_rect, border_radius=30)
        self.screen.blit(panel_surf, panel_rect)

        try:
            font_mono_large = pygame.font.SysFont("Consolas", 48)
            font_mono_medium = pygame.font.SysFont("Consolas", 32)
        except Exception:
            font_mono_large = pygame.font.Font(None, 48)
            font_mono_medium = pygame.font.Font(None, 32)

        title_text = " Typing Test Complete!"
        title_surface = font_mono_large.render(title_text, True, PRIMARY_BLUE)
        title_rect = title_surface.get_rect(center=(GAME_WIDTH // 2, 140))
        self.screen.blit(title_surface, title_rect)

        y_offset = 220
        results = [
            (f" Time: {self.elapsed_time:.2f} sec", PRIMARY_BLUE),
            (f" Characters: {self.correct_chars}/{self.total_chars}", SUCCESS_GREEN),
            (f" Accuracy: {self.accuracy:.1f}%", WARNING_ORANGE),
            (f" Speed: {self.wpm:.1f} WPM", ACCENT_BLUE),
        ]
        for result_text, color in results:
            result_surface = font_mono_medium.render(result_text, True, color)
            result_rect = result_surface.get_rect(center=(GAME_WIDTH // 2, y_offset))
            self.screen.blit(result_surface, result_rect)
            y_offset += 60

        feedback = self.get_performance_feedback()
        feedback_surface = font_mono_medium.render(feedback, True, SUCCESS_GREEN)
        feedback_rect = feedback_surface.get_rect(center=(GAME_WIDTH // 2, y_offset))
        self.screen.blit(feedback_surface, feedback_rect)

        mouse_pos = pygame.mouse.get_pos()
        self.play_again_button.update(mouse_pos)
        self.back_to_menu_button.update(mouse_pos)
        self.play_again_button.draw(self.screen)
        self.back_to_menu_button.draw(self.screen)

    def get_performance_feedback(self) -> str:
        if self.accuracy >= 95 and self.wpm >= 60:
            return " Outstanding! You're a typing master!"
        elif self.accuracy >= 85 and self.wpm >= 40:
            return " Excellent performance! Keep it up!"
        elif self.accuracy >= 70 and self.wpm >= 25:
            return " Good job! Room for improvement."
        else:
            return " Keep practicing! You'll get better!"

    def start_game(self, difficulty: str):
        self.difficulty = difficulty
        if difficulty == "Easy":
            self.n_gram = 2
            self.base_target_len = 6
            self.avg_word_len = 3.5
        elif difficulty == "Medium":
            self.n_gram = 3
            self.base_target_len = 8
            self.avg_word_len = 6.0
        elif difficulty == "Hard":
            self.n_gram = 4
            self.base_target_len = 10
            self.avg_word_len = 8.0
        try:
            random.seed()
            approx_chars_per_phrase = int(self.base_target_len * (self.avg_word_len + 1))
            min_chars = int(self.time_limit * 8)
            num_phrases = max(5, min(40, (min_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
            num_phrases += random.randint(-2, 2)
            num_phrases = max(3, min(50, num_phrases))
            self.ngrams_obj = Ngrams(corpus_file="corpora/corpora.pkl", n=self.n_gram, num_phrases=num_phrases, difficulty=self.difficulty.lower())
            test_phrases = self.ngrams_obj.generate_phrases()
            self.target_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
            if len(self.target_text) < min_chars:
                extra_needed = min_chars - len(self.target_text)
                extra_phrases = max(3, (extra_needed + approx_chars_per_phrase - 1) // approx_chars_per_phrase)
                tmp = Ngrams(corpus_file="corpora/corpora.pkl", n=self.n_gram, num_phrases=extra_phrases, difficulty=self.difficulty.lower())
                test_phrases += tmp.generate_phrases()
                self.target_text = " ".join(phrase for phrase in test_phrases if phrase.strip())
            self.total_chars = len(self.target_text)
            self.state = GAME
            self.typing_text = ""
            self.current_char_index = 0
            self.correct_chars = 0
            self.is_typing = False
            self.time_remaining = float(self.time_limit)
            self.render_start_index = 0
        except Exception as e:
            print(f"Error generating text: {e}")
            self.target_text = "The quick brown fox jumps over the lazy dog. This is a sample text for typing practice."
            self.total_chars = len(self.target_text)
            self.state = GAME

    def handle_typing(self, event):
        if event.key == pygame.K_BACKSPACE:
            if self.typing_text:
                self.typing_text = self.typing_text[:-1]
                self.correct_chars = 0
                for i in range(len(self.typing_text)):
                    if i < len(self.target_text) and self.typing_text[i] == self.target_text[i]:
                        self.correct_chars += 1
        elif event.key == pygame.K_RETURN:
            pass
        else:
            if not self.is_typing:
                self.is_typing = True
                self.start_time = time.time()
            char = event.unicode
            if char.isprintable():
                self.typing_text += char
                if len(self.typing_text) <= len(self.target_text):
                    if char == self.target_text[len(self.typing_text) - 1]:
                        self.correct_chars += 1
                        self.create_particles(GAME_WIDTH // 2, GAME_HEIGHT // 2, SUCCESS_GREEN, 8)
                    else:
                        self.create_particles(GAME_WIDTH // 2, GAME_HEIGHT // 2, ERROR_RED, 5)
                remaining_chars = len(self.target_text) - len(self.typing_text)
                if self.is_typing and self.time_remaining > 0.2 and remaining_chars < 150:
                    self.refill_target_text()
                if len(self.typing_text) >= len(self.target_text):
                    if self.is_typing and self.time_remaining > 0.2:
                        self.refill_target_text()
                    else:
                        self.end_game()

    def refill_target_text(self):
        try:
            random.seed()
            approx_chars_per_phrase = int(self.base_target_len * (self.avg_word_len + 1)) or 20
            needed_chars = max(200, int(self.time_remaining * 8))
            extra_phrases = max(3, min(40, (needed_chars + approx_chars_per_phrase - 1) // approx_chars_per_phrase))
            extra_phrases += random.randint(-1, 2)
            extra_phrases = max(2, min(50, extra_phrases))
            generator = Ngrams(corpus_file="corpora/corpora.pkl", n=self.n_gram, num_phrases=extra_phrases, difficulty=self.difficulty.lower())
            more_phrases = generator.generate_phrases()
            extra_text = " ".join(p for p in more_phrases if p.strip())
            if extra_text:
                if self.target_text and not self.target_text.endswith(" "):
                    self.target_text += " "
                self.target_text += extra_text
                self.total_chars = len(self.target_text)
        except Exception:
            fallback = " keep typing to improve your speed and accuracy."
            self.target_text += fallback
            self.total_chars = len(self.target_text)

    def end_game(self):
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.elapsed_time = min(elapsed, float(self.time_limit))
        else:
            self.elapsed_time = float(self.time_limit)
        elapsed_minutes = self.elapsed_time / 60
        if elapsed_minutes > 0:
            self.wpm = (self.correct_chars / 5) / elapsed_minutes
        else:
            self.wpm = 0
        typed_chars = len(self.typing_text)
        if typed_chars > 0:
            self.accuracy = (self.correct_chars / typed_chars) * 100
            
            # Save progress data
            try:
                from progress_tracker.tracker import save_typing_result
                save_typing_result(
                    wpm=self.wpm,
                    accuracy=self.accuracy,
                    characters_typed=self.correct_chars,  # Correctly typed characters (matches display)
                    total_characters=self.total_chars,    # Total available characters in test
                    time_taken=self.elapsed_time,
                    difficulty=self.difficulty.lower(),
                    n_gram_order=self.n_gram,
                    test_duration=self.time_limit
                )
            except Exception as e:
                print(f"Could not save progress: {e}")
        else:
            self.accuracy = 0
        self.state = RESULTS

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.state == GAME:
                        self.handle_typing(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == MENU:
                        if self.easy_button.is_clicked(event):
                            self.start_game("Easy")
                        elif self.medium_button.is_clicked(event):
                            self.start_game("Medium")
                        elif self.hard_button.is_clicked(event):
                            self.start_game("Hard")
                        elif self.custom_button.is_clicked(event):
                            if self.time_limit == 15:
                                self.time_limit = 30
                            elif self.time_limit == 30:
                                self.time_limit = 60
                            elif self.time_limit == 60:
                                self.time_limit = 120
                            else:
                                self.time_limit = 15
                            self.custom_button.text = f"Time: {self.time_limit}s"
                        elif self.exit_button.is_clicked(event):
                            running = False
                    elif self.state == GAME:
                        if self.restart_button.is_clicked(event):
                            self.start_game(self.difficulty)
                        elif self.menu_button.is_clicked(event):
                            self.state = MENU
                    elif self.state == RESULTS:
                        if self.play_again_button.is_clicked(event):
                            self.start_game(self.difficulty)
                        elif self.back_to_menu_button.is_clicked(event):
                            self.state = MENU
            self.update_particles()
            if self.state == MENU:
                self.draw_menu()
            elif self.state == GAME:
                self.draw_game()
            elif self.state == RESULTS:
                self.draw_results()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


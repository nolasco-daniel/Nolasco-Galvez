from typing import Tuple

import pygame

from .constants import (
    BLACK,
    WHITE,
    PURE_WHITE,
)


class ModernButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int], hover_color: Tuple[int, int, int],
                 icon: str = "", font_size: int = 32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.icon = icon
        self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.animation_time = 0
        self.scale = 1.0
        self.target_scale = 1.0
        self.glow_intensity = 0
        self.pressed = False

    def update(self, mouse_pos: Tuple[int, int]):
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and not was_hovered:
            self.target_scale = 1.02
            self.glow_intensity = 1.0
        elif not self.hovered and was_hovered:
            self.target_scale = 1.0
            self.glow_intensity = 0.0
        self.scale += (self.target_scale - self.scale) * 0.15
        if self.hovered:
            self.glow_intensity += (1.0 - self.glow_intensity) * 0.1
        else:
            self.glow_intensity += (0.0 - self.glow_intensity) * 0.1
        self.current_color = self.hover_color if self.hovered else self.color
        if self.hovered:
            self.animation_time += 0.1
        else:
            self.animation_time = 0

    def draw(self, screen: pygame.Surface):
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        if self.glow_intensity > 0:
            glow_rect = scaled_rect.inflate(20, 20)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_alpha = int(50 * self.glow_intensity)
            pygame.draw.rect(glow_surf, (*self.current_color, glow_alpha), glow_surf.get_rect(), border_radius=18)
            screen.blit(glow_surf, glow_rect)
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (*BLACK, 40), shadow_surf.get_rect(), border_radius=18)
        screen.blit(shadow_surf, shadow_rect)
        gradient_surf = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        for y in range(scaled_rect.height):
            ratio = y / scaled_rect.height
            r = int(self.current_color[0] * (1 - ratio * 0.3) + self.hover_color[0] * (ratio * 0.3))
            g = int(self.current_color[1] * (1 - ratio * 0.3) + self.hover_color[1] * (ratio * 0.3))
            b = int(self.current_color[2] * (1 - ratio * 0.3) + self.hover_color[2] * (ratio * 0.3))
            pygame.draw.line(gradient_surf, (r, g, b), (0, y), (scaled_rect.width, y))
        screen.blit(gradient_surf, scaled_rect)
        border_color = tuple(min(255, c + int(20 * self.glow_intensity)) for c in self.current_color)
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=18)
        highlight_rect = scaled_rect.copy()
        highlight_rect.height = highlight_rect.height // 2
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (*WHITE, 25), highlight_surf.get_rect(), border_radius=18)
        screen.blit(highlight_surf, highlight_rect)
        display_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surface = self.font.render(display_text, True, WHITE)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_surface = self.font.render(display_text, True, (*BLACK, 100))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event) -> bool:
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class OutlineButton:
    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 border_color: Tuple[int, int, int], font_size: int = 32):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.border_color = border_color
        try:
            self.font = pygame.font.SysFont("Consolas", font_size)
        except Exception:
            self.font = pygame.font.Font(None, font_size)
        self.hovered = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.hover_glow = 0.0
        self.click_flash = 0.0
        self.glow_intensity = 0.0

    def _lighten(self, color: Tuple[int, int, int], amount: float) -> Tuple[int, int, int]:
        r, g, b = color
        return (
            min(255, int(r + (255 - r) * amount)),
            min(255, int(g + (255 - g) * amount)),
            min(255, int(b + (255 - b) * amount)),
        )

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)
        if self.hovered and not was_hovered:
            self.target_scale = 1.02
            self.glow_intensity = 1.0
        elif not self.hovered and was_hovered:
            self.target_scale = 1.0
            self.glow_intensity = 0.0
        self.scale += (self.target_scale - self.scale) * 0.15
        target_hover = 0.25 if self.hovered else 0.0
        self.hover_glow += (target_hover - self.hover_glow) * 0.12
        self.click_flash = max(0.0, self.click_flash - 0.06)
        if self.hovered:
            self.glow_intensity += (1.0 - self.glow_intensity) * 0.1
        else:
            self.glow_intensity += (0.0 - self.glow_intensity) * 0.1

    def draw(self, screen: pygame.Surface) -> None:
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)
        
        # Glass effect glow (same as ModernButton)
        if self.glow_intensity > 0:
            glow_rect = scaled_rect.inflate(20, 20)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            glow_alpha = int(50 * self.glow_intensity)
            pygame.draw.rect(glow_surf, (*self.border_color, glow_alpha), glow_surf.get_rect(), border_radius=18)
            screen.blit(glow_surf, glow_rect)
        
        # Shadow effect
        shadow_rect = scaled_rect.copy()
        shadow_rect.x += 6
        shadow_rect.y += 6
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (*BLACK, 40), shadow_surf.get_rect(), border_radius=18)
        screen.blit(shadow_surf, shadow_rect)
        
        # Gradient fill (glass effect)
        gradient_surf = pygame.Surface((scaled_rect.width, scaled_rect.height), pygame.SRCALPHA)
        for y in range(scaled_rect.height):
            ratio = y / scaled_rect.height
            r = int(self.border_color[0] * (1 - ratio * 0.3) + self._lighten(self.border_color, 0.3)[0] * (ratio * 0.3))
            g = int(self.border_color[1] * (1 - ratio * 0.3) + self._lighten(self.border_color, 0.3)[1] * (ratio * 0.3))
            b = int(self.border_color[2] * (1 - ratio * 0.3) + self._lighten(self.border_color, 0.3)[2] * (ratio * 0.3))
            pygame.draw.line(gradient_surf, (r, g, b), (0, y), (scaled_rect.width, y))
        screen.blit(gradient_surf, scaled_rect)
        
        # Border with glow intensity
        border_color = tuple(min(255, c + int(20 * self.glow_intensity)) for c in self.border_color)
        pygame.draw.rect(screen, border_color, scaled_rect, 2, border_radius=18)
        
        # Highlight effect (glass shine)
        highlight_rect = scaled_rect.copy()
        highlight_rect.height = highlight_rect.height // 2
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (*WHITE, 25), highlight_surf.get_rect(), border_radius=18)
        screen.blit(highlight_surf, highlight_rect)
        
        # Text with shadow
        text_surface = self.font.render(self.text, True, PURE_WHITE)
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        shadow_surface = self.font.render(self.text, True, (*BLACK, 100))
        shadow_rect = shadow_surface.get_rect(center=(text_rect.centerx + 1, text_rect.centery + 1))
        screen.blit(shadow_surface, shadow_rect)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.click_flash = 0.6
            return True
        return False



import random
import math
from typing import Tuple

import pygame


class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], velocity: Tuple[float, float]):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 1.0
        self.decay = random.uniform(0.015, 0.035)
        self.size = random.randint(2, 6)
        self.original_size = self.size
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-3, 3)
        self.alpha = 255

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.12
        self.life -= self.decay
        self.size = max(0, self.original_size * self.life)
        self.rotation += self.rotation_speed
        self.alpha = int(255 * self.life)
        self.vx += random.uniform(-0.05, 0.05)

    def draw(self, screen: pygame.Surface) -> None:
        if self.life <= 0:
            return
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        points = []
        for i in range(4):
            angle = (i * 90 + self.rotation) * math.pi / 180
            radius = self.size
            x = self.size + radius * math.cos(angle)
            y = self.size + radius * math.sin(angle)
            points.append((x, y))
        if len(points) >= 3:
            pygame.draw.polygon(surf, self.color, points)
            surf.set_alpha(self.alpha)
        screen.blit(surf, (self.x - self.size, self.y - self.size))



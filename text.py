import enum

import pygame
import logging


class Text(pygame.sprite.Sprite):
    def __init__(self, text, font_name: str, color, size: int, center, bold=False, italic=False):
        super(Text, self).__init__()
        font = pygame.font.SysFont(font_name, size, bold, italic)
        self.image = font.render(text, True, color)
        text_center = pygame.math.Vector2(self.image.get_width() / 2, self.image.get_height() / 2)
        self.rect = self.image.get_rect(center=center)
        self.state = TextState.NEW

        self.acc = None
        self.outro_frames = 0
        self.since_frames = 0
        self.end_frames = 0

    def fadeDown(self, frames, rate):
        self.acc = pygame.math.Vector2(0, rate)
        self.end_frames = frames
        self.state = TextState.FADING

    def update(self):
        self.since_frames += 1
        if self.acc is not None:
            self.rect.center = self.rect.center + self.acc
            if self.state == TextState.FADING:
                self.outro_frames += 1
            if self.state == TextState.DYING:
                self.outro_frames += 1
        else:
            logging.info("No acc yet")

        logging.info("since_frames: {}\toutro_frames: {}\tend_frames: {}".format(self.since_frames, self.outro_frames, self.end_frames))
        if self.outro_frames > self.end_frames:
            self.state = TextState.DEAD

    def isDead(self):
        return self.state == TextState.DEAD


class TextState(enum.Enum):
    NEW = 1
    DEAD = 2
    FADING = 4
    DYING = 9

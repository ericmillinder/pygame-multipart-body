import pygame.draw

from screen import *


class YSortCameraGroup(pygame.sprite.Group):
    """
    This sprite group functions as a camera
    The sprites are rendered in order of self.sprites()
    The sprite.image and sprite.rect are used to blit the image.
    """

    def __init__(self):
        super().__init__()
        self.half_width = WIDTH // 2
        self.half_height = HEIGHT // 2
        self.offset = pygame.math.Vector2(0, 0)

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_width
        self.offset.y = target.rect.centery - self.half_height

    def draw(self, surface: pygame.Surface):
        # self.display_surface = pygame.display.get_surface()
        y_sorted_sprites = sorted(self.sprites(), key=lambda sprite: sprite.pos.y)
        for sprite in y_sorted_sprites:
            if hasattr(sprite, "draw"):
                sprite.draw(surface)
            else:
                offset_pos = sprite.rect.topleft - self.offset
                surface.blit(sprite.image, offset_pos)

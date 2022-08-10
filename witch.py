from typing import Any

from pygame.locals import *
import pygame
import logging
from pygame.math import Vector2

from pygame.sprite import AbstractGroup

import constants
import screen
from spritesheet import SpriteSheet
import random

RIGHT = 0
LEFT = 1


class Witch(pygame.sprite.Sprite):
    MAX_ARM_SWING_BACK = -35
    MAX_ARM_SWING_FORTH = 35

    def __init__(self, position=None):
        super().__init__()
        self.sheet = SpriteSheet("assets/images/witch.png")
        self.head = self.sheet.image_at((0, 0, 237, 237))
        self.blink = self.sheet.image_at((239, 227, 79, 37))
        self.hair = pygame.transform.rotate(self.sheet.image_at((241, 3, 90, 66)), -90)
        self.shirt = self.sheet.image_at((250, 75, 70, 55))
        self.skirt = self.sheet.image_at((3, 237, 120, 100))
        self.foot_l = self.sheet.image_at((240, 265, 40, 35))
        self.foot_r = self.sheet.image_at((282, 265, 40, 35))
        self.arm_r = self.sheet.image_at((254, 131, 64, 92))
        self.arm_r_drawn = None
        self.arm_l = pygame.transform.rotozoom(self.sheet.image_at((128, 238, 102, 72)), -90, 0.9)
        self.arm_l_drawn = None

        # all rects start at 0,0
        self.head_rect = self.head.get_rect().move(10, 0)
        self.blink_rect = self.blink.get_rect().move(108, 154)
        self.hair_rect = self.hair.get_rect().move(141, 130)
        self.shirt_rect = self.shirt.get_rect().move(110, self.head_rect.bottomleft[1] - 40)
        self.skirt_rect = self.skirt.get_rect().move(77, self.shirt_rect.bottomleft[1] - 15)
        self.foot_l_rect = self.foot_l.get_rect().move(110, self.skirt_rect.bottomleft[1] - 20)
        self.foot_r_rect = self.foot_r.get_rect().move(150, self.skirt_rect.bottomleft[1] - 27)
        self.arm_r_rect = self.arm_r.get_rect()
        self.arm_r_rect.center = self.shirt_rect.move(10, 25).topleft
        self.arm_r_drawn_rect = None
        self.arm_l_rect = self.arm_l.get_rect()
        self.arm_l_rect.center = self.shirt_rect.move(30, 14).topleft
        self.arm_l_drawn_rect = None

        if position == None:
            self.pos = Vector2(100, 100)  # Will eventually be the top-left offset for the entire group
        else:
            self.pos = Vector2(position)
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.directionFacing = RIGHT
        self.head_acc = Vector2(0, 0)
        self.arm_r_acc = Vector2(random.randint(Witch.MAX_ARM_SWING_BACK, Witch.MAX_ARM_SWING_FORTH),
                                 1)  # current angle, rate of change

        self.sinceLastBlink = 0
        self.blinking = False

    def draw(self, surface: pygame.Surface):
        """the sooner drawn, the lower the layer"""
        h = 380
        w = 250
        totalSize = Rect((0, 0, w, h))
        tmpSurface = pygame.Surface(totalSize.size).convert_alpha()
        # pygame.draw.rect(tmpSurface, "red", totalSize, 2)
        for i in range(len(self.sprites)):
            tmpSurface.blit(self.sprites[i], self.rects[i])
        if self.blinking:
            tmpSurface.blit(self.blink, self.blink_rect)

        if self.directionFacing == LEFT:
            tmpSurface = pygame.transform.flip(tmpSurface, True, False)

        tmpSurface = pygame.transform.scale(tmpSurface, (w * screen.SCALE, h * screen.SCALE))
        surface.blit(tmpSurface, tmpSurface.get_rect().move(self.pos))

    def add(self, *groups: AbstractGroup) -> None:
        super().add(*groups)

    def update(self):
        self.sinceLastBlink += 1
        if self == screen.active_player:
            self.move()
        self.animate()
        self.sprites = [self.foot_l, self.foot_r, self.arm_l_drawn, self.hair, self.shirt, self.skirt, self.head,
                        self.arm_r_drawn]
        self.rects = [self.foot_l_rect, self.foot_r_rect, self.arm_l_drawn_rect, self.hair_rect, self.shirt_rect,
                      self.skirt_rect, self.head_rect, self.arm_r_drawn_rect]

    def move(self):
        self.acc = Vector2(0, 0)

        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[K_LEFT]:
            self.acc.x = -constants.ACC
            self.directionFacing = LEFT
        if pressed_keys[K_RIGHT]:
            self.acc.x = constants.ACC
            self.directionFacing = RIGHT
        if pressed_keys[K_UP]:
            self.acc.y = -constants.ACC
        if pressed_keys[K_DOWN]:
            self.acc.y = constants.ACC

        self.acc += self.vel * constants.FRIC
        self.vel += self.acc
        self.pos += self.vel + constants.ACC * self.acc

        if self.pos.x > screen.WIDTH:
            self.pos.x = screen.WIDTH
        if self.pos.x < 0:
            self.pos.x = 0

    def animate(self):
        if self.head_rect.top >= 10:
            self.head_acc = Vector2(0, -1)
        elif self.head_rect.top <= 0:
            self.head_acc = Vector2(0, 1)
        self.head_rect.move_ip(self.head_acc)
        self.blink_rect.move_ip(self.head_acc)
        self.hair_rect.move_ip(self.head_acc)
        self.foot_l_rect.move_ip(self.head_acc.rotate(-180))
        self.foot_r_rect.move_ip(self.head_acc)

        if self.arm_r_acc.x <= self.MAX_ARM_SWING_BACK:
            self.arm_r_acc.y = 1
        elif self.arm_r_acc.x > self.MAX_ARM_SWING_FORTH:
            self.arm_r_acc.y = -1
        # TODO figure out how the rotation works when facing the other direction..
        #   it seems like it would be max - current angle
        # if self.directionFacing == LEFT:
        #     self.arm_r_acc.x = self.MA
        self.arm_r_acc.x += self.arm_r_acc.y

        angle = self.arm_r_acc.x
        pivot = self.arm_r_rect.center
        offset = Vector2(-10, 40)
        # logging.info("Rotating arm at {} by {}, {}, {}".format((self.arm_r_rect), angle, pivot, offset))
        self.arm_r_drawn, self.arm_r_drawn_rect = self.rotate(self.arm_r, angle, pivot, offset)
        # self.arm_r_rect = self.arm_r.get_bounding_rect()

        self.arm_l_drawn, self.arm_l_drawn_rect = \
            self.rotate(self.arm_l, -angle, self.arm_l_rect.center, Vector2(0, self.arm_l_rect.height / 2))

        if self.sinceLastBlink > 300:
            self.blinking = True
        if self.sinceLastBlink > 360:
            self.sinceLastBlink = 0
            self.blinking = False

    def rotate(self, surface, angle, pivot, offset: Vector2):
        """Rotate the surface around the pivot point.

        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
        rotated_image = pygame.transform.rotate(surface, -angle)  # Rotate the image.
        rotated_offset = offset.rotate(angle)  # Rotate the offset vector.
        # Add the offset vector to the center/pivot point to shift the rect.
        rect = rotated_image.get_rect(center=pivot + rotated_offset)
        return rotated_image, rect  # Return the rotated image and shifted rect.

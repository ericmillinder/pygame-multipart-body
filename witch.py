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
        self.hair_rect = self.hair.get_rect().move(141, 130)
        self.shirt_rect = self.shirt.get_rect().move(110, self.head_rect.bottomleft[1] - 40)
        self.skirt_rect = self.skirt.get_rect().move(77, self.shirt_rect.bottomleft[1] - 15)
        self.foot_l_rect = self.foot_l.get_rect().move(110, self.skirt_rect.bottomleft[1] - 20)
        self.foot_r_rect = self.foot_r.get_rect().move(150, self.skirt_rect.bottomleft[1] - 27)
        self.arm_r_rect = self.arm_r.get_rect()
        self.arm_r_rect.center = self.shirt_rect.move(10, 13).topleft
        self.arm_r_drawn_rect = None
        self.arm_l_rect = self.arm_l.get_rect()
        self.arm_l_rect.center = self.shirt_rect.move(30, 14).topleft
        self.arm_l_drawn_rect = None

        if position == None:
            self.pos = Vector2(100, 100)  # Will eventually be the top-left offset for the entire group
        else:
            self.pos = position
        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.directionFacing = RIGHT
        self.head_acc = Vector2(0, 0)
        self.arm_r_acc = Vector2(random.randint(Witch.MAX_ARM_SWING_BACK, Witch.MAX_ARM_SWING_FORTH), 1)  # current angle, rate of change

    def draw(self, surface: pygame.Surface):
        """the sooner drawn, the lower the layer"""
        # logging.debug("Drawing at {}".format(self.pos))
        surface.blit(self.foot_l, self.foot_l_rect.move(self.pos))
        surface.blit(self.foot_r, self.foot_r_rect.move(self.pos))

        surface.blit(self.arm_l_drawn, self.arm_l_drawn_rect.move(self.pos))
        surface.blit(self.hair, self.hair_rect.move(self.pos))
        surface.blit(self.shirt, self.shirt_rect.move(self.pos))
        surface.blit(self.skirt, self.skirt_rect.move(self.pos))

        surface.blit(self.head, self.head_rect.move(self.pos))

        surface.blit(self.arm_r_drawn, self.arm_r_drawn_rect.move(self.pos))
        # pygame.draw.rect(surface, (200, 200, 200), self.arm_r_drawn_rect, 2)

    def add(self, *groups: AbstractGroup) -> None:
        super().add(*groups)

    def update(self):
        if self == screen.active_player:
            self.move()
        self.animate()

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
        self.hair_rect.move_ip(self.head_acc)
        self.foot_l_rect.move_ip(self.head_acc.rotate(-180))
        self.foot_r_rect.move_ip(self.head_acc)

        if self.arm_r_acc.x <= Witch.MAX_ARM_SWING_BACK:
            self.arm_r_acc.y = 1
        elif self.arm_r_acc.x > Witch.MAX_ARM_SWING_FORTH:
            self.arm_r_acc.y = -1
        self.arm_r_acc.x += self.arm_r_acc.y

        angle = self.arm_r_acc.x
        pivot = self.arm_r_rect.center
        offset = Vector2(-10, self.arm_r_rect.height / 2)
        # logging.info("Rotating arm at {} by {}, {}, {}".format((self.arm_r_rect), angle, pivot, offset))
        self.arm_r_drawn, self.arm_r_drawn_rect = self.rotate(self.arm_r, angle, pivot, offset)
        # self.arm_r_rect = self.arm_r.get_bounding_rect()

        self.arm_l_drawn, self.arm_l_drawn_rect = \
            self.rotate(self.arm_l, -angle, self.arm_l_rect.center, Vector2(0, self.arm_l_rect.height / 2))

        # self.head_rect.move_ip()

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

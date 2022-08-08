from typing import Any

from pygame.locals import *
import pygame
import logging
from pygame.math import Vector2

from pygame.sprite import AbstractGroup

import constants
import screen
from spritesheet import SpriteSheet

RIGHT = 0
LEFT = 1


class Wizard(pygame.sprite.Sprite):

    def __init__(self, position=None):
        super().__init__()
        self.sheet = SpriteSheet("assets/images/wizard.png")
        self.head = self.sheet.image_at(((0, 0), (150, 220)))
        self.hat_point = self.sheet.image_at((0, 220, 110, 90))
        self.hair = self.sheet.image_at((5, 438, 52, 67))
        self.body = self.sheet.image_at(((150, 0), (150, 140)))
        self.foot_l = self.sheet.image_at((153, 148, 45, 38))
        self.foot_r = self.sheet.image_at((200, 148, 45, 35))
        self.arm_r = self.sheet.image_at((0, 310, 110, 125))
        self.arm_r_drawn = None
        self.arm_l = pygame.transform.rotate(self.sheet.image_at((60, 435, 100, 80)), -90)
        self.arm_l_drawn = None

        self.head_rect = self.head.get_rect().move(12, 20)
        self.hat_point_rect = self.hat_point.get_rect().move(-25, 35)
        self.hair_rect = self.body.get_rect().move(33, 160)
        self.body_rect = self.body.get_rect().move(10, 190)
        self.foot_l_rect = self.foot_l.get_rect().move(40, 305)
        self.foot_r_rect = self.foot_r.get_rect().move(90, 309)
        self.arm_r_rect = self.arm_r.get_rect().move(15, 135)
        self.arm_r_drawn_rect = None
        self.arm_l_rect = self.arm_l.get_rect().move(40, 155)
        self.arm_l_drawn_rect = None

        if position == None:
            self.pos = Vector2(100, 100)  # Will eventually be the top-left offset for the entire group
        else:
            self.pos = position

        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.directionFacing = RIGHT
        self.head_acc = Vector2(0, 0)
        self.arm_r_acc = Vector2(0, 1)  # current angle, rate of change

    def draw(self, surface: pygame.Surface):
        """Attempting to draw all the parts here as an alternative to this being a Group
        or having to have image and rect attributes
        """
        # logging.debug("Drawing at {}".format(self.pos))

        surface.blit(self.foot_l, self.foot_l_rect.move(self.pos))
        surface.blit(self.foot_r, self.foot_r_rect.move(self.pos))

        surface.blit(self.arm_l_drawn, self.arm_l_drawn_rect.move(self.pos))
        surface.blit(self.hair, self.hair_rect.move(self.pos))
        surface.blit(self.body, self.body_rect.move(self.pos))

        surface.blit(self.hat_point, self.hat_point_rect.move(self.pos))
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
        if self.head_rect.top >= 20:
            self.head_acc = Vector2(0, -1)
        elif self.head_rect.top <= 5:
            self.head_acc = Vector2(0, 1)
        self.head_rect.move_ip(self.head_acc)
        self.hat_point_rect.move_ip(self.head_acc)
        self.hair_rect.move_ip(self.head_acc)

        self.foot_l_rect.move_ip(self.head_acc.rotate(-180))
        self.foot_r_rect.move_ip(self.head_acc)

        if self.arm_r_acc.x <= -25:
            self.arm_r_acc.y = 1
        elif self.arm_r_acc.x > 35:
            self.arm_r_acc.y = -1
        self.arm_r_acc.x += self.arm_r_acc.y

        angle = self.arm_r_acc.x
        pivot = self.arm_r_rect.center
        offset = Vector2(0, self.arm_r_rect.height / 2)
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

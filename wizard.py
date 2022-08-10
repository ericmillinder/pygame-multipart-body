import random
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
    MAX_ARM_SWING_BACK = -65
    MAX_ARM_SWING_FORTH = 65
    BLINK_RATE = 240  # 240 / 60 fps ~ blink every 4 seconds?
    BLINK_DURATION = 40

    def __init__(self, position=None):
        super().__init__()
        self.sheet = SpriteSheet("assets/images/wizard.png")
        self.head = self.sheet.image_at(((0, 0), (150, 220)))
        self.blink = self.sheet.image_at((153, 187, 70, 43))
        self.hat_point = self.sheet.image_at((0, 220, 110, 90))
        self.hair = self.sheet.image_at((5, 438, 52, 67))
        self.body = self.sheet.image_at(((150, 0), (150, 140)))
        self.foot_l = self.sheet.image_at((153, 148, 45, 38))
        self.foot_r = self.sheet.image_at((200, 148, 45, 35))
        self.arm_r = self.sheet.image_at((0, 310, 110, 125))
        self.arm_r_drawn = None
        self.arm_l = pygame.transform.rotate(self.sheet.image_at((60, 440, 93, 68)), -90)
        self.arm_l_drawn = None

        self.head_rect = self.head.get_rect().move(38, 20)
        self.blink_rect = self.blink.get_rect().move(100, 130)
        self.hat_point_rect = self.hat_point.get_rect().move(-5, 35)
        self.hair_rect = self.body.get_rect().move(53, 160)
        self.body_rect = self.body.get_rect().move(30, 190)
        self.foot_l_rect = self.foot_l.get_rect().move(60, 305)
        self.foot_r_rect = self.foot_r.get_rect().move(110, 309)
        self.arm_r_rect = self.arm_r.get_rect().move(34, 150)
        self.arm_r_drawn_rect = None
        self.arm_l_rect = self.arm_l.get_rect().move(85, 165)
        self.arm_l_drawn_rect = None

        if position == None:
            self.pos = Vector2(100, 100)  # Will eventually be the top-left offset for the entire group
        else:
            self.pos = position

        self.vel = Vector2(0, 0)
        self.acc = Vector2(0, 0)

        self.sinceLastBlink = random.randint(0, Wizard.BLINK_RATE)
        self.blinking = False

        self.directionFacing = RIGHT
        self.head_acc = Vector2(0, 0)
        self.arm_r_acc = Vector2(0, 1)  # current angle, rate of change

        self.weapon = RedWizardStaff()
        self.weapon.rotate(-90)
        # self.weapon.rect.move_ip(-150, -25)
        self.weapon_drawn_rect = None
        self.weapon_drawn = None

    def draw(self, surface: pygame.Surface):
        """Moved on to bliting to a temp surface for left, right facing"""
        # logging.debug("Drawing at {}".format(self.pos))
        w = 300
        h = 372
        totalSize = Rect((0, 0, w, h))
        tmpSurface = pygame.Surface(totalSize.size).convert_alpha()

        tmpSurface.blit(self.foot_l, self.foot_l_rect)
        tmpSurface.blit(self.foot_r, self.foot_r_rect)

        tmpSurface.blit(self.hat_point, self.hat_point_rect)
        pygame.draw.circle(tmpSurface, "green", self.arm_l_rect.center, 3)
        pygame.draw.circle(tmpSurface, "blue", self.weapon_drawn_rect.center, 3)
        pygame.draw.rect(tmpSurface, (200, 200, 200), totalSize, 1)

        if self.directionFacing == RIGHT:
            # Needs arm/shoulder offsets
            tmpSurface.blit(self.weapon_drawn, self.weapon_drawn_rect)
            tmpSurface.blit(self.arm_l_drawn, self.arm_l_drawn_rect)
            tmpSurface.blit(self.hair, self.hair_rect)
            tmpSurface.blit(self.body, self.body_rect)

            tmpSurface.blit(self.head, self.head_rect)
            tmpSurface.blit(self.arm_r_drawn, self.arm_r_drawn_rect)
            pygame.draw.circle(tmpSurface, "green", self.arm_r_rect.center, 3)
            pygame.draw.circle(tmpSurface, "blue", self.arm_r_drawn_rect.center, 3)
        else:
            tmpSurface.blit(self.arm_r_drawn, self.arm_r_drawn_rect)
            pygame.draw.circle(tmpSurface, "green", self.arm_r_rect.center, 3)
            pygame.draw.circle(tmpSurface, "blue", self.arm_r_drawn_rect.center, 3)
            tmpSurface.blit(self.hair, self.hair_rect)
            tmpSurface.blit(self.body, self.body_rect)
            tmpSurface.blit(self.head, self.head_rect)
            tmpSurface.blit(self.arm_l_drawn, self.arm_l_drawn_rect)
            pygame.draw.circle(tmpSurface, "green", self.arm_l_rect.center, 3)
            pygame.draw.circle(tmpSurface, "blue", self.arm_l_drawn_rect.center, 3)
            tmpSurface.blit(self.weapon_drawn, self.weapon_drawn_rect)

        if self.blinking:
            tmpSurface.blit(self.blink, self.blink_rect)

        if self.directionFacing == LEFT:
            tmpSurface = pygame.transform.flip(tmpSurface, True, False)

        tmpSurface = pygame.transform.scale(tmpSurface, (w * screen.SCALE, h * screen.SCALE))
        surface.blit(tmpSurface, tmpSurface.get_rect().move(self.pos))
        surface.scroll()

    def add(self, *groups: AbstractGroup) -> None:
        super().add(*groups)

    def update(self):
        self.sinceLastBlink += 1
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
        self.blink_rect.move_ip(self.head_acc)
        self.hat_point_rect.move_ip(self.head_acc)
        self.hair_rect.move_ip(self.head_acc)

        self.foot_l_rect.move_ip(self.head_acc.rotate(-180))
        self.foot_r_rect.move_ip(self.head_acc)

        if self.arm_r_acc.x <= self.MAX_ARM_SWING_BACK:
            self.arm_r_acc.y = 1
        elif self.arm_r_acc.x > self.MAX_ARM_SWING_FORTH:
            self.arm_r_acc.y = -1
        self.arm_r_acc.x += self.arm_r_acc.y

        angle = self.arm_r_acc.x
        self.arm_r_drawn, self.arm_r_drawn_rect = \
            self.rotate(self.arm_r, angle, self.arm_r_rect.center, Vector2(-10, 50))

        self.arm_l_drawn, self.arm_l_drawn_rect = \
            self.rotate(self.arm_l, -35-angle, self.arm_l_rect.center, Vector2(-20, 40))

        self.weapon_drawn, self.weapon_drawn_rect = \
            self.rotate(self.weapon.image, -35-angle, self.arm_l_rect.center, Vector2(35, 85))

        if self.sinceLastBlink > self.BLINK_RATE:
            self.blinking = True
        if self.sinceLastBlink > self.BLINK_RATE + self.BLINK_DURATION:
            self.blinking = False
            self.sinceLastBlink = 0

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


class WizardStaff:
    def __init__(self, position=None):
        super().__init__()
        sheet = SpriteSheet("assets/images/wizard.png")
        self.wood = sheet.image_at((10, 241, 70, 265))


class WoodenWizardStaff(pygame.sprite.Sprite):

    def __init__(self, position=None):
        super().__init__()
        sheet = SpriteSheet("assets/images/staff_wizard.png")
        self.image = sheet.image_at((10, 241, 70, 265))
        self.rect = self.image.get_rect()


class RedWizardStaff(pygame.sprite.Sprite):

    def __init__(self, position=None):
        super().__init__()
        sheet = SpriteSheet("assets/images/staff_wizard.png")
        self.image = sheet.image_at((305, 215, 100, 295))
        self.rect = self.image.get_rect()

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()

import math
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
    MAX_ARM_SWING_FORTH = 35
    BLINK_RATE = 240  # 240 / 60 fps ~ blink every 4 seconds?
    BLINK_DURATION = 40

    w = 350
    h = 372

    def __init__(self, position=None):
        super().__init__()
        self.sheet = SpriteSheet("assets/images/wizard.png")
        self.head = self.sheet.image_at((0, 0, 150, 220))
        self.blink = self.sheet.image_at((153, 187, 70, 43))
        self.hat_point = self.sheet.image_at((0, 220, 110, 90))
        self.hair = self.sheet.image_at((5, 438, 52, 67))
        self.body = self.sheet.image_at((150, 0, 150, 140))
        self.foot_l = self.sheet.image_at((153, 148, 45, 38))
        self.foot_r = self.sheet.image_at((200, 148, 45, 35))
        self.arm_r = self.sheet.image_at((0, 310, 110, 125))
        self.arm_r_drawn = None
        self.arm_l = pygame.transform.rotate(self.sheet.image_at((60, 440, 93, 68)), -90)
        self.arm_l_drawn = None

        leftPadding = 20
        self.head_rect = self.head.get_rect().move(38 + leftPadding, 20)
        self.blink_rect = self.blink.get_rect().move(100 + leftPadding, 130)
        self.hat_point_rect = self.hat_point.get_rect().move(-5 + leftPadding, 35)
        self.hair_rect = self.body.get_rect().move(53 + leftPadding, 160)
        self.body_rect = self.body.get_rect().move(45 + leftPadding, 190)
        self.foot_l_rect = self.foot_l.get_rect().move(60 + leftPadding, 285)
        self.foot_r_rect = self.foot_r.get_rect().move(113 + leftPadding, 290)
        self.arm_r_rect = self.arm_r.get_rect().move(74 + leftPadding, 150)
        self.arm_r_drawn_rect = None
        self.arm_l_rect = self.arm_l.get_rect().move(90 + leftPadding, 165)
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
        self.arm_r_acc = Vector2(0, 2)  # current angle, rate of change

        self.weapons = [WoodenWizardStaff(-90), RedWizardStaff(-90)]
        self.weapon = self.weapons[0]

        self.weapon_drawn_rect = None
        self.weapon_drawn = None

        self.animate()  ## first tick to set up rotations

    def draw(self, surface: pygame.Surface):
        """Moved on to bliting to a temp surface for left, right facing"""
        # logging.debug("Drawing at {}".format(self.pos))
        totalSize = Rect((0, 0, self.w, self.h))
        tmpSurface = pygame.Surface(totalSize.size).convert_alpha()

        tmpSurface.blit(self.hat_point, self.hat_point_rect)
        pygame.draw.circle(tmpSurface, "green", self.arm_l_rect.center, 3)
        pygame.draw.circle(tmpSurface, "blue", self.weapon_drawn_rect.center, 3)
        # pygame.draw.rect(tmpSurface, (200, 200, 200), totalSize, 1)

        if self.directionFacing == RIGHT:

            tmpSurface.blit(self.weapon_drawn, self.weapon_drawn_rect)
            tmpSurface.blit(self.arm_l_drawn, self.arm_l_drawn_rect)
            tmpSurface.blit(self.foot_l, self.foot_l_rect)
            tmpSurface.blit(self.foot_r, self.foot_r_rect)
            # Needs arm/shoulder offsets
            tmpSurface.blit(self.hair, self.hair_rect)
            tmpSurface.blit(self.body, self.body_rect)

            tmpSurface.blit(self.head, self.head_rect)
            tmpSurface.blit(self.arm_r_drawn, self.arm_r_drawn_rect)
            pygame.draw.circle(tmpSurface, "green", self.arm_r_rect.center, 3)
            pygame.draw.circle(tmpSurface, "blue", self.arm_r_drawn_rect.center, 3)
        else:
            tmpSurface.blit(self.foot_l, self.foot_l_rect)
            tmpSurface.blit(self.foot_r, self.foot_r_rect)
            tmpSurface.blit(self.arm_r_drawn, self.arm_r_drawn_rect)
            tmpSurface.blit(self.hair, self.hair_rect)
            tmpSurface.blit(self.body, self.body_rect)
            tmpSurface.blit(self.head, self.head_rect)
            tmpSurface.blit(self.weapon_drawn, self.weapon_drawn_rect)
            tmpSurface.blit(self.arm_l_drawn, self.arm_l_drawn_rect)
            pygame.draw.circle(tmpSurface, "green", self.arm_l_rect.center, 3)
            pygame.draw.circle(tmpSurface, "blue", self.arm_l_drawn_rect.center, 3)

        if self.blinking:
            tmpSurface.blit(self.blink, self.blink_rect)

        if self.directionFacing == LEFT:
            tmpSurface = pygame.transform.flip(tmpSurface, True, False)

        tmpSurface = pygame.transform.scale(tmpSurface, (self.w * screen.SCALE, self.h * screen.SCALE))
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
        if pressed_keys[K_8]:
            self.weapon = self.weapons[0]

        if pressed_keys[K_9]:
            self.weapon = self.weapons[1]

        self.acc += self.vel * constants.FRIC
        self.vel += self.acc
        self.pos += self.vel + constants.ACC * self.acc

        if self.pos.x > screen.WIDTH:
            self.pos.x = screen.WIDTH
        if self.pos.x < -self.w:
            self.pos.x = -self.w

    def animate(self):
        if self.head_rect.top >= 33:
            self.head_acc = Vector2(0, -1)
        elif self.head_rect.top <= 20:
            self.head_acc = Vector2(0, 1)
        self.head_rect.move_ip(self.head_acc)
        self.blink_rect.move_ip(self.head_acc)
        self.hat_point_rect.move_ip(self.head_acc)
        self.hair_rect.move_ip(self.head_acc)

        self.foot_l_rect.move_ip(self.head_acc.rotate(-180))
        self.foot_r_rect.move_ip(self.head_acc)

        if self.arm_r_acc.x <= self.MAX_ARM_SWING_BACK:
            self.arm_r_acc.y = 2
        elif self.arm_r_acc.x > self.MAX_ARM_SWING_FORTH:
            self.arm_r_acc.y = -2
        self.arm_r_acc.x += self.arm_r_acc.y

        shoulder_offset = pygame.math.Vector2(-29, 0)

        if self.directionFacing == RIGHT:
            offset_arm_r = self.arm_r_rect.move(shoulder_offset)
            offset_arm_l = self.arm_l_rect.move(-shoulder_offset)
        else:
            offset_arm_r = self.arm_r_rect.move(shoulder_offset)
            offset_arm_l = self.arm_l_rect.move(shoulder_offset)


        angle = self.arm_r_acc.x
        self.arm_r_drawn, self.arm_r_drawn_rect = \
            self.rotate(self.arm_r, angle, offset_arm_r.center, Vector2(-10, 50))

        self.arm_l_drawn, self.arm_l_drawn_rect = \
            self.rotate(self.arm_l, -65 - angle, offset_arm_l.center, Vector2(-20, 40))

        self.weapon_drawn, self.weapon_drawn_rect = \
            self.rotate(self.weapon.image, -65 - angle, offset_arm_l.center, Vector2(35, self.weapon.y_offset))

        if self.sinceLastBlink > self.BLINK_RATE:
            self.blinking = True
        if self.sinceLastBlink > self.BLINK_RATE + self.BLINK_DURATION:
            self.blinking = False
            self.sinceLastBlink = 0
            self.BLINK_RATE = random.randint(150, 200)
            self.BLINK_DURATION = random.randint(15, 20)

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


class Weapon(pygame.sprite.Sprite):

    y_offset = 0

    def rotate(self, angle):
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()


class WoodenWizardStaff(Weapon):

    y_offset = 85
    def __init__(self, rotation, position=None):
        super().__init__()
        sheet = SpriteSheet("assets/images/staff_wizard.png")
        self.image = sheet.image_at((10, 241, 70, 265))
        self.rect = self.image.get_rect()
        self.rotate(rotation)


class RedWizardStaff(Weapon):
    y_offset = 70
    def __init__(self, rotation, position=None):
        super().__init__()
        sheet = SpriteSheet("assets/images/staff_wizard.png")
        self.image = sheet.image_at((303, 215, 98, 295))
        self.rect = self.image.get_rect()
        self.rotate(rotation)

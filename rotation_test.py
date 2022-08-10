import logging

import pygame
from spritesheet import SpriteSheet
import screen
from pygame.locals import *
from screen import *

logging.basicConfig(level=logging.DEBUG)
sheet = SpriteSheet("assets/images/staff_wizard.png")

image = sheet.image_at((10, 241, 70, 265))
pos = (WIDTH / 2, HEIGHT / 2)
rect = image.get_rect(center=pos)
offset = pygame.math.Vector2(8, -90)
pos = pygame.math.Vector2(pos)

ball_of_light = sheet.image_at((243, 11, 120, 140))
ball_of_light = pygame.transform.rotate(ball_of_light, -20)
ball_of_light = pygame.transform.flip(ball_of_light, True, False)
ball_of_light_offset = pygame.math.Vector2(60, -165)
ball_of_light_rect = ball_of_light.get_rect(center=pos + ball_of_light_offset).inflate(100, 0)

FramePerSec = pygame.time.Clock()
done = False
i = 0
moving = True
speed = 1


def process_keys():
    global done, moving, rect, speed
    pressed_keys = pygame.key.get_pressed()
    mod_keys = pygame.key.get_mods()
    if pressed_keys[K_q]:
        done = True
    if pressed_keys[K_LEFT]:
        offset.x -= 1
    if pressed_keys[K_RIGHT]:
        offset.x += 1
    if pressed_keys[K_UP]:
        offset.y -= 1
    if pressed_keys[K_DOWN]:
        offset.y += 1
    # logging.info("offset: {}".format(offset))
    if pressed_keys[K_s]:
        moving = not moving
    rect = image.get_rect(center=pos)
    if mod_keys & KMOD_SHIFT and pressed_keys[K_u]:
        screen.FPS += 3
        if screen.FPS >= 90:
            screen.FPS = 90
    elif pressed_keys[K_u]:
        screen.FPS -= 3
        if screen.FPS <= 3:
            screen.FPS = 3
    if mod_keys & KMOD_SHIFT and pressed_keys[K_f]:
        speed -= 1
    elif pressed_keys[K_f]:
        speed += 1


while not done:
    for event in pygame.event.get():
        if event.type == QUIT:
            done = True

    process_keys()

    displaysurface.fill('#30f030')
    if moving:
        i += speed

    rotated_image = pygame.transform.rotozoom(image, i % 360, 1)
    rotated_offset = offset.rotate(-i)
    rotated_rect = rotated_image.get_rect(center=rect.center + rotated_offset)

    rotated_ball_of_light_offset = ball_of_light_offset.rotate(-i)
    rotated_ball_of_light = pygame.transform.rotozoom(ball_of_light, i % 360, 1)
    rotated_ball_of_light_rect = rotated_ball_of_light.get_rect(center=rect.center + rotated_ball_of_light_offset)

    displaysurface.blit(rotated_ball_of_light, rotated_ball_of_light_rect)
    displaysurface.blit(rotated_image, rotated_rect)

    # pygame.draw.rect(displaysurface, "red", rotated_ball_of_light_rect, 1)
    pygame.draw.circle(displaysurface, "green", rotated_rect.center, 5)
    pygame.draw.circle(displaysurface, "blue", rect.center, 5)

    pygame.display.update()
    FramePerSec.tick(screen.FPS)

pygame.quit()

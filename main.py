from pygame.locals import *

import cameragroup
import screen
from screen import *
from wizard import *
from witch import *

logging.basicConfig(level=logging.DEBUG)

pygame.init()
pygame.display.set_caption("Sprite Loading")

FramePerSec = pygame.time.Clock()

all_sprites = cameragroup.YSortCameraGroup()

wizard = Wizard()
all_sprites.add(wizard)
screen.active_player = wizard

witch = Witch((300, 20))
all_sprites.add(witch)


# background = pygame.image.load("assets/images/training.png").convert_alpha()


def game_loop():
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                done = True

        pressed_keys = pygame.key.get_pressed()
        mod_keys = pygame.key.get_mods()
        if pressed_keys[K_q]:
            done = True
        if pressed_keys[K_1]:
            screen.active_player = wizard
        if pressed_keys[K_2]:
            screen.active_player = witch
        if mod_keys & KMOD_SHIFT and pressed_keys[K_s] and screen.SCALE > 0.1:
            screen.SCALE -= 0.1
        elif pressed_keys[K_s] and screen.SCALE < 5:
            screen.SCALE += 0.1

        if mod_keys & KMOD_SHIFT and pressed_keys[K_u]:
            screen.FPS += 3
            if screen.FPS >= 90:
                screen.FPS = 90
        elif pressed_keys[K_u]:
            screen.FPS -= 3
            if screen.FPS <= 3:
                screen.FPS = 3

        displaysurface.fill('#303030')

        all_sprites.update()
        all_sprites.draw(displaysurface)

        pygame.display.update()
        FramePerSec.tick(screen.FPS)

    pygame.quit()


if __name__ == "__main__":
    game_loop()

import pygame
import logging

logging.basicConfig(level=logging.INFO)

pygame.font.init()

logging.info("Default font: '{}'".format(pygame.font.get_default_font()))
for i in pygame.font.get_fonts():
    logging.info("{}".format(i.title()))
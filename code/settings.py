import pygame
from os import walk
from os.path import join
from pytmx.util_pygame import load_pygame

pygame.init()
info = pygame.display.Info()
WINDOW_WIDTH, WINDOW_HEIGHT = info.current_w,info.current_h
TILE_SIZE = 64 
FRAMERATE = 60
BG_COLOR = '#fcdfcd'

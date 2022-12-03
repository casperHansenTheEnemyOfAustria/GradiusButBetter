import pygame, sys, pickle
from pygame.locals import *
from random import *
from math import *

from pygame.time import Clock
from gamestates import Gamestate
import objects as obj

class Gradius_view():
    def __init__(self):
        self.stop_mixer()

    def stop_mixer() -> None:
        pygame.mixer.music.stop()
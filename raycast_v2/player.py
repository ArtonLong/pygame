import pygame
from pygame.locals import *

class Player:
    def __init__(self, x, y, z, a, l):
        self.x, self.y, self.z = x,y,z
        self.a = a
        self.l = l

    def move_player(self, cos, sin):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.a -= 2
        if keys[pygame.K_RIGHT]:
            self.a += 2
        self.a = self.rotation_clamp(self.a)

        dx = sin[self.a]*5
        dy = cos[self.a]*5

        if keys[pygame.K_d]:
            self.x += dy
            self.y -= dx
        if keys[pygame.K_a]:
            self.x -= dy
            self.y += dx
        if keys[pygame.K_w]:
            self.x += dx
            self.y += dy
        if keys[pygame.K_s]:
            self.x -= dx
            self.y -= dy
        if keys[pygame.K_UP]:
            self.l -= 1
        if keys[pygame.K_DOWN]:
            self.l += 1
        if keys[pygame.K_SPACE]:
            self.z += 4
        if keys[pygame.K_LCTRL]:
            self.z -= 4

    def rotation_clamp(self, a):
        if a < 0:
            a += 360
        elif a > 359:
            a -= 360
        return a
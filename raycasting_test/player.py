import pygame
from pygame.locals import *
import math

from settings import *

class Player:
    def __init__(self):

        self.camera = pygame.Vector3(WIDTH/2, HEIGHT-10, HEIGHT/2)
        self.rotation_angle = 0 * (math.pi / 180)
        self.turn_direction = 0
        self.walk_direction = 0
        self.pitch_angle = 0 * (math.pi / 180)
        self.pitch_direction = 0
        self.move_speed = 2.5
        self.rotation_speed = 2 * (math.pi / 180)

        self.width_ray_point = pygame.Vector2(self.camera.x, self.camera.y)
        self.height_ray_point = pygame.Vector2(self.camera.y + OFFSET, self.camera.z)

    def update(self, surface):
        keys = pygame.key.get_pressed()

        self.turn_direction = 0
        self.walk_direction = 0
        self.pitch_direction = 0

        if keys[pygame.K_RIGHT]:
            self.turn_direction = 1
        if keys[pygame.K_LEFT]:
            self.turn_direction = -1
        if keys[pygame.K_UP]:
            self.pitch_direction = 1
        if keys[pygame.K_DOWN]:
            self.pitch_direction = -1
        if keys[pygame.K_w]:
            self.walk_direction = 1
        if keys[pygame.K_s]:
            self.walk_direction = -1

        move_step = self.walk_direction * self.move_speed
        self.rotation_angle += self.turn_direction * self.rotation_speed
        self.width_ray_point.x += math.cos(self.rotation_angle) * move_step
        self.width_ray_point.y += math.sin(self.rotation_angle) * move_step

        self.pitch_angle += self.pitch_direction * self.rotation_speed

        if self.pitch_angle > math.pi * 1.5:
            self.pitch_angle = math.pi * 1.5
        elif self.pitch_angle < math.pi/2:
            self.pitch_angle = math.pi/2

        self.height_ray_point.x = self.width_ray_point.y + OFFSET
        #self.height_ray_point.y += math.sin(self.pitch_angle)

        pygame.draw.circle(surface, (255,0,0), self.width_ray_point, 5)
        pygame.draw.circle(surface, (255,0,0), self.height_ray_point, 5)

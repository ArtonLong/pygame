import pygame
from pygame.locals import *
import math

from settings import *

def normalize_angle(angle):
    angle = angle % (2*math.pi)
    if (angle < 0):
        angle = (2 * math.pi) + angle
    return angle   

class Ray:
    def __init__(self, angle, ray_point: pygame.Vector2):
        self.angle = normalize_angle(angle)
        self.ray_point = ray_point

    def cast(self):
        pass

    def render(self, surface):
        pygame.draw.line(surface, (255,0,0), self.ray_point, (self.ray_point.x + math.cos(self.angle) * 50, self.ray_point.y + math.sin(self.angle) * 50), 1)

class Raycaster:
    def __init__(self, player):
        # self.width_rays: list[Ray] = []
        # self.height_rays: list[Ray] = []
        self.rays: list[Ray] = []
        self.player = player

    def cast_all_rays(self):
        # self.width_rays = []
        # self.height_rays = []
        self.rays = []
        ray_angle = (self.player.rotation_angle - FOV/2)
        ray_pitch = (self.player.pitch_angle - FOV/2)
        for i in range(NUM_RAYS):
            width_ray = Ray(ray_angle, self.player.width_ray_point)
            width_ray.cast()
            self.rays.append(width_ray)

            height_ray = Ray(ray_pitch, self.player.height_ray_point)
            height_ray.cast()
            self.rays.append(height_ray)

            ray_angle += FOV / NUM_RAYS
            ray_pitch += FOV / NUM_RAYS

    def render(self, screen):
        for r in self.rays:
            r.render(screen)
import pygame
from pygame.locals import *
import math

class Particle:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.predicted_x = 0
        self.predicted_y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.density = 1
        self.color = (0,0,255)
        self.radius = 5
        self.collison_damping = 0.5

        self.tagged = False

    def update_velocity(self):
        self.x += self.velocity_x
        self.y += self.velocity_y

    def update_collisions(self, bounds_width, bounds_height, bounds_x, bounds_y):
        bounds_radius_w = bounds_width - self.radius
        bounds_radius_h = bounds_height - self.radius
        detect_x = self.x - bounds_x
        detect_y = self.y - bounds_y

        if detect_x > bounds_radius_w or detect_x < 0:
            self.x = (bounds_radius_w * self.sign(detect_x)) + bounds_x
            self.velocity_x *= -1 * self.collison_damping
        if detect_y > bounds_radius_h or detect_y < 0:
            self.y = (bounds_radius_h * self.sign(detect_y)) + bounds_y
            self.velocity_y *= -1 * self.collison_damping

    def sign(self, number):
        #the display starts at 0 and does not go negative
        if number > 0:
            return 1
        else:
            return 0


    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)
        
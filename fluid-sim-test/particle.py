import pygame
from pygame.locals import *
import math

class Particle:
    def __init__(self):
        self.position = pygame.math.Vector2(0, 0)
        self.predicted_position = pygame.math.Vector2(0, 0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.density = 1
        self.color = (0,0,255)
        self.radius = 5
        self.collison_damping = 0.5

        self.tagged = False

    def update_velocity(self):
        self.position += self.velocity

    def update_collisions(self, bounds: pygame.math.Vector2, bounds_position: pygame.math.Vector2):
        bounds_radius = bounds - pygame.math.Vector2(self.radius, self.radius)
        temp_position = self.position - bounds_position

        if temp_position.x > bounds_radius.x or temp_position.x < 0:
            self.position.x = (bounds_radius.x * self.sign(temp_position.x)) + bounds_position.x
            self.velocity.x *= -1 * self.collison_damping
        if temp_position.y > bounds_radius.y or temp_position.y < 0:
            self.position.y = (bounds_radius.y * self.sign(temp_position.y)) + bounds_position.y
            self.velocity.y *= -1 * self.collison_damping

    def sign(self, number):
        #the display starts at 0 and does not go negative
        if number > 0:
            return 1
        else:
            return 0


    def draw(self, surface):
        pygame.draw.circle(surface, self.color, self.position, self.radius)
        
import pygame
from pygame.locals import *
import math

from settings import *

def normalize_angle(angle):
    angle = angle % (2*math.pi)
    if (angle <= 0):
        angle = (2 * math.pi) + angle
    return angle   

def distance_between(x1,y1,x2,y2):
    return math.sqrt((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1))

class Ray:
    def __init__(self, angle, ray_point: pygame.Vector2, map, is_height = False):
        self.angle = normalize_angle(angle)
        self.ray_point = ray_point
        self.map = map
        self.is_height = is_height

        self.is_facing_down = self.angle > 0 and self.angle < math.pi
        self.is_facing_up = not self.is_facing_down
        self.is_facing_right = self.angle < 0.5 * math.pi or self.angle > 1.5 * math.pi
        self.is_facing_left = not self.is_facing_right

        self.wall_hit_x = 0
        self.wall_hit_y = 0

    def cast(self):
        found_horizontal_wall = False
        horizontal_hit_x = 0
        horizontal_hit_y = 0

        first_intersection_x = None
        first_intersection_y = None

        if self.is_facing_up:
            first_intersection_y = ((self.ray_point.y // TILESIZE) * TILESIZE) - 1
        elif self.is_facing_down:
            first_intersection_y = ((self.ray_point.y // TILESIZE) * TILESIZE) + TILESIZE

        first_intersection_x = self.ray_point.x + (first_intersection_y - self.ray_point.y) / math.tan(self.angle)

        next_horizontal_x = first_intersection_x
        next_horizontal_y = first_intersection_y

        xa = 0
        ya = 0

        if self.is_facing_up:
            ya = -TILESIZE
        elif self.is_facing_down:
            ya = TILESIZE

        xa = ya / math.tan(self.angle)

        while (next_horizontal_x <= WIDTH and next_horizontal_x >= 0 and next_horizontal_y <= HEIGHT and next_horizontal_y >= 0):
            if self.map.has_wall_at(next_horizontal_x, next_horizontal_y, self.is_height):
                found_horizontal_wall = True
                horizontal_hit_x = next_horizontal_x
                horizontal_hit_y = next_horizontal_y
                break
            else:
                next_horizontal_x += xa
                next_horizontal_y += ya

        found_vertical_wall = False
        vertical_hit_x = 0
        vertical_hit_y = 0

        if self.is_facing_right:
            first_intersection_x = ((self.ray_point.x // TILESIZE) * TILESIZE) + TILESIZE
        elif self.is_facing_left:
            first_intersection_x = ((self.ray_point.x // TILESIZE) * TILESIZE) - 1

        first_intersection_y = self.ray_point.y + (first_intersection_x - self.ray_point.x) * math.tan(self.angle)

        next_vertical_x = first_intersection_x
        next_vertical_y = first_intersection_y

        if self.is_facing_right:
            xa = TILESIZE
        elif self.is_facing_left:
            xa = -TILESIZE

        ya = xa * math.tan(self.angle)

        while (next_vertical_x <= WIDTH and next_vertical_x >= 0 and next_vertical_y <= HEIGHT and next_vertical_y >= 0):
            if self.map.has_wall_at(next_vertical_x, next_vertical_y, self.is_height):
                found_vertical_wall = True
                vertical_hit_x = next_vertical_x
                vertical_hit_y = next_vertical_y
                break
            else:
                next_vertical_x += xa
                next_vertical_y += ya
                
        horizontal_distance = 0
        vertical_distance = 0

        if found_horizontal_wall:
            horizontal_distance = distance_between(self.ray_point.x, self.ray_point.y, horizontal_hit_x, horizontal_hit_y)
        else:
            horizontal_distance = 99999999

        if found_vertical_wall:
            vertical_distance = distance_between(self.ray_point.x, self.ray_point.y, vertical_hit_x, vertical_hit_y)
        else:
            vertical_distance = 99999999

        if horizontal_distance < vertical_distance:
            self.wall_hit_x = horizontal_hit_x
            self.wall_hit_y = horizontal_hit_y
        else:
            self.wall_hit_x = vertical_hit_x
            self.wall_hit_y = vertical_hit_y

    def render(self, surface):
        pygame.draw.line(surface, (255,0,0), self.ray_point, (self.wall_hit_x, self.wall_hit_y))

class Raycaster:
    def __init__(self, player, map):
        self.width_rays: list[Ray] = []
        self.height_rays: list[Ray] = []
        self.player = player
        self.map = map

    def cast_hight_rays(self):
        ray_pitch = (self.player.pitch_angle - FOV/2)
        for i in range(NUM_RAYS):
            height_ray = Ray(ray_pitch, self.player.height_ray_point, self.map, is_height=True)
            height_ray.cast()
            self.height_rays.append(height_ray)

            ray_pitch += FOV / NUM_RAYS

    def cast_all_rays(self):
        self.width_rays = []
        self.height_rays = []
        ray_angle = (self.player.rotation_angle - FOV/2)
        for i in range(NUM_RAYS):
            width_ray = Ray(ray_angle, self.player.width_ray_point, self.map)
            width_ray.cast()
            self.cast_hight_rays()
            self.width_rays.append(width_ray)

            ray_angle += FOV / NUM_RAYS
            

    def render(self, screen):
        for r in self.width_rays:
            r.render(screen)
        for r in self.height_rays:
            r.render(screen)
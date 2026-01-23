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
    def __init__(self, angle, player, ray_point: pygame.Vector2, map, is_height = False):
        self.angle = normalize_angle(angle)
        self.ray_point = ray_point
        self.player = player
        self.map = map
        self.is_height = is_height
        self.height_rays: list[Ray] = []

        self.debug = False

        self.is_facing_down = self.angle > 0 and self.angle < math.pi
        self.is_facing_up = not self.is_facing_down
        self.is_facing_right = self.angle < 0.5 * math.pi or self.angle > 1.5 * math.pi
        self.is_facing_left = not self.is_facing_right

        self.wall_hit_x = 0
        self.wall_hit_y = 0
        self.all_hits = []

        self.distance = 0
        self.color = 255

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

        while (next_horizontal_x < WIDTH and next_horizontal_x > 0 and next_horizontal_y < HEIGHT and next_horizontal_y > 0):
            if self.map.has_wall_at(next_horizontal_x, next_horizontal_y, self.is_height):
                if self.is_height:
                    found_horizontal_wall = True
                    horizontal_hit_x = next_horizontal_x
                    horizontal_hit_y = next_horizontal_y
                    break
                else:
                    self.all_hits.append((next_horizontal_x, next_horizontal_y, distance_between(self.ray_point.x, self.ray_point.y, next_horizontal_x, next_horizontal_y)))
                    next_horizontal_x += xa
                    next_horizontal_y += ya
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

        while (next_vertical_x < WIDTH and next_vertical_x > 0 and next_vertical_y < HEIGHT and next_vertical_y > 0):
            if self.map.has_wall_at(next_vertical_x, next_vertical_y, self.is_height):
                if self.is_height:
                    found_vertical_wall = True
                    vertical_hit_x = next_vertical_x
                    vertical_hit_y = next_vertical_y
                    break
                else:
                    self.all_hits.append((next_vertical_x, next_vertical_y, distance_between(self.ray_point.x, self.ray_point.y, next_vertical_x, next_vertical_y)))
                    next_vertical_x += xa
                    next_vertical_y += ya
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
            self.distance = horizontal_distance
        else:
            self.wall_hit_x = vertical_hit_x
            self.wall_hit_y = vertical_hit_y
            self.distance = vertical_distance

        #self.distance *= math.cos(self.player.rotation_angle - self.angle)

        self.color *= (60 / self.distance)
        self.color = max(min(255, self.color), 0)

    def render(self, surface):
        color = (255,0,0)
        if self.debug:
            color = (0,255,0)
        pygame.draw.line(surface, color, self.ray_point, (self.wall_hit_x, self.wall_hit_y))

class Raycaster:
    def __init__(self, player, map):
        self.width_rays: list[Ray] = []
        self.player = player
        self.map = map

    def cast_hight_rays(self):
        height_rays = []
        ray_pitch = (self.player.pitch_angle - FOV/2)
        for i in range(NUM_RAYS):
            height_ray = Ray(ray_pitch, self.player, self.player.height_ray_point, self.map, is_height=True)
            height_ray.cast()
            height_rays.append(height_ray)

            ray_pitch += FOV / NUM_RAYS
        return height_rays

    def cast_all_rays(self, surface):
        self.width_rays = []
        self.height_rays = []
        ray_angle = (self.player.rotation_angle - FOV/2)
        for i in range(NUM_RAYS):
            width_ray = Ray(ray_angle, self.player, self.player.width_ray_point, self.map)
            width_ray.cast()
            self.map.create_height_slice(width_ray)
            if i == NUM_RAYS//2:
                width_ray.debug = True
                #self.map.draw_height(surface)
            width_ray.height_rays = self.cast_hight_rays()
            self.width_rays.append(width_ray)
            self.map.reset_height_map()

            ray_angle += FOV / NUM_RAYS
            

    def render(self, screen):
        for i, width_ray in enumerate(self.width_rays):
            #width_ray.render(screen)

            # line_height = (TILESIZE/width_ray.all_hits[0][2]) * 400

            # draw_begin = (HEIGHT/2) - (line_height/2)
            # draw_end = line_height

            #pygame.draw.rect(screen, (width_ray.color, width_ray.color, width_ray.color), (i*RESULUTION + OFFSET, draw_begin, RESULUTION, draw_end))
            
            for j, height_ray in enumerate(width_ray.height_rays):
                if width_ray.debug:
                    height_ray.render(screen)

                #box = height_ray.distance / TILESIZE
                #angle = math.radians(FOV/NUM_RAYS)
                #box = math.sqrt(height_ray.distance**2 + height_ray.distance**2 - 2*height_ray.distance*height_ray.distance*math.cos(angle))

                # draw_begin = (WIDTH/2) - (line_height/2)
                # draw_end = line_height

                ## draw the size of boxes to be the distance to the ray to the side of it 

                #pygame.draw.rect(screen, (height_ray.color, height_ray.color, height_ray.color), (i*RESULUTION + OFFSET, HEIGHT - j*RESULUTION, box, box))


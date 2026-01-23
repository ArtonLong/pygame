import pygame
from pygame.locals import *

from settings import *
from ray import Ray

class Object:
    def __init__(self, width, height, depth, x, y, z, color: tuple[int,int,int]):
        self.width = width
        self.height = height
        self.depth = depth
        self.x = x
        self.y = y
        self.z = z
        self.color = color
    
    #width
    def rect_width(self):
        return pygame.rect.Rect((self.x*TILESIZE, self.y*TILESIZE), (self.width*TILESIZE, self.height*TILESIZE))
    
    def draw_width(self, surface):
        pygame.draw.rect(surface, self.color, self.rect_width(), 1)

    #height
    def rect_height(self, distance_from_player):
        return pygame.rect.Rect((self.y*TILESIZE, self.z*TILESIZE), (self.y*TILESIZE, self.z*TILESIZE))
    
    def draw_height(self, surface, distance_from_player):
        pygame.draw.rect(surface, self.color, self.rect_height(distance_from_player))

class Map:
    def __init__(self):
        self.width_walls: list[Object] = [Object(1,1,1, (WIDTH/2)//TILESIZE,(HEIGHT/2)//TILESIZE,3, (255,255,255))]
        self.width_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
        self.height_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.generate_empty_cube()
        self.place_walls()

    def place_walls(self):
        for w in self.width_walls:
            self.width_grid[int(w.y)][int(w.x)] = w

    def has_wall_at(self, x, y, is_height):
        if not is_height:
            if self.width_grid[int(y//TILESIZE)][int(x//TILESIZE)] != 0:
                    return True
        else:
            if self.height_grid[int(y//TILESIZE)][int(x//TILESIZE)] != 0:
                return True
        return False
    
    def generate_empty_cube(self):
        for i in range(COLS):
            if i == 0:
                for x in range(ROWS):
                    self.width_walls.append(Object(1,1,ROWS, x, i, 0, (255,255,255)))
            if i == COLS - 1:
                for x in range(ROWS):
                    self.width_walls.append(Object(1,1,0, x, i, 0, (255,255,255)))
            else:
                self.width_walls.append(Object(1,1,ROWS, 0, i, 0, (255,255,255)))
                self.width_walls.append(Object(1,1,0, ROWS-1, i, 0, (255,255,255)))

    
    def create_height_slice(self, ray: Ray):
        for r in ray.all_hits:
            if -15 >= int(r[2]//-TILESIZE):
                return
            wall = self.width_grid[int(r[0]//TILESIZE)][int(r[1]//TILESIZE)]
            if wall != 0:
                for z in range(wall.depth):
                    self.height_grid[int(r[2]//-TILESIZE)][wall.z + z] = wall

    def reset_height_map(self):
        self.height_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]


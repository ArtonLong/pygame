import pygame
from pygame.locals import *

from settings import *

class Object:
    def __init__(self, width, height, depth, x, y, z, color: tuple[int,int,int]):
        self.size = pygame.Vector3(width, depth, height)
        self.position = pygame.Vector3(x, y, z)
        self.color = color
    
    #width
    def rect_width(self):
        return pygame.rect.Rect((self.position.x - self.size.x/2, self.position.y - self.size.y/2), (self.size.x, self.size.y))
    
    def draw_width(self, surface):
        pygame.draw.rect(surface, self.color, self.rect_width())

    def draw_as_circle_width(self, surface):
        pygame.draw.circle(surface, self.color, (self.position.x, self.position.y), self.position.x/2)

    #height
    def rect_height(self):
        return pygame.rect.Rect((self.position.y + OFFSET - self.size.y/2, self.position.z - self.size.z/2), (self.size.y, self.size.z))
    
    def draw_height(self, surface):
        pygame.draw.rect(surface, self.color, self.rect_height())

    def draw_as_circle_height(self, surface):
        pygame.draw.circle(surface, self.color, (self.position.y, self.position.z), self.position.z/2)

class Map:
    def __init__(self):
        self.width_grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),(1,1),(1,1),0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,(1,1),0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            
        ]
        self.height_grid = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        ]
        self.width_tile_coords = []
        self.height_tile_coords = []
        self.compute_width()

    def draw_width(self, surface):
        for tc in self.width_tile_coords:
            if tc[2] == 1:
                pygame.draw.rect(surface, (255,255,255), (self.tile_coords_to_map(tc), (TILESIZE, TILESIZE)))

    def draw_height(self, surface):
        for tc in self.height_tile_coords:
            if tc[2] == 1:
                coords = self.tile_coords_to_map(tc)
                pygame.draw.rect(surface, (255,255,255), ((coords[0] + OFFSET, coords[1]), (TILESIZE, TILESIZE)))

    def tile_coords_to_map(self, tile):
        return (tile[0]*TILESIZE, tile[1]*TILESIZE)

    def compute_width(self):
        for r in range(len(self.width_grid)):
            for c in range(len(self.width_grid[0])):
                is_block = 0
                if type(self.width_grid[r][c]) == tuple or self.width_grid[r][c] == 1:
                    is_block = 1
                self.width_tile_coords.append((c,r, is_block))
    
    def compute_height(self):
        for r in range(len(self.height_grid)):
            for c in range(len(self.height_grid[0])):
                is_block = 0
                if self.height_grid[r][c] == 1:
                    is_block = 1
                self.height_tile_coords.append((c,r, is_block))

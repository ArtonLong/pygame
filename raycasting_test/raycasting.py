import pygame
from pygame.locals import *
import sys

from settings import *
from map import Map
from ray import Raycaster
from player import Player

class App:
    def __init__(self):
        pygame.init()

        self._running = True
        self.player = Player()
        self.DISPLAY_SURF = pygame.display.set_mode(SIZE)

        self.map = Map()
        self.ray_caster = Raycaster(self.player, self.map)

    def on_quit(self):
        pygame.quit()
        sys.exit()

    def font(self, text):
        font = pygame.font.SysFont("Arial" , 18 , bold = True)
        return font.render(text , 1, pygame.Color("RED"))

    def fps_counter(self, clock):
        fps = str(int(clock.get_fps()))
        fps_t = self.font(fps)
        self.DISPLAY_SURF.blit(fps_t,(WIDTH-20,0))
 
    def on_execute(self):
        clock = pygame.time.Clock()

        while( self._running ):
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_quit()
            self.DISPLAY_SURF.fill((0,0,0))
            self.DISPLAY_SURF.fill((50,50,50), ((OFFSET, 0),(WIDTH, HEIGHT)))
            pygame.draw.line(self.DISPLAY_SURF, (255,255,255), (WIDTH, 0), (WIDTH, HEIGHT), 1)

            self.map.draw_width(self.DISPLAY_SURF)
            #self.map.draw_height(self.DISPLAY_SURF)

            self.player.update(self.DISPLAY_SURF)
            self.ray_caster.cast_all_rays(self.DISPLAY_SURF)
            self.ray_caster.render(self.DISPLAY_SURF)

            self.fps_counter(clock)
            pygame.display.update()
            clock.tick(FPS)
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
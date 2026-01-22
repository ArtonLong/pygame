import sys
import pygame
from pygame.locals import *
import math
import threading

from particle import Particle

 
class App:
    def __init__(self):
        pygame.init()

        self.FPS = 60
        self._running = True
        self.width, self.height = 800, 700
        self.size = (self.width, self.height)

        self.bounds = pygame.math.Vector2(350, 350)
        self.bounds_position = pygame.math.Vector2(100, 100)
        self.num_particles = 100
        self.spacing = 10

        self.particals = self.create_particals()
        self.particals[0].tagged = True

        self.DISPLAY_SURF = pygame.display.set_mode(self.size)

        self.smoothing_radius = 25
        self.gravity = 0.1
        self.MASS = 1
        self.target_density = 130
        self.pressure_multiplier = 460

        self.particle_cells:dict[int, list[Particle]] = {}
        self.cell_offsets = [(-1,1),(0,1),(1,1),(-1,0),(0,0),(1,0),(-1,-1),(0,-1),(1,-1)]

        self.is_bounds_unlocked = False

    def debug(self, p:Particle):
        if p.tagged:
            pygame.draw.line(self.DISPLAY_SURF, (255, 255, 255), p.position, p.position + p.velocity, 2)
            pygame.draw.circle(self.DISPLAY_SURF, (255,255,255), p.position, self.smoothing_radius, 2)
            p_and_v = f"position: {p.position} velocity: {p.velocity}"
            p_and_v = self.font(p_and_v)
            self.DISPLAY_SURF.blit(p_and_v,(self.width/3, 10))
        temp_position = p.position - self.bounds_position
        pygame.draw.circle(self.DISPLAY_SURF, (255,0,0), temp_position, p.radius)

    def move_bounds(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_m] and not self.is_bounds_unlocked:
            self.is_bounds_unlocked = True
            pygame.mouse.set_pos(self.bounds_position)
        elif key[pygame.K_m]:
            self.is_bounds_unlocked = False

        if self.is_bounds_unlocked:
            mouse_pos = pygame.mouse.get_pos()
            self.bounds_position = pygame.math.Vector2(mouse_pos)

    def draw_cell(self, position):
        cell = self.position_to_cell_coord(position)
        area = pygame.Rect(cell.x*self.smoothing_radius, cell.y*self.smoothing_radius, self.smoothing_radius, self.smoothing_radius)
        pygame.draw.rect(self.DISPLAY_SURF, (255,255,255), area, 1)
        

    def create_cell_coords(self):
        num_of_cells = self.bounds / self.smoothing_radius
        for x in range(math.floor(num_of_cells.x)):
            for y in range(math.floor(num_of_cells.y)):
                self.particle_cells[self.hash_cell_key(pygame.math.Vector2(x,y))] = []

        threads = []
        for p in self.particals:
            t = threading.Thread(target=self.update_cells, args=(p,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def foreach_point_within_radius(self, particle: Particle):
        origin_cell = self.position_to_cell_coord(particle.predicted_position)
        sqr_radius = self.smoothing_radius * self.smoothing_radius

        for i in range(9):
            key = origin_cell + self.cell_offsets[i]

            try:
                particals = self.particle_cells[self.hash_cell_key(key)]
            except:
                continue

            for other_particle in particals:

                sqd_dis = (other_particle.predicted_position - particle.predicted_position).magnitude_squared()
                if (sqd_dis <= sqr_radius):
                    particle.density += self.calculate_density(particle, other_particle)

            pressure_force = pygame.math.Vector2(0,0)

            for other_particle in particals:
                    
                sqd_dis = (other_particle.predicted_position - particle.predicted_position).magnitude_squared()

                if (sqd_dis <= sqr_radius):
                    pressure_force += self.calculate_pressure_force(particle, other_particle)

            pressure_accelaration = pressure_force / particle.density
            particle.velocity += pressure_accelaration
        
    def update_cells(self, p:Particle):
        #predict where the partical will go for better reaction
        p.predicted_position = p.position + p.velocity
        cell = self.position_to_cell_coord(p.predicted_position)
        try:
            self.particle_cells[self.hash_cell_key(cell)].append(p)
        except:
            cell = self.position_to_cell_coord(p.position)
            self.particle_cells[self.hash_cell_key(cell)].append(p)

    def position_to_cell_coord(self, point: pygame.math.Vector2):
        div_vector = (point - self.bounds_position) / self.smoothing_radius
        return pygame.math.Vector2(math.floor(div_vector.x), math.floor(div_vector.y))
    
    def hash_cell_key(self, coords:pygame.math.Vector2):
        a = coords.x * 37
        b = coords.y * 907
        return a + b

    def convert_density_to_pressure(self, density):
        density_error = density - self.target_density
        pressure = density_error * self.pressure_multiplier
        return pressure
    
    def calculate_shared_pressure(self, density_a, density_b):
        pressure_a = self.convert_density_to_pressure(density_a)
        pressure_b = self.convert_density_to_pressure(density_b)
        return (pressure_a + pressure_b) / 2
    
    def  calculate_pressure_force(self, particle: Particle, other_particle: Particle):
        if particle.position == other_particle.position:
            return pygame.math.Vector2(0,0)

        dst = (other_particle.predicted_position - particle.predicted_position).magnitude()
        dir = (other_particle.predicted_position - particle.predicted_position) / dst
        slope = self.smoothing_kernal_derivative(dst)
        shared_pressure = self.calculate_shared_pressure(particle.density, other_particle.density)
        return -shared_pressure * dir * slope * self.MASS / other_particle.density

    def smoothing_kernal(self, dst):
        if dst >= self.smoothing_radius:
            return 0
        volume = (math.pi * pow(self.smoothing_radius, 4)) / 6
        return (self.smoothing_radius - dst) * (self.smoothing_radius - dst) / volume
    
    def smoothing_kernal_derivative(self, dst):
        if dst >= self.smoothing_radius:
            return 0
        scale = 12 / (pow(self.smoothing_radius, 4) * math.pi)
        return (dst - self.smoothing_radius) * scale
    
    def calculate_density(self, particle: Particle, other_particle: Particle):
        density = 0
        dst = (other_particle.predicted_position - particle.predicted_position).magnitude()
        influence = self.smoothing_kernal(dst)
        density += self.MASS * influence
        return density

    def create_particals(self) -> list[Particle]:
        particles = []
        particles_per_row, Particles_per_colum = self.particle_start_pos()
        for i, p in enumerate(range(self.num_particles)):
            p = Particle()
            p.position.x = ((i % particles_per_row + particles_per_row / 4 + 0.5) * (p.radius * 2 + self.spacing)) + self.bounds_position.x
            p.position.y = ((i / particles_per_row + Particles_per_colum / 4 + 0.5) * (p.radius * 2 + self.spacing)) + self.bounds_position.y
            particles.append(p)
        return particles
    
    def particle_start_pos(self):
        particles_per_row = int(math.sqrt(self.num_particles))
        Particles_per_colum = (self.num_particles - 1) / particles_per_row + 1
        return particles_per_row, Particles_per_colum 
    
    def update_partical(self, p: Particle):
        p.velocity += pygame.math.Vector2(0,1) * self.gravity

        if p.tagged:
            p.color = (0,255,0)
        else:
            p.color = (0,0,255)
        
        self.foreach_point_within_radius(p)
        
        p.update_velocity()
        p.update_collisions(self.bounds, self.bounds_position)
        p.draw(self.DISPLAY_SURF)

        self.debug(p)

    def draw_bounds(self):
        pygame.draw.rect(self.DISPLAY_SURF, (255,255,255), (self.bounds_position, self.bounds), 1)
            
    def on_quit(self):
        pygame.quit()
        sys.exit()

    def font(self, text):
        font = pygame.font.SysFont("Arial" , 18 , bold = True)
        return font.render(text , 1, pygame.Color("RED"))

    def fps_counter(self, clock):
        fps = str(int(clock.get_fps()))
        fps_t = self.font(fps)
        self.DISPLAY_SURF.blit(fps_t,(self.bounds.x + 40,0))
 
    def on_execute(self):
        clock = pygame.time.Clock()

        while( self._running ):
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_quit()
            self.DISPLAY_SURF.fill((0,0,0))

            self.create_cell_coords()
            
            threads = []
            for p in self.particals:
                t = threading.Thread(target=self.update_partical, args=(p,))
                threads.append(t)

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            self.move_bounds()
            self.draw_bounds()

            self.fps_counter(clock)
            pygame.display.update()
            clock.tick(self.FPS)
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
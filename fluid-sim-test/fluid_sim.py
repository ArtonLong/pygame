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

        self.bounds_width = 350
        self.bounds_height = 350
        self.bounds_x = 100
        self.bounds_y = 100
        self.num_particles = 100
        self.spacing = 10

        self.particals = self.create_particals()
        self.particals[0].tagged = True

        self.DISPLAY_SURF = pygame.display.set_mode(self.size)

        self.smoothing_radius = 25
        self.gravity = 0.1
        self.MASS = 1
        self.target_density = 130 # 130
        self.pressure_multiplier = 460 # 460

        self.particle_cells:dict[int, list[Particle]] = {}
        self.cell_offsets = [(-1,1),(0,1),(1,1),(-1,0),(0,0),(1,0),(-1,-1),(0,-1),(1,-1)]

        self.is_bounds_unlocked = False

    def debug(self, p:Particle):
        if p.tagged:
            pygame.draw.line(self.DISPLAY_SURF, (255, 255, 255), (p.x, p.y), (p.x + p.velocity_x, p.y + p.velocity_y), 2)
            pygame.draw.circle(self.DISPLAY_SURF, (255,255,255), (p.x, p.y), self.smoothing_radius, 2)
            p_and_v = f"position: {(round(p.x), round(p.y))} velocity: {(p.velocity_x, p.velocity_y)}"
            p_and_v = self.font(p_and_v)
            self.DISPLAY_SURF.blit(p_and_v,(self.width/3, 10))
        x = p.x - self.bounds_x
        y = p.y - self.bounds_y
        pygame.draw.circle(self.DISPLAY_SURF, (255,0,0), (x,y), p.radius)

    def move_bounds(self):
        key = pygame.key.get_pressed()

        if key[pygame.K_m] and not self.is_bounds_unlocked:
            self.is_bounds_unlocked = True
            pygame.mouse.set_pos(self.bounds_x, self.bounds_y)
        elif key[pygame.K_m]:
            self.is_bounds_unlocked = False

        if self.is_bounds_unlocked:
            mouse_pos = pygame.mouse.get_pos()
            self.bounds_x = mouse_pos[0]
            self.bounds_y = mouse_pos[1]

    def draw_cell(self, x, y):
        cell = self.position_to_cell_coord(x, y)
        area = pygame.Rect(cell[0]*self.smoothing_radius, cell[1]*self.smoothing_radius, self.smoothing_radius, self.smoothing_radius)
        pygame.draw.rect(self.DISPLAY_SURF, (255,255,255), area, 1)
        

    def create_cell_coords(self):
        num_of_cells_x = self.bounds_width / self.smoothing_radius
        num_of_cells_y = self.bounds_height / self.smoothing_radius
        for x in range(math.floor(num_of_cells_x)):
            for y in range(math.floor(num_of_cells_y)):
                self.particle_cells[self.hash_cell_key(x,y)] = []

        threads = []
        for p in self.particals:
            t = threading.Thread(target=self.update_cells, args=(p,))
            threads.append(t)

        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def foreach_point_within_radius(self, particle: Particle):
        origin_cell = self.position_to_cell_coord(particle.predicted_x, particle.predicted_y)
        sqr_radius = self.smoothing_radius * self.smoothing_radius

        for i in range(9):
            key_x = origin_cell[0] + self.cell_offsets[i][0]
            key_y = origin_cell[1] + self.cell_offsets[i][1]

            try:
                particals = self.particle_cells[self.hash_cell_key(key_x, key_y)]
            except:
                continue

            for other_particle in particals:
                if particle.tagged:
                    self.draw_cell(other_particle.x, other_particle.y)

                sqd_dis = self.magnitude_squared(other_particle.predicted_x - particle.predicted_x, other_particle.predicted_y - particle.predicted_y)
                if (sqd_dis <= sqr_radius):
                    particle.density += self.calculate_density(particle, other_particle)

            pressure_force_x = 0
            pressure_force_y = 0

            for other_particle in particals:
                    
                sqd_dis = self.magnitude_squared(other_particle.predicted_x - particle.predicted_x, other_particle.predicted_y - particle.predicted_y)

                if (sqd_dis <= sqr_radius):
                    pressure_forces = self.calculate_pressure_force(particle, other_particle)
                    pressure_force_x += pressure_forces[0]
                    pressure_force_y += pressure_forces[1]

            pressure_accelaration_x = pressure_force_x / particle.density
            pressure_accelaration_y = pressure_force_y / particle.density
            particle.velocity_x += pressure_accelaration_x
            particle.velocity_y += pressure_accelaration_y
        
    def update_cells(self, p:Particle):
        #predict where the partical will go for better reaction
        p.predicted_x = p.x + p.velocity_x
        p.predicted_y = p.y + p.velocity_y
        cell = self.position_to_cell_coord(p.predicted_x, p.predicted_y)
        try:
            self.particle_cells[self.hash_cell_key(cell[0], cell[1])].append(p)
        except:
            cell = self.position_to_cell_coord(p.x, p.y)
            self.particle_cells[self.hash_cell_key(cell[0], cell[1])].append(p)

    def position_to_cell_coord(self, x, y):
        div_x = (x - self.bounds_x) / self.smoothing_radius
        div_y = (y - self.bounds_y) / self.smoothing_radius
        return math.floor(div_x), math.floor(div_y)
    
    def hash_cell_key(self, coord_x, coord_y):
        a = coord_x * 37
        b = coord_y * 907
        return a + b

    def convert_density_to_pressure(self, density):
        density_error = density - self.target_density
        pressure = density_error * self.pressure_multiplier
        return pressure
    
    def calculate_shared_pressure(self, density_a, density_b):
        pressure_a = self.convert_density_to_pressure(density_a)
        pressure_b = self.convert_density_to_pressure(density_b)
        return (pressure_a + pressure_b) / 2
    
    def magnitude(self, x, y):
        return math.sqrt(x**2 + y**2)
    
    def magnitude_squared(self, x, y):
        return x**2 + y**2
    
    def  calculate_pressure_force(self, particle: Particle, other_particle: Particle):
        if particle.x == other_particle.x and particle.y == other_particle.y:
            return 0, 0

        dst = self.magnitude(other_particle.predicted_x - particle.predicted_x, other_particle.predicted_y - particle.predicted_y)
        dir_x = (other_particle.predicted_x - particle.predicted_x) / dst
        dir_y = (other_particle.predicted_y - particle.predicted_y) / dst
        slope = self.smoothing_kernal_derivative(dst)
        shared_pressure = self.calculate_shared_pressure(particle.density, other_particle.density)
        x = -shared_pressure * dir_x * slope * self.MASS / other_particle.density
        y = -shared_pressure * dir_y * slope * self.MASS / other_particle.density
        return x, y#, -shared_pressure * dir_y * slope * self.MASS / other_particle.density

    def smoothing_kernal(self, dst):
        if dst >= self.smoothing_radius:
            return 0
        volume = (math.pi * pow(self.smoothing_radius, 4)) / 6
        return (self.smoothing_radius - dst) * (self.smoothing_radius - dst) / volume
    
    def smoothing_kernal_derivative(self, dst:float):
        if dst >= self.smoothing_radius:
            return 0
        scale = 12 / (pow(self.smoothing_radius, 4) * math.pi)
        return (dst - self.smoothing_radius) * scale
    
    def calculate_density(self, particle: Particle, other_particle: Particle):
        density = 0
        dst = self.magnitude(other_particle.predicted_x - particle.predicted_x, other_particle.predicted_y - particle.predicted_y)
        influence = self.smoothing_kernal(dst)
        density += self.MASS * influence
        return density

    def create_particals(self) -> list[Particle]:
        particles = []
        particles_per_row, Particles_per_colum = self.particle_start_pos()
        for i, p in enumerate(range(self.num_particles)):
            p = Particle()
            p.x = ((i % particles_per_row + particles_per_row / 4 + 0.5) * (p.radius * 2 + self.spacing)) + self.bounds_x
            p.y = ((i / particles_per_row + Particles_per_colum / 4 + 0.5) * (p.radius * 2 + self.spacing)) + self.bounds_y
            particles.append(p)
        return particles
    
    def particle_start_pos(self):
        particles_per_row = int(math.sqrt(self.num_particles))
        Particles_per_colum = (self.num_particles - 1) / particles_per_row + 1
        return particles_per_row, Particles_per_colum 
    
    def update_partical(self, p: Particle):
        p.velocity_y += self.gravity

        if p.tagged:
            p.color = (0,255,0)
        else:
            p.color = (0,0,255)
        
        self.foreach_point_within_radius(p)
        
        p.update_velocity()
        p.update_collisions(self.bounds_width, self.bounds_height, self.bounds_x, self.bounds_y)
        p.draw(self.DISPLAY_SURF)

        self.debug(p)

    def draw_bounds(self):
        pygame.draw.rect(self.DISPLAY_SURF, (255,255,255), ((self.bounds_x, self.bounds_y), (self.bounds_width, self.bounds_height)), 1)
            
    def on_quit(self):
        pygame.quit()
        sys.exit()

    def font(self, text):
        font = pygame.font.SysFont("Arial" , 18 , bold = True)
        return font.render(text , 1, pygame.Color("RED"))

    def fps_counter(self, clock):
        fps = str(int(clock.get_fps()))
        fps_t = self.font(fps)
        self.DISPLAY_SURF.blit(fps_t,(self.bounds_x + 40,0))
 
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
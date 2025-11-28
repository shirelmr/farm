# food.py
import random
import math
from OpenGL.GL import *


class FoodParticle:
    """A single tiny food cube"""
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        # Random velocity - spread outward and fall down
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(1, 3)  # Initial upward velocity
        self.vz = random.uniform(-2, 2)
        self.gravity = -0.15
        self.lifetime = 120  # Frames before disappearing
        self.age = 0
        self.on_ground = False
        self.size = random.uniform(2, 4)  # Tiny cubes!
        
    def update(self):
        """Update particle physics"""
        self.age += 1
        
        # Apply gravity
        self.vy += self.gravity
        
        # Move
        self.x += self.vx
        self.y += self.vy
        self.z += self.vz
        
        # Disappear before hitting ground (when y gets low)
        if self.y <= 10:
            return False  # Remove particle
        
        return self.age < self.lifetime
    
    def render(self):
        """Draw tiny food cube"""
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        
        # Brown/tan color for food
        glColor3f(0.7, 0.5, 0.2)
        
        s = self.size
        glBegin(GL_QUADS)
        # Front
        glVertex3f(-s, -s, s)
        glVertex3f(s, -s, s)
        glVertex3f(s, s, s)
        glVertex3f(-s, s, s)
        # Back
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, -s, -s)
        # Top
        glVertex3f(-s, s, -s)
        glVertex3f(-s, s, s)
        glVertex3f(s, s, s)
        glVertex3f(s, s, -s)
        # Bottom
        glVertex3f(-s, -s, -s)
        glVertex3f(s, -s, -s)
        glVertex3f(s, -s, s)
        glVertex3f(-s, -s, s)
        # Right
        glVertex3f(s, -s, -s)
        glVertex3f(s, s, -s)
        glVertex3f(s, s, s)
        glVertex3f(s, -s, s)
        # Left
        glVertex3f(-s, -s, -s)
        glVertex3f(-s, -s, s)
        glVertex3f(-s, s, s)
        glVertex3f(-s, s, -s)
        glEnd()
        
        glPopMatrix()


class FoodSystem:
    """Manages all food particles"""
    def __init__(self):
        self.particles = []
        self.spawn_timer = 0
        self.spawn_rate = 3  # Spawn every N frames while feeding
        
    def spawn_food(self, farmer_x, farmer_y, farmer_z, farmer_angle):
        """Spawn food particles from farmer's hand position"""
        # Calculate hand position (in front of farmer)
        angle_rad = math.radians(farmer_angle)
        
        # Offset from farmer center to hand position
        hand_distance = 40  # How far in front
        hand_height = 50    # Height of hand
        
        hand_x = farmer_x + math.sin(angle_rad) * hand_distance
        hand_z = farmer_z + math.cos(angle_rad) * hand_distance
        hand_y = farmer_y + hand_height
        
        # Spawn 2-4 particles at once
        for _ in range(random.randint(2, 4)):
            # Add some randomness to spawn position
            px = hand_x + random.uniform(-5, 5)
            py = hand_y + random.uniform(-3, 3)
            pz = hand_z + random.uniform(-5, 5)
            
            self.particles.append(FoodParticle(px, py, pz))
    
    def update(self, is_feeding, farmer_x, farmer_y, farmer_z, farmer_angle):
        """Update all particles and spawn new ones if feeding"""
        # Spawn new food while feeding
        if is_feeding:
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_rate:
                self.spawn_timer = 0
                self.spawn_food(farmer_x, farmer_y, farmer_z, farmer_angle)
        
        # Update existing particles, remove dead ones
        self.particles = [p for p in self.particles if p.update()]
        
        # Limit max particles to avoid slowdown
        if len(self.particles) > 200:
            self.particles = self.particles[-200:]
    
    def render(self):
        """Render all food particles"""
        glDisable(GL_LIGHTING)  # Food cubes don't need lighting
        for particle in self.particles:
            particle.render()
        glEnable(GL_LIGHTING)
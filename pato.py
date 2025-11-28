import math
from OpenGL.GL import *
from OpenGL.GLU import *

class Pato:
    def __init__(self, x, z, velocidad=1.0):
        self.x = x
        self.y = 0
        self.z = z
        self.velocidad = velocidad
        self.angulo_rotacion = 0
        
        self.tiempo_animacion = 0
        self.velocidad_animacion = 5.0
        
        self.obj_body = None
        self.obj_pata1 = None
        self.obj_pata2 = None
        self.obj_ala1 = None
        self.obj_ala2 = None
        
        self.limite = 200
        # Peck (eating) animation state
        self.pecking = False
        self.peck_timer = 0
        self.peck_duration = 20  # frames
        # Maximum rotation angle for pecking (in degrees)
        self.peck_angle_max = 45.0
        self._peck_angle = 0.0
        
    def cargar_objetos(self, objetos_dict):
        self.obj_body = objetos_dict.get('body')
        self.obj_pata1 = objetos_dict.get('pata1')
        self.obj_pata2 = objetos_dict.get('pata2')
        self.obj_ala1 = objetos_dict.get('ala1')
        self.obj_ala2 = objetos_dict.get('ala2')
        
    def actualizar(self, moviendo=False):
        if moviendo:
            self.tiempo_animacion += self.velocidad_animacion
            if self.tiempo_animacion > 360:
                self.tiempo_animacion = 0
        # actualizar picoteo
        if self.pecking:
            self.peck_timer += 1
            t = self.peck_timer / float(self.peck_duration)
            if t <= 1.0:
                # smooth in/out using sine half-wave
                factor = math.sin(t * math.pi)
                self._peck_angle = factor * self.peck_angle_max
            else:
                self.pecking = False
                self.peck_timer = 0
                self._peck_angle = 0.0
                
    def mover(self, direccion_x, direccion_z):
        # Move relative to the current facing direction
        angulo_rad = math.radians(self.angulo_rotacion)
        cos_ang = math.cos(angulo_rad)
        sin_ang = math.sin(angulo_rad)

        # Transform local movement to world-space
        dx = direccion_z * sin_ang + direccion_x * cos_ang
        dz = direccion_z * cos_ang - direccion_x * sin_ang

        nueva_x = self.x + dx * self.velocidad
        nueva_z = self.z + dz * self.velocidad

        if -self.limite <= nueva_x <= self.limite:
            self.x = nueva_x
        if -self.limite <= nueva_z <= self.limite:
            self.z = nueva_z

    def rotar(self, direccion):
        self.angulo_rotacion = (self.angulo_rotacion + direccion * 5) % 360
        
    def dibujar(self):
        glPushMatrix()
        
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angulo_rotacion + 180, 0, 1, 0)
        
        # Dibujar cuerpo
        if self.obj_body:
            glPushMatrix()
            peck_angle = getattr(self, '_peck_angle', 0.0)
            glTranslatef(0.0, 0.3, -0.3)
            glRotatef(-peck_angle, 1, 0, 0)
            glTranslatef(0.0, -0.3, 0.3)
            glRotatef(-90, 1, 0, 0)
            glScalef(100.0, 100.0, 100.0)
            self.obj_body.render()
            glPopMatrix()
        
        # Dibujar pata1
        if self.obj_pata1:
            glPushMatrix()
            glTranslatef(-0.5, 0, 0)
            angulo_pata = math.sin(math.radians(self.tiempo_animacion)) * 15
            glRotatef(angulo_pata, 1, 0, 0)
            glTranslatef(0.5, 0, 0)
            glRotatef(-90, 1, 0, 0)
            glScalef(100.0, 100.0, 100.0)
            self.obj_pata1.render()
            glPopMatrix()
        
        # Dibujar pata2
        if self.obj_pata2:
            glPushMatrix()
            glTranslatef(0.5, 0, 0)
            angulo_pata = math.sin(math.radians(self.tiempo_animacion + 180)) * 15
            glRotatef(angulo_pata, 1, 0, 0)
            glTranslatef(-0.5, 0, 0)
            glRotatef(-90, 1, 0, 0)
            glScalef(100.0, 100.0, 100.0)
            self.obj_pata2.render()
            glPopMatrix()
        
        # Dibujar ala1 (aleteo) - FIXED PIVOT
        if self.obj_ala1:
            glPushMatrix()
            # Apply peck transform
            peck_angle = getattr(self, '_peck_angle', 0.0)
            glTranslatef(0.0, 0.3, -0.3)
            glRotatef(-peck_angle, 1, 0, 0)
            glTranslatef(0.0, -0.3, 0.3)
            
            # Position wing at body - no rotation pivot tricks, just place it
            glTranslatef(0.0, 0.15, 0)  # Slight height offset
            
            # Small flap angle to keep it subtle
            angulo_ala = math.sin(math.radians(self.tiempo_animacion * 3)) * 10
            glRotatef(angulo_ala, 0, 0, 1)
            
            glRotatef(-90, 1, 0, 0)
            glScalef(100.0, 100.0, 100.0)
            self.obj_ala1.render()
            glPopMatrix()
        
        # Dibujar ala2 (aleteo opuesto) - FIXED PIVOT
        if self.obj_ala2:
            glPushMatrix()
            # Apply peck transform
            peck_angle = getattr(self, '_peck_angle', 0.0)
            glTranslatef(0.0, 0.3, -0.3)
            glRotatef(-peck_angle, 1, 0, 0)
            glTranslatef(0.0, -0.3, 0.3)
            
            # Position wing at body - no rotation pivot tricks, just place it
            glTranslatef(0.0, 0.15, 0)  # Slight height offset
            
            # Small flap angle opposite direction
            angulo_ala = math.sin(math.radians(self.tiempo_animacion * 3)) * -10
            glRotatef(angulo_ala, 0, 0, 1)
            
            glRotatef(-90, 1, 0, 0)
            glScalef(100.0, 100.0, 100.0)
            self.obj_ala2.render()
            glPopMatrix()
        
        glPopMatrix()

    def start_peck(self):
        """Start a single peck animation (no-op if already pecking)."""
        if not self.pecking:
            self.pecking = True
            self.peck_timer = 0
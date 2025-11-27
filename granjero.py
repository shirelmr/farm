import math
from OpenGL.GL import *
from OpenGL.GLU import *

class Granjero:
    def __init__(self, x, z, velocidad=8.0):
        self.x = x
        self.y = 0  # ← AL NIVEL DEL SUELO (era 100)
        self.z = z
        self.velocidad = velocidad
        self.angulo_rotacion = 0
        
        # Animation
        self.tiempo_animacion = 0
        self.velocidad_animacion = 0.08
        self.moviendo = False
        
        # Estados del granjero
        self.feeding = False
        self.collecting_wheat = False
        self.herding_mode = False
        
        # Animación de brazos para acciones
        self.feeding_arm_angle = 0.0
        self.feeding_arm_speed = 3.0  # ← MÁS LENTO (era 5.0)
        
        # Objetos 3D
        self.obj_body = None
        self.obj_arm_right = None
        self.obj_arm_left = None
        self.obj_leg_right = None
        self.obj_leg_left = None
        
        self.limite = 400  # Límites de movimiento
        
    def cargar_objetos(self, objetos_dict):
        """Carga los modelos 3D del granjero"""
        self.obj_body = objetos_dict.get('farmer_body')
        self.obj_arm_right = objetos_dict.get('farmer_arm_right')
        self.obj_arm_left = objetos_dict.get('farmer_arm_left')
        self.obj_leg_right = objetos_dict.get('farmer_leg_right')
        self.obj_leg_left = objetos_dict.get('farmer_leg_left')
    
    def _draw_simple_cube(self):
        """Dibuja un cubo simple como fallback si no hay modelo 3D"""
        glBegin(GL_QUADS)
        # Frente
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        # Atrás
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        # Arriba
        glVertex3f(-0.5, 0.5, -0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, 0.5, -0.5)
        # Abajo
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, -0.5, 0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        # Derecha
        glVertex3f(0.5, -0.5, -0.5)
        glVertex3f(0.5, 0.5, -0.5)
        glVertex3f(0.5, 0.5, 0.5)
        glVertex3f(0.5, -0.5, 0.5)
        # Izquierda
        glVertex3f(-0.5, -0.5, -0.5)
        glVertex3f(-0.5, -0.5, 0.5)
        glVertex3f(-0.5, 0.5, 0.5)
        glVertex3f(-0.5, 0.5, -0.5)
        glEnd()
        
    def actualizar(self, moviendo=False):
        """Actualiza la animación del granjero"""
        self.moviendo = moviendo
        if moviendo:
            self.tiempo_animacion += self.velocidad_animacion
            if self.tiempo_animacion > 2 * math.pi:
                self.tiempo_animacion = 0
        
        # Actualizar animación del brazo cuando está alimentando
        if self.feeding:
            # Extender brazo gradualmente hacia adelante (máximo 45 grados)
            if self.feeding_arm_angle < 45.0:  # ← REDUCIDO A 45 (era 60)
                self.feeding_arm_angle += self.feeding_arm_speed
                if self.feeding_arm_angle > 45.0:
                    self.feeding_arm_angle = 45.0
        else:
            # Regresar brazo a posición normal
            if self.feeding_arm_angle > 0.0:
                self.feeding_arm_angle -= self.feeding_arm_speed
                if self.feeding_arm_angle < 0.0:
                    self.feeding_arm_angle = 0.0
                
    def mover(self, dx, dz):
        """Mueve el granjero en las direcciones especificadas"""
        nueva_x = self.x + dx
        nueva_z = self.z + dz
        
        # Mantener dentro de los límites
        if -self.limite <= nueva_x <= self.limite:
            self.x = nueva_x
        if -self.limite <= nueva_z <= self.limite:
            self.z = nueva_z
            
        # Calcular ángulo de rotación basado en dirección de movimiento
        if abs(dx) > 0.1 or abs(dz) > 0.1:
            self.angulo_rotacion = math.degrees(math.atan2(dx, dz))
        
    def dibujar(self):
        """Dibuja el granjero con animación"""
        glPushMatrix()
        
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.angulo_rotacion, 0, 1, 0)
        
        # Color según estado
        if self.feeding:
            glColor3f(0.0, 1.0, 0.0)  # Verde cuando alimenta
        elif self.collecting_wheat:
            glColor3f(1.0, 1.0, 0.0)  # Amarillo cuando recolecta
        elif self.herding_mode:
            glColor3f(0.0, 0.5, 1.0)  # Azul en modo pastor
        else:
            glColor3f(1.0, 1.0, 1.0)  # Blanco normal
        
        scale = 25.0
        glScalef(scale, scale, scale)
        
        # Dibujar cuerpo (siempre fijo)
        if self.obj_body:
            glPushMatrix()
            self.obj_body.render()
            glPopMatrix()
        else:
            # Fallback: dibujar un cubo simple si no hay modelo
            self._draw_simple_cube()
        
        # Brazo derecho - SE EXTIENDE HACIA ADELANTE CUANDO ALIMENTA
        if self.obj_arm_right:
            glPushMatrix()
            # MOVEMOS EL PIVOTE AL HOMBRO antes de rotar
            glTranslatef(0.0, 0.6, 0.0)  # Mover pivote al hombro (ajusta según tu modelo)
            glRotatef(-self.feeding_arm_angle, 1, 0, 0)  # Rotar hacia adelante
            glTranslatef(0.0, -0.6, 0.0)  # Regresar pivote
            self.obj_arm_right.render()
            glPopMatrix()
        
        # Brazo izquierdo - SIEMPRE ESTATICO
        if self.obj_arm_left:
            glPushMatrix()
            self.obj_arm_left.render()
            glPopMatrix()
        
        # Animación de piernas - MOVIMIENTO MINIMO (solo cuando camina)
        if self.moviendo:
            leg_swing = math.sin(self.tiempo_animacion) * 5
        else:
            leg_swing = 0
        
        # Pierna derecha
        if self.obj_leg_right:
            glPushMatrix()
            glRotatef(leg_swing, 1, 0, 0)
            self.obj_leg_right.render()
            glPopMatrix()
        
        # Pierna izquierda (movimiento opuesto)
        if self.obj_leg_left:
            glPushMatrix()
            glRotatef(-leg_swing, 1, 0, 0)
            self.obj_leg_left.render()
            glPopMatrix()
        
        glPopMatrix()
import math
from OpenGL.GL import *
from OpenGL.GLU import *

class Granjero:
    def __init__(self, x, z, velocidad=8.0):
        self.x = x
        self.y = 0  # AL NIVEL DEL SUELO
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
        self.feeding_arm_speed = 4.0
        self.arm_swing_angle = 0.0
        self.arm_swing_speed = 12.0
        self.action_intensity = 1.0
        
        # Objetos 3D
        self.obj_body = None
        self.obj_arm_right = None
        self.obj_arm_left = None
        self.obj_leg_right = None
        self.obj_leg_left = None
        
        self.limite = 400
        
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
            self.arm_swing_angle += self.arm_swing_speed
            if self.arm_swing_angle > 360:
                self.arm_swing_angle = 0
        else:
            self.arm_swing_angle = 0.0
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
        
        # Raise farmer up so he's not sinking into ground
        glTranslatef(self.x, self.y + 30, self.z)
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
        
        # ENORMOUS FARMER!
        scale = 150.0
        glScalef(scale, scale, scale)
        
        # Dibujar cuerpo (siempre fijo)
        if self.obj_body:
            glPushMatrix()
            self.obj_body.render()
            glPopMatrix()
        else:
            self._draw_simple_cube()
        
        # Brazo derecho - PIVOTE EN EL HOMBRO
        if self.obj_arm_right:
            glPushMatrix()
            
            shoulder_offset_x = 0.6
            shoulder_offset_y = 1.2
            shoulder_offset_z = 0.0
            
            glTranslatef(shoulder_offset_x, shoulder_offset_y, shoulder_offset_z)
            
            if self.feeding:
                # Arm extends slightly forward and stays there
                forward_extend = -15  # Subtle forward extension
                glRotatef(forward_extend, 1, 0, 0)
                
            elif self.collecting_wheat:
                collection_phase = self.tiempo_animacion * 4
                collect_swing = 30 + math.sin(collection_phase) * 15
                glRotatef(collect_swing, 1, 0, 0)
                
            elif self.herding_mode:
                # No hay animación especial en modo herding, solo mantener brazo normal
                pass
            
            glTranslatef(-shoulder_offset_x, -shoulder_offset_y, -shoulder_offset_z)
            
            self.obj_arm_right.render()
            glPopMatrix()
        
        # Brazo izquierdo - SIEMPRE ESTATICO
        if self.obj_arm_left:
            glPushMatrix()
            self.obj_arm_left.render()
            glPopMatrix()
        
        # Piernas - Animación de caminar realista
        if self.moviendo:
            # Usar tiempo de animación más rápido para caminar natural
            walk_cycle = self.tiempo_animacion * 4  # Mucho más rápido - de 2 a 4
            leg_swing = math.sin(walk_cycle) * 12  # Movimiento más sutil - 12 grados
        else:
            leg_swing = 0
        
        # Pierna derecha - con pivote en la cadera, más cerca del cuerpo
        if self.obj_leg_right:
            glPushMatrix()
            # Mover al punto de pivote (cadera) - más cerca del centro
            glTranslatef(0.15, 0.8, 0)  # Posición más cerca del cuerpo
            glRotatef(leg_swing, 1, 0, 0)  # Rotación hacia adelante/atrás
            glTranslatef(-0.15, -0.8, 0)  # Regresar al origen
            self.obj_leg_right.render()
            glPopMatrix()
        
        # Pierna izquierda - opuesta a la derecha, más cerca del cuerpo
        if self.obj_leg_left:
            glPushMatrix()
            # Mover al punto de pivote (cadera) - más cerca del centro
            glTranslatef(-0.15, 0.8, 0)  # Posición más cerca del cuerpo
            glRotatef(-leg_swing, 1, 0, 0)  # Rotación opuesta
            glTranslatef(0.15, -0.8, 0)  # Regresar al origen
            self.obj_leg_left.render()
            glPopMatrix()
        
        glPopMatrix()
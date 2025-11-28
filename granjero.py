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
        self.feeding_arm_speed = 4.0
        self.arm_swing_angle = 0.0  # Para movimiento de balanceo lateral
        self.arm_swing_speed = 12.0  # Velocidad del balanceo (más rápido para efecto de golpe)
        self.action_intensity = 1.0  # Intensidad del movimiento
        
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
            # Movimiento de balanceo lateral como si estuviera esparciendo comida
            self.arm_swing_angle += self.arm_swing_speed
            if self.arm_swing_angle > 360:
                self.arm_swing_angle = 0
            
            # # Elevar brazo ligeramente
            # if self.feeding_arm_angle < 30.0:
            #     self.feeding_arm_angle += self.feeding_arm_speed
            #     if self.feeding_arm_angle > 30.0:
            #         self.feeding_arm_angle = 30.0
        else:
            # Regresar brazo a posición normal
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
        
        # Brazo derecho - PIVOTE EN EL HOMBRO
        if self.obj_arm_right:
            glPushMatrix()
            
            # Posición del hombro (AJUSTA ESTOS VALORES según tu modelo)
            shoulder_offset_x = 0.6   # Lado derecho del cuerpo
            shoulder_offset_y = 1.2   # Altura del hombro  
            shoulder_offset_z = 0.0   # Centro en profundidad
            
            # PASO 1: Mover AL punto de pivote (hombro)
            glTranslatef(shoulder_offset_x, shoulder_offset_y, shoulder_offset_z)
            
            # PASO 2: Aplicar rotaciones desde el hombro
            if self.feeding:
                phase = math.radians(self.arm_swing_angle)
                pendulum_motion = math.sin(phase) * 25
                glRotatef(-self.feeding_arm_angle, 1, 0, 0)
                glRotatef(pendulum_motion, 1, 0, 0)
                
            elif self.collecting_wheat:
                collection_phase = self.tiempo_animacion * 4
                collect_swing = 30 + math.sin(collection_phase) * 15
                glRotatef(collect_swing, 1, 0, 0)
                
            elif self.herding_mode:
                herd_phase = self.tiempo_animacion * 1.5
                point_swing = math.sin(herd_phase) * 20
                glRotatef(-15, 1, 0, 0)
                glRotatef(point_swing, 0, 1, 0)
            
            # PASO 3: Compensar el origen del modelo 3D
            # Esto mueve de vuelta desde el hombro al origen del modelo
            glTranslatef(-shoulder_offset_x, -shoulder_offset_y, -shoulder_offset_z)
            
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
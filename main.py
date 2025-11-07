import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math
import requests
import json
import time

from objloader import *
from pato import Pato

# BIGGER WINDOW
screen_width = 1400
screen_height = 900

# Configuración de cámara - BETTER VIEW
FOVY = 60.0
ZNEAR = 0.01
ZFAR = 2000.0
EYE_X = 0.0
EYE_Y = 400.0  # Higher up
EYE_Z = 600.0  # Further back
CENTER_X = 0
CENTER_Y = 0
CENTER_Z = 0
UP_X = 0
UP_Y = 1
UP_Z = 0

# Ejes - BIGGER
X_MIN = -800
X_MAX = 800
Y_MIN = -800
Y_MAX = 800
Z_MIN = -800
Z_MAX = 800
DimBoard = 800  # BIGGER GRID

# Variables para los patos
patos = []
objetos_pato = {}
farm_models = {}
previous_positions = {}

# Variables para el control del observador
theta = 0.0
phi = 30.0  # Vertical angle
radius = 700.0  # Camera distance

pygame.init()

# Cliente REST API
def inicializar_simulacion():
    """Inicializa la simulación en Julia (POST /init)"""
    try:
        response = requests.post("http://localhost:8000/init", timeout=2)
        if response.status_code == 200:
            print("Simulación Julia inicializada correctamente")
            return True
    except Exception as e:
        print(f"Error inicializando simulación: {e}")
    return False

def obtener_posiciones_patos():
    """Obtiene las posiciones actuales de los patos (GET /run)"""
    try:
        response = requests.get("http://localhost:8000/run", timeout=1)
        if response.status_code == 200:
            data = response.json()
            return data['ducks']
    except Exception as e:
        print(f"Error obteniendo posiciones: {e}")
    return None

def julia_to_opengl(julia_x, julia_y):
    """
    Convierte coordenadas de Julia (0-20, 0-15) a OpenGL
    """
    opengl_x = (julia_x - 10.0) * 50.0  # Bigger scaling
    opengl_z = (julia_y - 7.5) * 50.0
    return opengl_x, opengl_z

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    # X axis in red
    glColor3f(1.0, 0.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN, 0.0, 0.0)
    glVertex3f(X_MAX, 0.0, 0.0)
    glEnd()
    # Y axis in green
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, Y_MIN, 0.0)
    glVertex3f(0.0, Y_MAX, 0.0)
    glEnd()
    # Z axis in blue
    glColor3f(0.0, 0.0, 1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0, 0.0, Z_MIN)
    glVertex3f(0.0, 0.0, Z_MAX)
    glEnd()
    glLineWidth(1.0)

def Init():
    global patos, objetos_pato, farm_models
    
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL: 10 Patos con Flocking desde Julia")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOVY, screen_width/screen_height, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)
    glClearColor(0.53, 0.81, 0.92, 1.0)  # Nice sky blue background
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    # Better lighting
    glLightfv(GL_LIGHT0, GL_POSITION, (200, 500, 200, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)
    
    # Cargar objetos del pato
    print("Cargando body.obj...")
    objetos_pato['body'] = OBJ("body.obj", swapyz=True)
    objetos_pato['body'].generate()
    
    print("Cargando pata1.obj...")
    objetos_pato['pata1'] = OBJ("pata1.obj", swapyz=True)
    objetos_pato['pata1'].generate()
    
    print("Cargando pata2.obj...")
    objetos_pato['pata2'] = OBJ("pata2.obj", swapyz=True)
    objetos_pato['pata2'].generate()

    print("Cargando ala1.obj...")
    objetos_pato['ala1'] = OBJ("ala1.obj", swapyz=True)
    objetos_pato['ala1'].generate()

    print("Cargando ala2.obj...")
    objetos_pato['ala2'] = OBJ("ala2.obj", swapyz=True)
    objetos_pato['ala2'].generate()

    print("Objetos cargados correctamente!")
    
    # Cargar modelos de la granja
    print("Cargando modelos de la granja...")
    
    try:
        farm_models['farm'] = OBJ("farm.obj", swapyz=False)  # Try without swapyz
        farm_models['farm'].generate()
        print("✓ farm.obj cargado")
    except:
        print("✗ No se pudo cargar farm.obj")
    
    try:
        farm_models['granja'] = OBJ("granja.obj", swapyz=False)
        farm_models['granja'].generate()
        print("✓ granja.obj cargado")
    except:
        print("✗ No se pudo cargar granja.obj")
    
    try:
        farm_models['gallinero'] = OBJ("gallinero.obj", swapyz=False)
        farm_models['gallinero'].generate()
        print("✓ gallinero.obj cargado")
    except:
        print("✗ No se pudo cargar gallinero.obj")
    
    try:
        farm_models['molino'] = OBJ("molino.obj", swapyz=False)
        farm_models['molino'].generate()
        print("✓ molino.obj cargado")
    except:
        print("✗ No se pudo cargar molino.obj")
    
    try:
        farm_models['trigo'] = OBJ("trigo.obj", swapyz=False)
        farm_models['trigo'].generate()
        print("✓ trigo.obj cargado")
    except:
        print("✗ No se pudo cargar trigo.obj")
    
    try:
        farm_models['sembradero'] = OBJ("sembradero1.obj", swapyz=False)
        farm_models['sembradero'].generate()
        print("✓ sembradero1.obj cargado")
    except:
        print("✗ No se pudo cargar sembradero1.obj")
    
    print("Modelos de granja cargados!")
    
    # Crear 10 patos
    for i in range(10):
        nuevo_pato = Pato(0, 0, velocidad=2.0)
        nuevo_pato.cargar_objetos(objetos_pato)
        patos.append(nuevo_pato)
        previous_positions[i+1] = (0, 0)
    
    print(f"Creados {len(patos)} patos")

def lookat():
    global EYE_X, EYE_Y, EYE_Z, radius, theta, phi
    # Spherical coordinates for better camera control
    phi_rad = math.radians(phi)
    theta_rad = math.radians(theta)
    
    EYE_X = radius * math.sin(phi_rad) * math.sin(theta_rad)
    EYE_Y = radius * math.cos(phi_rad)
    EYE_Z = radius * math.sin(phi_rad) * math.cos(theta_rad)
    
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
    
    # Draw BIGGER green ground
    glColor3f(0.2, 0.7, 0.2)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    
    # Farm models - FIXED positions and rotations
    if farm_models.get('granja'):
        glPushMatrix()
        glTranslatef(-200, 0, -150)
        glRotatef(0, 0, 1, 0)  # Rotate to face correctly
        glScalef(30, 30, 30)
        farm_models['granja'].render()
        glPopMatrix()

    if farm_models.get('gallinero'):
        glPushMatrix()
        glTranslatef(150, 0, -180)
        glRotatef(45, 0, 1, 0)
        glScalef(25, 25, 25)
        farm_models['gallinero'].render()
        glPopMatrix()

    if farm_models.get('molino'):
        glPushMatrix()
        glTranslatef(-180, 0, 150)
        glRotatef(0, 0, 1, 0)
        glScalef(35, 35, 35)
        farm_models['molino'].render()
        glPopMatrix()

    if farm_models.get('sembradero'):
        glPushMatrix()
        glTranslatef(180, 0, 120)
        glRotatef(0, 0, 1, 0)
        glScalef(28, 28, 28)
        farm_models['sembradero'].render()
        glPopMatrix()

    if farm_models.get('trigo'):
        # Multiple wheat patches
        positions = [(120, 0, 80), (150, 0, 100), (200, 0, 90), 
                     (-150, 0, 80), (-120, 0, 100)]
        for pos in positions:
            glPushMatrix()
            glTranslatef(*pos)
            glScalef(15, 15, 15)
            farm_models['trigo'].render()
            glPopMatrix()

    if farm_models.get('farm'):
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glRotatef(0, 0, 1, 0)
        glScalef(40, 40, 40)
        farm_models['farm'].render()
        glPopMatrix()
    
    # Draw ducks
    for pato in patos:
        pato.dibujar()

# Inicialización
done = False
Init()

print("Conectando con servidor Julia...")
if not inicializar_simulacion():
    print("ERROR: No se pudo conectar con Julia!")
    print("Asegúrate de que el servidor Julia esté corriendo en localhost:8000")
    done = True

print("Programa iniciado. 10 patos con flocking desde Julia!")
print("Usa flechas para rotar cámara. W/S para zoom. ESC para salir.")

# Main loop
last_julia_call = time.time()
julia_call_frequency = 0.1  # Call Julia 10 times per second (slower for now)
clock = pygame.time.Clock()

while not done:
    current_time = time.time()
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    
    # Camera controls
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        theta = (theta + 2.0) % 360
        lookat()
    if keys[pygame.K_LEFT]:
        theta = (theta - 2.0) % 360
        lookat()
    if keys[pygame.K_UP]:
        phi = max(10, phi - 1.0)  # Don't go below horizon
        lookat()
    if keys[pygame.K_DOWN]:
        phi = min(80, phi + 1.0)  # Don't flip upside down
        lookat()
    if keys[pygame.K_w]:
        radius = max(200, radius - 10)  # Zoom in
        lookat()
    if keys[pygame.K_s]:
        radius = min(1200, radius + 10)  # Zoom out
        lookat()
    
    # Call Julia
    if current_time - last_julia_call >= julia_call_frequency:
        last_julia_call = current_time
        
        datos_patos = obtener_posiciones_patos()
        if datos_patos:
            for datos in datos_patos:
                duck_id = datos['id']
                julia_pos = datos['pos']
                
                new_x, new_z = julia_to_opengl(julia_pos[0], julia_pos[1])
                old_x, old_z = previous_positions.get(duck_id, (new_x, new_z))
                
                dx = new_x - old_x
                dz = new_z - old_z
                distance = math.sqrt(dx*dx + dz*dz)
                is_moving = distance > 0.5
                
                pato_index = duck_id - 1
                if 0 <= pato_index < len(patos):
                    patos[pato_index].x = new_x
                    patos[pato_index].z = new_z
                    
                    if is_moving:
                        angle = math.degrees(math.atan2(dx, dz))
                        patos[pato_index].angulo_rotacion = angle
                    
                    patos[pato_index].actualizar(moviendo=is_moving)
                    previous_positions[duck_id] = (new_x, new_z)
    
    # Update animations
    for pato in patos:
        pato.actualizar(moviendo=True)

    # Render
    display()
    pygame.display.flip()
    
    clock.tick(60)

pygame.quit()
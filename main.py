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

screen_width = 800
screen_height = 600

# Configuración de cámara
FOVY = 60.0
ZNEAR = 0.01
ZFAR = 900.0
EYE_X = 300.0
EYE_Y = 200.0
EYE_Z = 300.0
CENTER_X = 0
CENTER_Y = 0
CENTER_Z = 0
UP_X = 0
UP_Y = 1
UP_Z = 0

# Ejes
X_MIN = -500
X_MAX = 500
Y_MIN = -500
Y_MAX = 500
Z_MIN = -500
Z_MAX = 500
DimBoard = 500  # Grid más grande

# Variables para los patos
patos = []  # Lista de patos
objetos_pato = {}
farm_models = {}
previous_positions = {}  # Para calcular el ángulo de rotación

# Variables para el control del observador
theta = 0.0
radius = 600  # Cámara más lejos para ver todo

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
            return data['ducks']  # Julia devuelve {"ducks": [...]}
    except Exception as e:
        print(f"Error obteniendo posiciones: {e}")
    return None

def julia_to_opengl(julia_x, julia_y):
    """
    Convierte coordenadas de Julia (0-20, 0-15) a OpenGL
    Mapeamos a un espacio más grande para que se vea bien
    """
    # Centrar en (10, 7.5) y escalar por 40 (MÁS GRANDE)
    opengl_x = (julia_x - 10.0) * 40.0
    opengl_z = (julia_y - 7.5) * 40.0
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
    glClearColor(0, 0, 0, 0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    
    # Iluminación
    glLightfv(GL_LIGHT0, GL_POSITION, (0, 200, 0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.5, 0.5, 0.5, 1.0))
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
        farm_models['farm'] = OBJ("farm.obj", swapyz=True)
        farm_models['farm'].generate()
        print("✓ farm.obj cargado")
    except:
        print("✗ No se pudo cargar farm.obj")
    
    try:
        farm_models['granja'] = OBJ("granja.obj", swapyz=True)
        farm_models['granja'].generate()
        print("✓ granja.obj cargado")
    except:
        print("✗ No se pudo cargar granja.obj")
    
    try:
        farm_models['gallinero'] = OBJ("gallinero.obj", swapyz=True)
        farm_models['gallinero'].generate()
        print("✓ gallinero.obj cargado")
    except:
        print("✗ No se pudo cargar gallinero.obj")
    
    try:
        farm_models['molino'] = OBJ("molino.obj", swapyz=True)
        farm_models['molino'].generate()
        print("✓ molino.obj cargado")
    except:
        print("✗ No se pudo cargar molino.obj")
    
    try:
        farm_models['trigo'] = OBJ("trigo.obj", swapyz=True)
        farm_models['trigo'].generate()
        print("✓ trigo.obj cargado")
    except:
        print("✗ No se pudo cargar trigo.obj")
    
    try:
        farm_models['sembradero'] = OBJ("sembradero1.obj", swapyz=True)
        farm_models['sembradero'].generate()
        print("✓ sembradero1.obj cargado")
    except:
        print("✗ No se pudo cargar sembradero1.obj")
    
    print("Modelos de granja cargados!")
    
    # Crear 10 patos (Julia inicializa con n_ducks=10)
    for i in range(10):
        nuevo_pato = Pato(0, 0, velocidad=2.0)
        nuevo_pato.cargar_objetos(objetos_pato)
        patos.append(nuevo_pato)
        previous_positions[i+1] = (0, 0)  # Inicializar posiciones previas
    
    print(f"Creados {len(patos)} patos")

def lookat():
    global EYE_X, EYE_Z, radius
    EYE_X = radius * (math.cos(math.radians(theta)) + math.sin(math.radians(theta)))
    EYE_Z = radius * (-math.sin(math.radians(theta)) + math.cos(math.radians(theta)))
    glLoadIdentity()
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
    
    # Dibujar el plano VERDE (como pasto)
    glColor3f(0.2, 0.6, 0.2)
    glBegin(GL_QUADS)
    glVertex3d(-DimBoard, 0, -DimBoard)
    glVertex3d(-DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, DimBoard)
    glVertex3d(DimBoard, 0, -DimBoard)
    glEnd()
    
    # Dibujar modelos de la granja con posiciones específicas
    # Granja principal (barn) - centro-izquierda
    if farm_models.get('granja'):
        glPushMatrix()
        glTranslatef(-150, 0, -100)
        glScalef(20, 20, 20)
        farm_models['granja'].render()
        glPopMatrix()

    # Gallinero (chicken coop) - arriba-derecha
    if farm_models.get('gallinero'):
        glPushMatrix()
        glTranslatef(100, 0, -120)
        glScalef(15, 15, 15)
        farm_models['gallinero'].render()
        glPopMatrix()

    # Molino (windmill) - esquina superior izquierda
    if farm_models.get('molino'):
        glPushMatrix()
        glTranslatef(-120, 0, 100)
        glScalef(25, 25, 25)
        farm_models['molino'].render()
        glPopMatrix()

    # Sembradero (planter/field) - abajo-derecha
    if farm_models.get('sembradero'):
        glPushMatrix()
        glTranslatef(120, 0, 80)
        glScalef(18, 18, 18)
        farm_models['sembradero'].render()
        glPopMatrix()

    # Trigo (wheat) - esparcido en varias posiciones
    if farm_models.get('trigo'):
        # Trigo 1
        glPushMatrix()
        glTranslatef(80, 0, 50)
        glScalef(10, 10, 10)
        farm_models['trigo'].render()
        glPopMatrix()
        
        # Trigo 2
        glPushMatrix()
        glTranslatef(100, 0, 70)
        glScalef(10, 10, 10)
        farm_models['trigo'].render()
        glPopMatrix()
        
        # Trigo 3
        glPushMatrix()
        glTranslatef(140, 0, 60)
        glScalef(10, 10, 10)
        farm_models['trigo'].render()
        glPopMatrix()

    # Farm (si es cercado o decoración) - alrededor
    if farm_models.get('farm'):
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glScalef(30, 30, 30)
        farm_models['farm'].render()
        glPopMatrix()
    
    # Dibujar todos los patos
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
print("Usa flechas para rotar cámara. ESC para salir.")

# Main loop
last_julia_call = time.time()
julia_call_frequency = 0.033  # Call Julia 30 times per second (every 33ms)

while not done:
    current_time = time.time()
    
    keys = pygame.key.get_pressed()
    
    # Control de cámara (flechas)
    if keys[pygame.K_RIGHT]:
        theta = (theta + 1.0) % 360
        lookat()
    if keys[pygame.K_LEFT]:
        theta = (theta - 1.0) % 360
        lookat()
    
    # Obtener posiciones desde Julia - basado en TIEMPO no en frames
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
    
    # Actualizar animaciones de patos cada frame
    for pato in patos:
        pato.actualizar(moviendo=True)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
        if event.type == pygame.QUIT:
            done = True

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()
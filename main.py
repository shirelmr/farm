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
from granjero import Granjero

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
X_MIN = -1000
X_MAX = 1000
Y_MIN = -1000
Y_MAX = 1000
Z_MIN = -1000
Z_MAX = 1000
DimBoard = 1000  # EVEN BIGGER GRID

# Variables para los patos
patos = []
objetos_pato = {}
farm_models = {}
previous_positions = {}
smooth_positions = {}  # Para interpolación suave

# Variables para el granjero
granjero = None  # Se inicializará en Init()

def print_controls():
    """Imprime los controles del granjero en consola"""
    print("\n=== CONTROLES DEL GRANJERO ===")
    print("Movimiento:")
    print("  Q/E - Adelante/Atrás")
    print("  A/D - Izquierda/Derecha")
    print("\nAcciones:")
    print("  SPACE - Alimentar patos (verde)")
    print("  T - Recolectar trigo (amarillo)")
    print("  H - Modo pastor/corral (azul)")
    print("\nCámara:")
    print("  Flechas - Rotar cámara")
    print("  W/S - Zoom in/out")
    print("===============================\n")

# Variables para el control del observador
theta = 0.0
phi = 30.0  # Vertical angle
radius = 700.0  # Camera distance

pygame.init()
print_controls()

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
    """Obtiene las posiciones actuales de los patos y granjero (GET /run)"""
    try:
        response = requests.get("http://localhost:8000/run", timeout=0.03)  # Very short timeout
        if response.status_code == 200:
            data = response.json()
            return data.get('ducks'), data.get('farmer')
    except:
        # Silent fail - just skip this update, interpolation will continue smoothly
        pass
    return None, None

def julia_to_opengl(julia_x, julia_y):
    """
    Convierte coordenadas de Julia (0-20, 0-15) a OpenGL
    """
    opengl_x = (julia_x - 10.0) * 50.0  # Bigger scaling
    opengl_z = (julia_y - 7.5) * 50.0
    return opengl_x, opengl_z

def opengl_to_julia(opengl_x, opengl_z):
    """
    Convierte coordenadas de OpenGL a Julia
    """
    julia_x = (opengl_x / 50.0) + 10.0
    julia_y = (opengl_z / 50.0) + 7.5
    return julia_x, julia_y

def update_farmer_position(x, z, feeding, collecting_wheat=False, herding_mode=False):
    """Envía la posición del granjero a Julia"""
    try:
        julia_x, julia_y = opengl_to_julia(x, z)
        
        # Mantener granjero dentro de los límites
        julia_x = max(0, min(20, julia_x))
        julia_y = max(0, min(15, julia_y))
        
        data = {
            "x": julia_x,
            "y": julia_y,
            "feeding": feeding,
            "collecting_wheat": collecting_wheat,
            "herding_mode": herding_mode
        }
        
        response = requests.post("http://localhost:8000/farmer", 
                               json=data, timeout=0.03)
    except:
        pass  # Silent fail para mantener fluidez

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
    global patos, objetos_pato, farm_models, granjero
    
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
        farm_models['farm'] = OBJ("farm.obj", swapyz=False)
        farm_models['farm'].generate()
        print("✓ farm.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar farm.obj: {e}")
    
    try:
        farm_models['granja'] = OBJ("granja.obj", swapyz=False)
        farm_models['granja'].generate()
        print("✓ granja.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar granja.obj: {e}")
    
    try:
        farm_models['gallinero'] = OBJ("gallinero.obj", swapyz=False)
        farm_models['gallinero'].generate()
        print("✓ gallinero.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar gallinero.obj: {e}")
    
    try:
        farm_models['molino'] = OBJ("molino.obj", swapyz=False)
        farm_models['molino'].generate()
        print("✓ molino.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar molino.obj: {e}")
    
    try:
        farm_models['trigo'] = OBJ("trigo.obj", swapyz=False)
        farm_models['trigo'].generate()
        print("✓ trigo.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar trigo.obj: {e}")
    
    try:
        farm_models['sembradero'] = OBJ("sembradero1.obj", swapyz=False)
        farm_models['sembradero'].generate()
        print("✓ sembradero1.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar sembradero1.obj: {e}")
    
    print("Modelos de granja cargados!")
    
    # Cargar modelos del granjero
    print("Cargando modelos del granjero...")
    objetos_granjero = {}
    
    try:
        objetos_granjero['farmer_body'] = OBJ("granjero/farmer.obj", swapyz=False)
        objetos_granjero['farmer_body'].generate()
        print("✓ farmer.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar farmer.obj: {e}")
    
    try:
        objetos_granjero['farmer_arm_right'] = OBJ("granjero/arm_derecho.obj", swapyz=False)
        objetos_granjero['farmer_arm_right'].generate()
        print("✓ arm_derecho.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar arm_derecho.obj: {e}")
    
    try:
        objetos_granjero['farmer_arm_left'] = OBJ("granjero/arm_izquierdo.obj", swapyz=False)
        objetos_granjero['farmer_arm_left'].generate()
        print("✓ arm_izquierdo.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar arm_izquierdo.obj: {e}")
    
    try:
        objetos_granjero['farmer_leg_right'] = OBJ("granjero/pie_derecho.obj", swapyz=False)
        objetos_granjero['farmer_leg_right'].generate()
        print("✓ pie_derecho.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar pie_derecho.obj: {e}")
    
    try:
        objetos_granjero['farmer_leg_left'] = OBJ("granjero/pie_izquierdo.obj", swapyz=False)
        objetos_granjero['farmer_leg_left'].generate()
        print("✓ pie_izquierdo.obj cargado")
    except Exception as e:
        print(f"✗ No se pudo cargar pie_izquierdo.obj: {e}")
    
    print("Modelos del granjero cargados!")
    
    # Crear granjero
    granjero = Granjero(0.0, 0.0, velocidad=8.0)
    granjero.cargar_objetos(objetos_granjero)
    print("Granjero creado!")
    
    # Crear 10 patos
    for i in range(10):
        nuevo_pato = Pato(0, 0, velocidad=2.0)
        nuevo_pato.cargar_objetos(objetos_pato)
        patos.append(nuevo_pato)
        previous_positions[i+1] = (0, 0)
        smooth_positions[i+1] = (0, 0)
    
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
    
    # Farm models
    if farm_models.get('molino'):
        glPushMatrix()
        glTranslatef(-180, 0, 150)
        glRotatef(0, 0, 1, 0)
        glScalef(15, 15, 15)
        farm_models['molino'].render()
        glPopMatrix()

    if farm_models.get('farm'):
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glRotatef(0, 0, 1, 0)
        glScalef(15, 15, 15)
        farm_models['farm'].render()
        glPopMatrix()

    if farm_models.get('gallinero'):
        glPushMatrix()
        glTranslatef(800, 0, 10)
        glRotatef(45, 0, 1, 0)
        glScalef(15, 15, 15)
        farm_models['gallinero'].render()
        glPopMatrix()
    
    # Draw farmer
    if granjero:
        granjero.dibujar()
    
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
print("Controles:")
print("- Flechas: Rotar cámara")
print("- W/S: Zoom")
print("- A/D: Mover granjero izquierda/derecha")
print("- Q/E: Mover granjero adelante/atrás") 
print("- ESPACIO: Dar de comer a los patos")
print("- T: Recolectar trigo")
print("- H: Modo pastor")
print("- ESC: Salir")

# Main loop
last_julia_call = time.time()
julia_call_frequency = 0.033  # Call Julia 30 times per second (smoother)
clock = pygame.time.Clock()
frame_count = 0
last_fps_display = time.time()

while not done:
    current_time = time.time()
    frame_count += 1
    
    # Display FPS every second for debugging
    if current_time - last_fps_display >= 1.0:
        fps = frame_count / (current_time - last_fps_display)
        print(f"FPS: {fps:.1f}")
        frame_count = 0
        last_fps_display = current_time
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    
    # Guardar posición anterior del granjero
    old_x = granjero.x
    old_z = granjero.z
    
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
    
    # Farmer controls
    dx = 0
    dz = 0
    
    if keys[pygame.K_a]:  # Izquierda
        dx -= granjero.velocidad
    if keys[pygame.K_d]:  # Derecha
        dx += granjero.velocidad
    if keys[pygame.K_q]:  # Adelante
        dz -= granjero.velocidad
    if keys[pygame.K_e]:  # Atrás
        dz += granjero.velocidad
    
    # Mover granjero
    if dx != 0 or dz != 0:
        granjero.mover(dx, dz)
    
    # Detectar movimiento
    moviendo = (abs(granjero.x - old_x) > 0.1 or abs(granjero.z - old_z) > 0.1)
    granjero.actualizar(moviendo=moviendo)
    
    # Farmer actions
    granjero.feeding = keys[pygame.K_SPACE]
    granjero.collecting_wheat = keys[pygame.K_t]
    granjero.herding_mode = keys[pygame.K_h]
    
    # Update farmer position in Julia
    update_farmer_position(granjero.x, granjero.z, granjero.feeding, 
                          granjero.collecting_wheat, granjero.herding_mode)
    
    # Call Julia
    if current_time - last_julia_call >= julia_call_frequency:
        last_julia_call = current_time
        
        datos_patos, datos_granjero = obtener_posiciones_patos()
        if datos_patos:
            for datos in datos_patos:
                duck_id = datos['id']
                julia_pos = datos['pos']
                
                new_x, new_z = julia_to_opengl(julia_pos[0], julia_pos[1])
                
                # Initialize smooth position if not exists
                if duck_id not in smooth_positions:
                    smooth_positions[duck_id] = (new_x, new_z)
                
                old_x, old_z = previous_positions.get(duck_id, (new_x, new_z))
                
                dx = new_x - old_x
                dz = new_z - old_z
                distance = math.sqrt(dx*dx + dz*dz)
                is_moving = distance > 0.5
                
                pato_index = duck_id - 1
                if 0 <= pato_index < len(patos):
                    # Store target position for interpolation
                    previous_positions[duck_id] = (new_x, new_z)
                    
                    if is_moving:
                        angle = math.degrees(math.atan2(dx, dz))
                        patos[pato_index].angulo_rotacion = angle
    
    # Smooth interpolation every frame (not just when calling Julia)
    for duck_id in previous_positions:
        pato_index = duck_id - 1
        if 0 <= pato_index < len(patos):
            target_x, target_z = previous_positions[duck_id]
            current_x, current_z = smooth_positions.get(duck_id, (target_x, target_z))
            
            # Smooth interpolation with lerp factor
            lerp_factor = 0.15  # Higher = more responsive, lower = smoother
            smooth_x = current_x + (target_x - current_x) * lerp_factor
            smooth_z = current_z + (target_z - current_z) * lerp_factor
            
            # Update smooth position
            smooth_positions[duck_id] = (smooth_x, smooth_z)
            
            # Apply to pato
            patos[pato_index].x = smooth_x
            patos[pato_index].z = smooth_z
            
            # Check if moving for animation
            distance = math.sqrt((target_x - current_x)**2 + (target_z - current_z)**2)
            is_moving = distance > 2.0
            patos[pato_index].actualizar(moviendo=is_moving)

    # Render
    display()
    pygame.display.flip()
    
    clock.tick(60)  # Back to 60 FPS for smooth movement

pygame.quit()
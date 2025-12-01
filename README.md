# Granja de Patos

Simulación multi-agente de patos con comportamiento de bandada (flocking) usando Julia y visualización 3D en OpenGL.

## Descripción

Sistema donde 10 patos autónomos se mueven en grupo siguiendo el algoritmo de Boids, mientras un granjero controlado por el jugador interactúa con ellos. La simulación corre en Julia (backend) con Agents.jl y se visualiza en Python con PyGame y OpenGL (frontend), comunicándose mediante una API REST.

## Características

- 10 agentes autónomos con comportamiento de flocking (cohesión, alineación, separación)
- Granjero controlado por teclado
- Sistema de alimentación con partículas
- Modelos 3D personalizados en Blender
- Animaciones de alas, patas y brazos
- Detección de colisiones entre patos y granjero

## Arquitectura

| Componente | Tecnología | Función |
|------------|------------|---------|
| Backend | Julia + Agents.jl | Simulación multi-agente |
| API | Genie.jl | Servidor REST en localhost:8000 |
| Frontend | Python + PyGame + OpenGL | Renderizado 3D |

## Requisitos

### Julia
- Agents.jl
- Genie.jl
- HTTP.jl
- JSON3.jl
- LinearAlgebra
- StaticArrays

### Python
- pygame
- PyOpenGL
- PyOpenGL_accelerate
- requests
- pillow

## Instalación

### Dependencias de Julia
```julia
using Pkg
Pkg.add(["Agents", "Genie", "HTTP", "JSON3", "StaticArrays"])
```

### Dependencias de Python
```bash
pip install pygame PyOpenGL PyOpenGL_accelerate requests pillow
```

## Ejecución

### 1. Iniciar servidor Julia
```bash
julia
```
```julia
include("webapi.jl")
```
Esperar hasta ver: "Server running on localhost:8000"

### 2. Ejecutar visualización
En otra terminal:
```bash
python3 main.py
```

## Controles

### Movimiento del Granjero
| Tecla | Acción |
|-------|--------|
| Q | Avanzar |
| E | Retroceder |
| A | Izquierda |
| D | Derecha |

### Acciones
| Tecla | Acción |
|-------|--------|
| SPACE | Alimentar patos |
| H | Modo pastor |
| T | Recolectar trigo |

### Cámara
| Tecla | Acción |
|-------|--------|
| Flechas | Rotar cámara |
| W | Zoom in |
| S | Zoom out |
| ESC | Salir |

## Estructura del Proyecto

```
farm/
├── main.py              # Cliente OpenGL principal
├── webapi.jl            # Servidor API REST
├── ducks.jl             # Lógica de flocking
├── pato.py              # Clase del pato
├── granjero.py          # Clase del granjero
├── food.py              # Sistema de partículas
├── ground.py            # Piso con textura
├── objloader.py         # Cargador de modelos .obj
├── pato/                # Modelos 3D del pato
├── granjero/            # Modelos 3D del granjero
└── grass2.jpg           # Textura del pasto
```



## Licencia

Proyecto académico - Tecnológico de Monterrey
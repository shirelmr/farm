# Duck Flocking Simulation

Simulación de patos con comportamiento de bandada (flocking) usando Agents.jl y visualización 3D en OpenGL.

## Descripción

Sistema multi-agente donde 10 patos autónomos se mueven en grupo siguiendo tres reglas de Boids:
- **Cohesión**: Se acercan al centro del grupo
- **Alineación**: Igualan su dirección con vecinos
- **Separación**: Evitan colisiones

La simulación corre en Julia (backend) y se visualiza en Python con OpenGL (frontend).

## Requisitos

**Julia:** `Agents`, `Genie`, `HTTP`, `JSON3`, `LinearAlgebra`, `StaticArrays`

**Python:** `pygame`, `PyOpenGL`, `requests`

## Cómo Ejecutar

### 1. Iniciar servidor Julia
```bash
julia
```
```julia
include("webapi.jl")
```

### 2. Ejecutar visualización (en otra terminal)
```bash
python3 main.py
```

## Controles

- **Flechas**: Rotar cámara
- **W/S**: Zoom in/out
- **ESC**: Salir
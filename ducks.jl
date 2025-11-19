using Agents
using LinearAlgebra
using StaticArrays
using Plots

mutable struct Duck <: AbstractAgent
    id::Int
    pos::SVector{2,Float64}  # Position as continuous coordinates
    vel::SVector{2,Float64}  # Velocity vector
    speed::Float64          # Speed magnitude
end

# Farmer structure (not an agent, just a game entity)
mutable struct Farmer
    id::Int
    pos::SVector{2,Float64}  # Position in the farm
    feeding::Bool           # Whether farmer is feeding ducks
    feed_radius::Float64    # Radius where ducks can be attracted to food
end

# Function to initialize a duck with random position and velocity
function initialize_duck(id, dims)
    pos = SVector{2,Float64}(rand(2) .* dims)
    angle = 2π * rand()
    speed = 1.0
    vel = SVector{2,Float64}(speed * cos(angle), speed * sin(angle))
    return Duck(id, pos, vel, speed)
end

# Create the model
function initialize_model(;n_ducks=10, dims=(100, 100))
    # Ensure dimensions are multiples of the default spacing (1.0)
    adjusted_dims = (ceil(Int, dims[1]), ceil(Int, dims[2]))
    space = ContinuousSpace(adjusted_dims, spacing=1.0)
    # Initialize farmer at center
    center_x = adjusted_dims[1] / 2
    center_y = adjusted_dims[2] / 2
    farmer = Farmer(999, SVector{2,Float64}(center_x, center_y), false, 8.0)
    
    model = AgentBasedModel(
        Duck, 
        space; 
        properties = Dict{Symbol,Any}(:dims => adjusted_dims, :farmer => farmer),
        agent_step! = agent_step!
    )
    
    # Add initial ducks
    for i in 1:n_ducks
        add_agent!(initialize_duck(i, adjusted_dims), model)
    end
    

    
    return model
end

# Calculate the vector to center of mass of neighbors
function cohesion_vector(duck, model, neighbors)
    n = collect(neighbors)
    isempty(n) && return SVector{2,Float64}(0.0, 0.0)
    center = sum(n -> n.pos, n) ./ length(n)
    return center .- duck.pos
end

# Calculate average velocity of neighbors
function alignment_vector(duck, model, neighbors)
    n = collect(neighbors)
    isempty(n) && return duck.vel
    avg_vel = sum(n -> n.vel, n) ./ length(n)
    return avg_vel
end

# Calculate separation vector
function separation_vector(duck, model, neighbors)
    n = collect(neighbors)
    if isempty(n)
        return SVector{2,Float64}(0.0, 0.0)
    end
    
    separation = SVector{2,Float64}(0.0, 0.0)
    for neighbor in n
        diff = duck.pos .- neighbor.pos
        dist = norm(diff)
        if dist < 2.0  # Separation radius
            separation = separation .+ (diff ./ (dist^2))
        end
    end
    return separation
end

# Main agent step function
function agent_step!(duck::Duck, model)
    # Get neighbors within vision radius
    neighbors = nearby_agents(duck, model, 5.0)
    
    # Calculate flocking vectors
    cohesion = cohesion_vector(duck, model, neighbors)
    alignment = alignment_vector(duck, model, neighbors)
    separation = separation_vector(duck, model, neighbors)
    
    # Calculate farmer interaction
    farmer = getproperty(model, :farmer)
    farmer_force = SVector{2,Float64}(0.0, 0.0)
    farmer_dist = norm(duck.pos .- farmer.pos)
    
    if farmer.feeding && farmer_dist < farmer.feed_radius
        # Attract to farmer when feeding (stronger attraction)
        direction_to_farmer = farmer.pos .- duck.pos
        if norm(direction_to_farmer) > 0
            farmer_force = (direction_to_farmer ./ norm(direction_to_farmer)) .* 0.4
        end
    elseif farmer_dist < 4.0 && !farmer.feeding
        # Slight avoidance when farmer is close but not feeding
        direction_from_farmer = duck.pos .- farmer.pos
        if norm(direction_from_farmer) > 0
            farmer_force = (direction_from_farmer ./ norm(direction_from_farmer)) .* 0.1
        end
    end
    
    # Combine forces with different weights (reduced inertia for more responsiveness)
    new_vel = duck.vel .* 0.4 .+        # Current velocity (reduced inertia)
              cohesion .* 0.08 .+       # Cohesion force (slightly reduced)
              alignment .* 0.25 .+      # Alignment force (slightly reduced)
              separation .* 0.15 .+     # Separation force (slightly reduced)
              farmer_force              # Farmer interaction force
    
    # Normalize and scale to maintain constant speed
    if norm(new_vel) > 0
        new_vel = (new_vel ./ norm(new_vel)) .* duck.speed
    end
    
    # Update duck's velocity and position
    duck.vel = new_vel
    new_pos = duck.pos .+ duck.vel
    
    # Wrap around boundaries using the space's extent
    dims = abmspace(model).extent
    new_pos = SVector{2,Float64}(mod(new_pos[1], dims[1]), mod(new_pos[2], dims[2]))
    
    duck.pos = new_pos
end
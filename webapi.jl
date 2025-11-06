include("ducks.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

# Initialize the model with ducks
model = initialize_model(n_ducks=10, dims=(20, 15))

route("/init", method = POST) do
    # Reset the model if needed
    model = initialize_model(n_ducks=10, dims=(20, 15))
    
    ducks = []
    for duck in allagents(model)
        push!(ducks, Dict(
            "id" => duck.id,
            "pos" => [round(Int, duck.pos[1]), round(Int, duck.pos[2])]
        ))
    end
    
    json(Dict("ducks" => ducks))
end

route("/run") do
    step!(model)
    ducks = []
    for duck in allagents(model)
        push!(ducks, Dict(
            "id" => duck.id,
            "pos" => [round(Int, duck.pos[1]), round(Int, duck.pos[2])]
        ))
    end
    
    json(Dict("ducks" => ducks))
end

Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

up()
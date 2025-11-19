include("ducks.jl")
using Genie, Genie.Renderer.Json, Genie.Requests, HTTP
using UUIDs

# Initialize the model with ducks
model = initialize_model(n_ducks=10, dims=(20, 15))

route("/init", method = POST) do
    # Reset the model if needed
    global model
    model = initialize_model(n_ducks=10, dims=(20, 15))
    
    ducks = []
    for duck in allagents(model)
        push!(ducks, Dict(
            "id" => duck.id,
            "pos" => [round(Int, duck.pos[1]), round(Int, duck.pos[2])]
        ))
    end
    
    # Include initial farmer information
    farmer = getproperty(model, :farmer)
    farmer_data = Dict(
        "pos" => [farmer.pos[1], farmer.pos[2]],
        "feeding" => farmer.feeding
    )
    
    json(Dict("ducks" => ducks, "farmer" => farmer_data))
end

route("/farmer", method = POST) do
    try
        farmer_data = jsonpayload()
        farmer = getproperty(model, :farmer)
        
        # Update farmer position and feeding status
        farmer.pos = SVector{2,Float64}(farmer_data["x"], farmer_data["y"])
        farmer.feeding = farmer_data["feeding"]
        
        json(Dict("status" => "ok"))
    catch e
        json(Dict("status" => "error", "message" => string(e)))
    end
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
    
    # Include farmer information in response
    farmer = getproperty(model, :farmer)
    farmer_data = Dict(
        "pos" => [farmer.pos[1], farmer.pos[2]],
        "feeding" => farmer.feeding
    )
    
    json(Dict("ducks" => ducks, "farmer" => farmer_data))
end

Genie.config.run_as_server = true
Genie.config.cors_headers["Access-Control-Allow-Origin"] = "*"
Genie.config.cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
Genie.config.cors_headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
Genie.config.cors_allowed_origins = ["*"]

up()
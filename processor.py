from cost_model import predict_cost
from aiservices import generate_ai

def process_data(data):

    # Extract input
    description = data["description"]
    length = float(data["length"])
    width = float(data["width"])
    quantity = int(data["quantity"])
    material = data["material"]
    shape = data["shape"]
    thickness = float(data["thickness"])

    # 🔹 ML prediction
    cost_data = predict_cost(length, width, quantity, material, shape, thickness)

    # 🔹 AI generation
    ai_data = generate_ai(description)

    # 🔹 Combine everything
    return {
        "time": ai_data["time"],
        "steps": ai_data["steps"],
        "safety": ai_data["safety"],
        "alternatives": ai_data["alternatives"],
        "material_needed": cost_data["material_needed"],
        "price_per_meter": cost_data["price_per_meter"],
        "total_cost": cost_data["total_cost"]
    }
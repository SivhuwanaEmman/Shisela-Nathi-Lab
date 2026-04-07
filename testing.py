from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from openai import OpenAI

load_dotenv()

print("API KEY:", os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# =========================
# TRAIN MODEL ON STARTUP
# =========================
df = pd.read_csv("materials_dataset.csv")
df = df.drop(columns=["ID"])

def split_size(size):
    try:
        parts = size.lower().replace("mm", "").split("x")
        return float(parts[0]), float(parts[1])
    except:
        return 0, 0

df[["Size_1", "Size_2"]] = df["Size_mm"].apply(lambda x: pd.Series(split_size(str(x))))
df = df.drop(columns=["Size_mm"])

df_encoded = pd.get_dummies(df, columns=["Material", "Type", "Shape"])

X = df_encoded.drop(columns=["Price_per_meter"])
y = df_encoded["Price_per_meter"]

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

model_columns = X.columns

print("✅ ML model ready")

# =========================
# FLASK ROUTES
# =========================
@app.route("/")
def home():
    return render_template("authetication.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json

    result = process_data(data)

    return jsonify(result)

# =========================
# CORE LOGIC (SHARED)
# =========================
def process_data(data):

    description = data["description"]
    length = float(data["length"])
    width = float(data["width"])
    quantity = int(data["quantity"])
    material = data["material"]
    shape = data["shape"]
    thickness = float(data["thickness"])

    # ML
    size_1 = length * 100
    size_2 = width * 100

    user_data = {
        "Thickness_mm": thickness,
        "Length_m": 6.0,
        "Price_ZAR": 0,
        "Size_1": size_1,
        "Size_2": size_2
    }

    user_df = pd.DataFrame([user_data])

    for col in model_columns:
        if col not in user_df.columns:
            user_df[col] = 0

    for col in model_columns:
        if material in col:
            user_df[col] = 1
        if shape in col:
            user_df[col] = 1

    user_df = user_df[model_columns]

    price_per_meter = model.predict(user_df)[0]

    perimeter = 2 * (length + width)
    material_needed = perimeter * 2 * quantity
    total_cost = material_needed * price_per_meter

    # AI
    prompt = f"""
    You are a welding expert.

    Project: {description}

    Return JSON:
    {{
      "time": "",
      "steps": [],
      "safety": [],
      "alternatives": []
    }}
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        ai_data = json.loads(response.choices[0].message.content)
    except:
        ai_data = {
            "time": "Not available",
            "steps": [],
            "safety": [],
            "alternatives": []
        }

    return {
        "time": ai_data["time"],
        "steps": ai_data["steps"],
        "safety": ai_data["safety"],
        "alternatives": ai_data["alternatives"],
        "material_needed": material_needed,
        "price_per_meter": price_per_meter,
        "total_cost": total_cost
    }

# =========================
# TERMINAL TEST MODE
# =========================
if __name__ == "__main__":

    mode = input("Run mode (web/test): ")

    if mode == "test":
        data = {
            "description": input("Describe project: "),
            "length": float(input("Length (m): ")),
            "width": float(input("Width (m): ")),
            "quantity": int(input("Quantity: ")),
            "material": input("Material: "),
            "shape": input("Shape: "),
            "thickness": float(input("Thickness (mm): "))
        }

        result = process_data(data)

        print("\n=== RESULT ===")
        print(result)

    else:
        app.run(debug=True)
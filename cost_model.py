import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# =========================
# LOAD + TRAIN MODEL ONCE
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

print("✅ Cost model loaded")


# =========================
# FUNCTION (THIS IS THE KEY)
# =========================
def predict_cost(length, width, quantity, material, shape, thickness):

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

    return {
        "material_needed": material_needed,
        "price_per_meter": price_per_meter,
        "total_cost": total_cost
    }
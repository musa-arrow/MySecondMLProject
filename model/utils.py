import pandas as pd
import pickle
import os
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

MODEL_PATH = os.path.join("models", "crop_recommendation_model.pkl")

def train_model():
    os.makedirs("models", exist_ok=True)
    train_df = pd.read_csv("data/train.csv")
    test_df = pd.read_csv("data/test.csv")

    X_train = train_df.drop(["Crop", "Unnamed: 0"], axis=1)
    y_train = train_df["Crop"]
    X_test = test_df.drop(["Crop", "Unnamed: 0"], axis=1)
    y_test = test_df["Crop"]

    encoder = LabelEncoder()
    y_train_encoded = encoder.fit_transform(y_train)
    y_test_encoded = encoder.transform(y_test)

    model = XGBClassifier(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=5,
        use_label_encoder=False,
        eval_metric="mlogloss",
        random_state=42
    )
    model.fit(X_train, y_train_encoded)

    y_pred = model.predict(X_test)
    y_pred_labels = encoder.inverse_transform(y_pred)
    print(f"✅ XGBoost doğruluk oranı: {accuracy_score(y_test, y_pred_labels):.2f}")

    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, encoder), f)

def load_model():
    with open(MODEL_PATH, "rb") as file:
        model, encoder = pickle.load(file)
    return model, encoder

def predict_crop(N, P, K, pH, rainfall, temperature):
    model, encoder = load_model()
    input_df = pd.DataFrame([[N, P, K, pH, rainfall, temperature]],
                            columns=["N", "P", "K", "pH", "rainfall", "temperature"])
    prediction_num = model.predict(input_df)[0]
    prediction_label = encoder.inverse_transform([prediction_num])[0]
    return prediction_label

def get_typical_values(crop_name):
    df = pd.read_csv("data/train.csv")
    crop_df = df[df["Crop"].str.lower() == crop_name.lower()]
    if crop_df.empty:
        return None
    stats = {
        "Sıcaklık (°C)": f"{crop_df['temperature'].mean():.1f}",
        "pH": f"{crop_df['pH'].mean():.2f}",
        "Yağış (mm)": f"{crop_df['rainfall'].mean():.1f}",
        "Azot (N)": f"{crop_df['N'].mean():.0f}",
        "Fosfor (P)": f"{crop_df['P'].mean():.0f}",
        "Potasyum (K)": f"{crop_df['K'].mean():.0f}"
    }
    return stats
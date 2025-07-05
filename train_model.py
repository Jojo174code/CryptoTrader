# === train_model.py ===
import pandas as pd
import os
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle

DATA_DIR = "data/historical"
MODEL_FILE = "model.pkl"

# === Load and prepare data ===
def load_price_data():
    all_data = []
    for file in os.listdir(DATA_DIR):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(DATA_DIR, file))
            df["symbol"] = file.replace(".csv", "")
            all_data.append(df)
    return pd.concat(all_data).sort_values("timestamp")

def create_features_and_labels(df):
    df["price_next"] = df["price"].shift(-1)
    df["1h_change"] = df["price"].pct_change(periods=1) * 100
    df["24h_change"] = df["price"].pct_change(periods=24) * 100
    df.dropna(inplace=True)

    # Simple rule-based labeling
    df["label"] = "HOLD"
    df.loc[df["price_next"] > df["price"] * 1.002, "label"] = "BUY"
    df.loc[df["price_next"] < df["price"] * 0.998, "label"] = "SELL"

    features = df[["price", "volume", "1h_change", "24h_change"]]
    labels = df["label"]
    return features, labels

# === Train and save model ===
def train_model():
    print("🔄 Loading price data...")
    df = load_price_data()
    print(f"✅ Loaded {len(df)} rows.")

    print("🧠 Creating training data...")
    X, y = create_features_and_labels(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = DecisionTreeClassifier(max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    print("📊 Classification report:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))

    print("💾 Saving model to model.pkl...")
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(clf, f)
    print("✅ Model saved!")

if __name__ == "__main__":
    train_model()


import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

print("🔄 Loading price data...")

# ✅ Load historical Bitcoin data
df = pd.read_csv("data/historical/bitcoin.csv")
print(f"✅ Loaded {len(df)} rows.")

# ✅ Ensure timestamp is datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])
df = df.sort_values("timestamp")

# ✅ Calculate percent changes
df["1h_change"] = df["price"].pct_change(periods=1) * 100
df["24h_change"] = df["price"].pct_change(periods=24) * 100

# ✅ Drop rows with missing values
df.dropna(inplace=True)

# ✅ Features
X = df[["price", "1h_change", "24h_change", "volume"]]

# ✅ Labeling logic
labels = []
threshold = 0.2  # 0.2% change

for i in range(1, len(df)):
    pct_change = (df["price"].iloc[i] - df["price"].iloc[i - 1]) / df["price"].iloc[i - 1]
    if pct_change > threshold / 100:
        labels.append("BUY")
    elif pct_change < -threshold / 100:
        labels.append("SELL")
    else:
        labels.append("HOLD")

# Align X with labels
X = X.iloc[1:]
y = labels

print("🧠 Creating training data...")

# ✅ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# ✅ Train model
model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# ✅ Evaluate model
predictions = model.predict(X_test)
print("📊 Classification report:")
print(classification_report(y_test, predictions))

# ✅ Save model
joblib.dump(model, "model.pkl")
print("💾 Saved model as model.pkl")

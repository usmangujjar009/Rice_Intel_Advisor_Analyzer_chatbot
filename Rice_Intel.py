import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# === Load and train model === #
df = pd.read_excel("rice_field_data_with_suggestions.xlsx")

label_encoder = LabelEncoder()
df['irrigation_needed'] = label_encoder.fit_transform(df['irrigation_needed'])

X = df[['temperature', 'humidity', 'ph_level', 'moisture']]
y = df['irrigation_needed']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = XGBClassifier(n_estimators=200, learning_rate=0.05, max_depth=5, eval_metric='logloss', random_state=42)
model.fit(X_train_scaled, y_train)

accuracy = accuracy_score(y_test, model.predict(X_test_scaled)) * 100

# === Store latest input values globally === #
latest_values = {"temp": None, "hum": None, "ph": None, "mois": None}

# === Chatbot logic (dynamic) === #
def get_bot_response(msg):
    msg = msg.lower()

    temp = latest_values["temp"]
    hum = latest_values["hum"]
    ph = latest_values["ph"]
    mois = latest_values["mois"]

    if any(v is None for v in [temp, hum, ph, mois]):
        return "ℹ️ Please enter field conditions above and click 'Analyze Conditions' first."

    if "temperature" in msg:
        if temp > 38:
            return f"🌡️ Temperature is {temp}°C — too high! Apply irrigation & consider shading."
        elif temp < 20:
            return f"❄️ Temperature is {temp}°C — too low. Protect your field from cold."
        else:
            return f"✅ Temperature is {temp}°C — Normal range for rice."

    elif "humidity" in msg:
        if hum < 40:
            return f"💧 Humidity {hum}% — too low. Use irrigation & mulching."
        elif hum > 80:
            return f"🌫️ Humidity {hum}% — too high. Watch for fungal infections."
        else:
            return f"✅ Humidity {hum}% — Suitable for rice."

    elif "moisture" in msg:
        if mois < 30:
            return f"🌱 Moisture {mois}% — too low. Immediate irrigation needed."
        elif mois > 70:
            return f"⚠️ Moisture {mois}% — too high. Avoid overwatering."
        else:
            return f"✅ Moisture {mois}% — Balanced for rice growth."

    elif "ph" in msg:
        if ph < 5.5:
            return f"🧪 pH {ph} — too acidic. Apply lime to balance it."
        elif ph > 7.5:
            return f"🧪 pH {ph} — too alkaline. Add compost or sulfur to lower it."
        else:
            return f"✅ pH {ph} — Ideal for rice farming."

    elif "irrigation" in msg:
        return "💧 Irrigation is recommended when temperature is high or soil moisture is low."

    elif "hello" in msg or "hi" in msg:
        return "👋 Hello! Ask me about your current field conditions."

    elif "bye" in msg or "exit" in msg:
        root.destroy()

    return "🤖 I can help based on your latest input. Ask about temperature, pH, moisture or humidity!"

# === GUI Setup === #
root = tk.Tk()
root.title("🌾 Rice Intel Advisor - Assistant + Analyzer")
root.geometry("680x700")
root.configure(bg="#f4fff6")

# === Top Section: Inputs & Analyze === #
frame_top = tk.Frame(root, bg="#dfffe0", padx=20, pady=10)
frame_top.pack(fill=tk.X)

tk.Label(frame_top, text="🌾 Rice Intel Condition Analyzer", font=("Helvetica", 16, "bold"), bg="#dfffe0").grid(row=0, columnspan=2, pady=10)

def make_entry(label, row):
    tk.Label(frame_top, text=label, bg="#dfffe0").grid(row=row, column=0, sticky="w")
    e = tk.Entry(frame_top)
    e.grid(row=row, column=1, pady=5)
    return e

temp_entry = make_entry("Temperature (°C):", 1)
hum_entry = make_entry("Humidity (%):", 2)
ph_entry = make_entry("pH Level:", 3)
mois_entry = make_entry("Moisture (%):", 4)

result_label = tk.Label(frame_top, text="", font=("Helvetica", 12, "bold"), bg="#dfffe0", fg="green")
result_label.grid(row=6, columnspan=2, pady=5)

# ✅ UPDATED: Bolder and clearer model accuracy label
accuracy_label = tk.Label(
    frame_top,
    text=f"📊 Model Accuracy: {accuracy:.2f}%",
    font=("Helvetica", 13, "bold"),
    bg="#dfffe0",
    fg="#333333"
)
accuracy_label.grid(row=7, columnspan=2)

def analyze_conditions():
    try:
        temp = float(temp_entry.get())
        hum = float(hum_entry.get())
        ph = float(ph_entry.get())
        mois = float(mois_entry.get())

        # Store for chatbot
        latest_values["temp"] = temp
        latest_values["hum"] = hum
        latest_values["ph"] = ph
        latest_values["mois"] = mois

        input_data = scaler.transform([[temp, hum, ph, mois]])
        prediction = model.predict(input_data)
        irrigation = label_encoder.inverse_transform(prediction)[0]

        result_label.config(text=f"🌿 Irrigation Needed: {irrigation.upper()}")

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers in all fields.")

tk.Button(frame_top, text="Analyze Conditions", bg="green", fg="white", command=analyze_conditions).grid(row=5, columnspan=2, pady=10)

# === Bottom Section: Chatbot === #
frame_chat = tk.Frame(root, bg="#f4fff6", padx=10, pady=10)
frame_chat.pack(fill=tk.BOTH, expand=True)

tk.Label(frame_chat, text="🤖 Ask Smart Advisor (Chatbot)", font=("Helvetica", 14, "bold"), bg="#f4fff6").pack()

chat_display = scrolledtext.ScrolledText(frame_chat, wrap=tk.WORD, height=12, font=("Helvetica", 11))
chat_display.pack(pady=10, fill=tk.BOTH, expand=True)
chat_display.insert(tk.END, "Bot: 👋 Hello! I am Rice Intel.\nAsk me about your crop conditions (Temperature, pH, Humidity, Moisture, etc).\n\n")

entry_chat = tk.Entry(frame_chat, font=("Helvetica", 12))
entry_chat.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

def send_chat():
    msg = entry_chat.get()
    if msg.strip() == "":
        return
    chat_display.insert(tk.END, f"You: {msg}\n")
    response = get_bot_response(msg)
    chat_display.insert(tk.END, f"Bot: {response}\n\n")
    entry_chat.delete(0, tk.END)
    chat_display.yview(tk.END)

tk.Button(frame_chat, text="Search", command=send_chat, bg="#4CAF50", fg="white", width=10).pack(side=tk.LEFT, padx=5)
tk.Button(frame_chat, text="Exit", command=root.destroy, bg="red", fg="white", width=10).pack(side=tk.RIGHT, padx=5)

root.mainloop()

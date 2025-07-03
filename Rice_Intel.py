import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from datetime import datetime
import os

# === Load & Train Model ===
df = pd.read_excel("C:/Users/waqas lodhi/Desktop/Rice Intel/rice_field_data_with_suggestions.xlsx")
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

latest_values = {"temp": None, "hum": None, "ph": None, "mois": None}
chat_history = []

# === Themes ===
themes = {
    "light": {
        "bg": "#f4fff6", "fg": "#000000", "entry_bg": "#ffffff",
        "btn_bg": "#4CAF50", "btn_fg": "#ffffff",
        "header": "#dfffe0", "chat_bg": "#ffffff"
    },
    "dark": {
        "bg": "#121212", "fg": "#ffffff", "entry_bg": "#1e1e1e",
        "btn_bg": "#007BFF", "btn_fg": "#ffffff",
        "header": "#1f1f1f", "chat_bg": "#2c2c2c"
    }
}
current_theme = "light"
btn_analyze = None
btn_report = None

# === GUI Setup ===
root = tk.Tk()
root.title("🌾 Rice Intel Advisor")
root.geometry("1020x780")

script_dir = os.path.dirname(os.path.abspath(__file__))
logo_path = os.path.join(script_dir, "logo.png")

frame_top = tk.Frame(root)
frame_top.pack(fill=tk.X, pady=10)
frame_top.grid_columnconfigure(3, weight=1)

logo_img = tk.PhotoImage(file=logo_path).subsample(4, 4)
logo_label = tk.Label(frame_top, image=logo_img)
logo_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="w")

title_label = tk.Label(frame_top, text="🌾 Rice Intel Condition Analyzer", font=("Helvetica", 16, "bold"))
title_label.grid(row=0, column=1, columnspan=2, pady=10, sticky="w")

def toggle_theme():
    global current_theme
    current_theme = "dark" if current_theme == "light" else "light"
    apply_theme()

theme_button = tk.Button(frame_top, text="Toggle Theme", command=toggle_theme, font=("Helvetica", 9),
                         width=12, relief=tk.FLAT, cursor="hand2")
theme_button.grid(row=0, column=3, padx=10, pady=8, sticky='ne')

def make_entry(label, row):
    lbl = tk.Label(frame_top, text=label)
    lbl.grid(row=row, column=1, sticky="w")
    e = tk.Entry(frame_top)
    e.grid(row=row, column=2, pady=5)
    return e

temp_entry = make_entry("Temperature (°C):", 1)
hum_entry = make_entry("Humidity (%):", 2)
ph_entry = make_entry("pH Level:", 3)
mois_entry = make_entry("Moisture (%):", 4)

result_label = tk.Label(frame_top, text="", font=("Helvetica", 12, "bold"))
result_label.grid(row=6, column=1, columnspan=2, pady=5)

accuracy_label = tk.Label(frame_top, text=f"📊 Model Accuracy: {accuracy:.2f}%", font=("Helvetica", 13, "bold"))
accuracy_label.grid(row=7, column=1, columnspan=2)

# === CHAT FRAME ===
frame_chat = tk.Frame(root)
frame_chat.pack(fill=tk.BOTH, expand=True, pady=(10, 20))

chat_label = tk.Label(frame_chat, text="🤖 Ask Smart Advisor (Chatbot)", font=("Helvetica", 14, "bold"))
chat_label.pack()

chat_display = scrolledtext.ScrolledText(frame_chat, wrap=tk.WORD, height=12, font=("Helvetica", 11))
chat_display.pack(pady=10, fill=tk.BOTH, expand=True)
chat_display.insert(tk.END, "Bot: 👋 Hello! I am Rice Intel.\nAsk me about your crop conditions (Temperature, Humidity, pH level, Moisture, Fertilizer, Pesticide).\n\n")
chat_history.append("Bot: 👋 Hello! I am Rice Intel.\nAsk me about your crop conditions (Temperature, Humidity, pH level, Moisture, Fertilizer, Pesticide).\n")

entry_chat = tk.Entry(frame_chat, font=("Helvetica", 12))
entry_chat.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=(0, 10))

# === THEME FUNCTION ===
def apply_theme():
    t = themes[current_theme]
    root.configure(bg=t["bg"])
    frame_top.configure(bg=t["header"])
    frame_chat.configure(bg=t["bg"])
    logo_label.configure(bg=t["header"])
    title_label.configure(bg=t["header"], fg=t["fg"])
    theme_button.configure(bg=t["btn_bg"], fg=t["btn_fg"], activebackground=t["btn_bg"])

    for widget in frame_top.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=t["header"], fg=t["fg"])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=t["entry_bg"], fg=t["fg"])

    chat_label.configure(bg=t["bg"], fg=t["fg"])
    chat_display.configure(bg=t["chat_bg"], fg=t["fg"])
    entry_chat.configure(bg=t["entry_bg"], fg=t["fg"])

    for btn in frame_chat.winfo_children():
        if isinstance(btn, tk.Button):
            btn.configure(bg=t["btn_bg"], fg=t["btn_fg"], activebackground=t["btn_bg"])

    if current_theme == "light":
        btn_analyze.configure(bg="#f44336", fg="white")
        btn_report.configure(bg="#4CAF50", fg="white")
    else:
        btn_analyze.configure(bg="#1E90FF", fg="white")
        btn_report.configure(bg="#800080", fg="white")

# === FUNCTIONS ===
def analyze_conditions():
    try:
        temp = float(temp_entry.get())
        hum = float(hum_entry.get())
        ph = float(ph_entry.get())
        mois = float(mois_entry.get())
        latest_values.update({"temp": temp, "hum": hum, "ph": ph, "mois": mois})
        input_data = scaler.transform([[temp, hum, ph, mois]])
        pred = model.predict(input_data)
        irrigation = label_encoder.inverse_transform(pred)[0]
        result_label.config(text=f"🌿 Irrigation Needed: {irrigation.upper()}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter valid numbers in all fields.")

def get_bot_response(msg):
    msg = msg.lower()
    temp, hum, ph, mois = latest_values.values()
    if any(v is None for v in [temp, hum, ph, mois]):
        return "ℹ️ Please enter field conditions above and click 'Analyze Conditions' first."

    if "temperature" in msg or "temp" in msg:
        if temp < 20:
            return f"🌡️ Temperature is too low ({temp}°C). Suggestion: Apply mulch or reduce watering."
        elif temp > 35:
            return f"🌡️ Temperature is too high ({temp}°C). Suggestion: Install shade net."
        else:
            return f"🌡️ Temperature is optimal ({temp}°C)."

    elif "humidity" in msg or "hum" in msg:
        if hum < 60:
            return f"💧 Humidity is low ({hum}%). Suggestion: Use sprinkler system."
        elif hum > 80:
            return f"💧 Humidity is high ({hum}%). Suggestion: Increase ventilation."
        else:
            return f"💧 Humidity is ideal ({hum}%)."

    elif "ph" in msg:
        if ph < 5.5:
            return f"🧪 pH is low ({ph}). Suggestion: Add lime to raise pH."
        elif ph > 7.0:
            return f"🧪 pH is high ({ph}). Suggestion: Add sulfur or gypsum."
        else:
            return f"🧪 pH is optimal ({ph})."

    elif "moisture" in msg or "mois" in msg:
        if mois < 40:
            return f"🌱 Moisture is low ({mois}%). Suggestion: Increase watering."
        elif mois > 60:
            return f"🌱 Moisture is high ({mois}%). Suggestion: Improve soil drainage."
        else:
            return f"🌱 Moisture is good ({mois}%)."

    elif "irrigation" in msg:
        pred = model.predict(scaler.transform([[temp, hum, ph, mois]]))
        irrigation = label_encoder.inverse_transform(pred)[0]
        return f"🚿 Irrigation recommendation: {irrigation.upper()}"

    elif "fertilizer" in msg:
        if ph < 5.5:
            return "🧪 Fertilizer Tip: Use DAP or lime-based fertilizers to balance low pH."
        elif mois < 40:
            return "🌿 Fertilizer Tip: Use urea with proper watering for better nitrogen absorption."
        else:
            return "🌿 Use balanced NPK (10-10-10) fertilizer for healthy rice growth."

    elif "pesticide" in msg or "bug" in msg or "insect" in msg or "fungus" in msg:
        return "🦟 Pesticide Tip: Use neem oil or Carbofuran for pests. For fungal issues, use copper oxychloride."

    return "🤖 I can help you with temperature, humidity, pH, moisture, fertilizer, pesticide, and irrigation advice."

def send_chat():
    msg = entry_chat.get().strip()
    if not msg: return
    chat_display.insert(tk.END, f"You: {msg}\n")
    chat_history.append(f"You: {msg}")
    response = get_bot_response(msg)
    chat_display.insert(tk.END, f"Bot: {response}\n\n")
    chat_history.append(f"Bot: {response}")
    entry_chat.delete(0, tk.END)
    chat_display.yview(tk.END)

def generate_report():
    if any(v is None for v in latest_values.values()):
        messagebox.showinfo("No Data", "Please analyze conditions first.")
        return
    now = datetime.now()
    filename = f"Rice_Field_Report_{now.strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(script_dir, filename)
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    y = height - 1 * inch

    c.setFont("Helvetica-Bold", 16)
    c.drawString(1 * inch, y, "🌾 Rice Field Condition Report")
    y -= 0.4 * inch

    c.setFont("Helvetica", 12)
    for key, value in latest_values.items():
        label = {"temp": "Temperature (°C)", "hum": "Humidity (%)", "ph": "pH Level", "mois": "Moisture (%)"}[key]
        c.drawString(1 * inch, y, f"{label}: {value}")
        y -= 0.3 * inch

    pred = model.predict(scaler.transform([[latest_values['temp'], latest_values['hum'], latest_values['ph'], latest_values['mois']]]))
    irrigation = label_encoder.inverse_transform(pred)[0]
    c.setFont("Helvetica-Bold", 13)
    c.drawString(1 * inch, y, f"Irrigation Recommendation: {irrigation.upper()}")
    y -= 0.5 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(1 * inch, y, "💬 Chat History")
    y -= 0.3 * inch
    c.setFont("Helvetica", 11)
    for chat in chat_history:
        if y < 1 * inch:
            c.showPage()
            y = height - 1 * inch
            c.setFont("Helvetica", 11)
        c.drawString(1 * inch, y, chat)
        y -= 0.25 * inch

    c.save()
    messagebox.showinfo("Report Generated", f"Report saved:\n{filepath}")

# === BUTTONS ===
btn_analyze = tk.Button(frame_top, text="Analyze Conditions", command=analyze_conditions, font=("Helvetica", 11, "bold"))
btn_analyze.grid(row=5, column=1, columnspan=2, pady=10)

btn_report = tk.Button(frame_top, text="Generate Report", command=generate_report, font=("Helvetica", 11, "bold"))
btn_report.grid(row=8, column=1, columnspan=2, pady=5)

tk.Button(frame_chat, text="Search", command=send_chat, width=10).pack(side=tk.LEFT, padx=5, pady=(0, 10))
tk.Button(frame_chat, text="Exit", command=root.destroy, width=10).pack(side=tk.RIGHT, padx=5, pady=(0, 10))

# === START ===
apply_theme()
root.mainloop()

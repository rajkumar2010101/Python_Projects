import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import xgboost as xgb
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global variables
df = None
model = None
max_week = None
week_range = None

def load_data():
    """Load and preprocess dataset from CSV or Excel."""
    global df, max_week, week_range
    file_path = filedialog.askopenfilename(
        title="Select CSV or Excel File", 
        filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx;*.xls")]
    )
    
    if not file_path:
        messagebox.showerror("Error", "No file selected!")
        return None
    
    try:
        # Read file based on extension
        df = pd.read_csv(file_path) if file_path.endswith(".csv") else pd.read_excel(file_path)

        # Ensure date format is correct
        df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
        df.dropna(subset=["Date"], inplace=True)  # Remove invalid dates
        
        # Extract week number and filter out weekends
        df["Week"] = df["Date"].dt.isocalendar().week
        df["Day"] = df["Date"].dt.weekday  # Monday=0, Sunday=6
        df = df[df["Day"] < 5]  # Keep only Monday-Friday

        max_week, min_week = df["Week"].max(), df["Week"].min()
        week_range = max_week - min_week + 1  

        # Update GUI labels
        weeks_label.config(text=f"Weeks Available in Dataset: {week_range}")
        predict_range_label.config(text=f"Maximum Weeks We Can Predict: {max_week + 1} onwards")

        messagebox.showinfo("Success", "File loaded successfully!")
        return df
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file: {e}")
        return None

def train_model():
    """Train an XGBoost model on the loaded data."""
    global model, df
    df = load_data()
    if df is None:
        return
    
    if "Week" not in df.columns or "Calls Offered" not in df.columns:
        messagebox.showerror("Error", "Invalid data format! Required columns: Date, Week, Calls Offered")
        return
    
    X, y = df[["Day"]].values, df["Calls Offered"].values  
    
    model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=100)
    model.fit(X, y)
    
    messagebox.showinfo("Success", "Model trained successfully!")

def predict_calls():
    """Predict call volumes for a future week."""
    global model, df
    if model is None:
        messagebox.showerror("Error", "Please train the model first!")
        return
    
    try:
        week_value = int(entry_week.get())
        if week_value <= max_week:
            messagebox.showerror("Input Error", "Please enter a future week number!")
            return

        # Predict only for weekdays (Monday-Friday)
        future_days = np.array([0, 1, 2, 3, 4]).reshape(-1, 1)
        predicted_calls = model.predict(future_days)

        # Get the last available date
        last_date = df["Date"].max()

        # Generate future dates strictly after the last available date
        future_dates = []
        i = 1
        while len(future_dates) < 5:  # Only include 5 weekdays
            new_date = last_date + pd.Timedelta(days=i)
            if new_date.weekday() < 5 and new_date not in df["Date"].values:  # Ensure it's a weekday and not in actual data
                future_dates.append(new_date)
            i += 1
        
        # Create predicted DataFrame
        predicted_data = pd.DataFrame({"Date": future_dates, "Predicted Calls Offered": predicted_calls})
        
        plot_graph(predicted_data)

        total_calls = int(predicted_data["Predicted Calls Offered"].sum())
        result_label.config(text=f"Predicted Total Calls Offered for Week {week_value}: {total_calls}")
    
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid week number")
    except Exception as e:
        messagebox.showerror("Error", f"Prediction failed: {e}")

def plot_graph(predicted_data):
    """Plot actual and predicted call volumes."""
    global df
    past_data = df[df["Week"] >= df["Week"].max() - 2][["Date", "Calls Offered"]]

    fig, ax = plt.subplots(figsize=(12, 5))

    # Plot actual data
    ax.plot(past_data["Date"], past_data["Calls Offered"], marker='o', linestyle='-', label="Actual Calls", color='blue')

    # Plot predicted data
    ax.plot(predicted_data["Date"], predicted_data["Predicted Calls Offered"], marker='o', linestyle='--', label="Predicted Calls", color='red')

    # Format x-axis labels
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%a, %d-%b'))
    plt.xticks(rotation=45, ha="right")

    # Annotate values on the graph
    for i, txt in enumerate(past_data["Calls Offered"]):
        ax.annotate(f"{int(txt)}", (past_data["Date"].iloc[i], past_data["Calls Offered"].iloc[i]), 
                    textcoords="offset points", xytext=(0,5), ha='center', fontsize=9, color='blue')
    
    for i, txt in enumerate(predicted_data["Predicted Calls Offered"]):
        ax.annotate(f"{int(txt)}", (predicted_data["Date"].iloc[i], predicted_data["Predicted Calls Offered"].iloc[i]), 
                    textcoords="offset points", xytext=(0,5), ha='center', fontsize=9, color='red')

    ax.set_xlabel("Date (Day)")
    ax.set_ylabel("Calls Offered")
    ax.set_title("Actual vs. Predicted Calls")
    ax.legend()
    ax.grid()

    plt.tight_layout()

    # Clear previous graph
    for widget in graph_frame.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# GUI Setup
root = tk.Tk()
root.title("Calls Prediction")
root.geometry("650x550")
root.configure(bg="#F5F5F5")

train_button = tk.Button(root, text="Upload & Train Model", command=train_model, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
train_button.pack(pady=10)

weeks_label = tk.Label(root, text="Weeks Available in Dataset: -", bg="#F5F5F5", font=("Arial", 10))
weeks_label.pack()

predict_range_label = tk.Label(root, text="Maximum Weeks We Can Predict: -", bg="#F5F5F5", font=("Arial", 10))
predict_range_label.pack()

label_week = tk.Label(root, text="Enter Future Week Number:", bg="#F5F5F5", font=("Arial", 12))
label_week.pack()
entry_week = tk.Entry(root, font=("Arial", 12))
entry_week.pack(pady=5)

predict_button = tk.Button(root, text="Predict Calls Offered", command=predict_calls, bg="#FF9800", fg="white", font=("Arial", 12, "bold"))
predict_button.pack(pady=10)

result_label = tk.Label(root, text="Predicted Calls Offered: ", bg="#F5F5F5", font=("Arial", 12, "bold"))
result_label.pack()

graph_frame = tk.Frame(root, bg="#F5F5F5")
graph_frame.pack(pady=10)

root.mainloop()

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import serial
import time
from openai import OpenAI

# ------------------------- MathAssist_v04 (Functionality) -------------------------

SYSTEM_PROMPT_REASONER = (
    "You are an agent specialized in solving mathematical problems through step-by-step reasoning. "
    "When you receive a math problem statement from the user, your task is to develop and present a structured reasoning "
    "that illustrates every logical step needed to reach the solution.\n"
    "Make sure to:\n"
    "- Carefully analyze the problem statement and identify relevant information.\n"
    "- Break down the problem into clear and sequential steps.\n"
    "- Provide detailed explanations for each step, using examples or formulas when appropriate.\n"
    "- Avoid giving the final solution immediately unless explicitly requested."
)

SYSTEM_PROMPT_SUGGERIMENTO_TEMPLATE = (
    "You are an agent assigned to provide targeted hints to guide the user in completing their reasoning for solving a math problem. "
    "Below are the given details:\n"
    "- **Problem statement:** {problem_description}\n"
    "- **Step-by-step reasoning:** {reasoning}\n\n"
    "You will receive a user message containing details about the type of hint requested, information about their progress, and a numerical label (1 to 5) representing their psychological state.\n\n"
    "Your task is to:\n"
    "1) Determine the necessary level of support based on the numerical label:\n"
    "   - 1: Provide a minimal hint to encourage student independence.\n"
    "   - 2: Offer a slightly more explicit hint, guiding the student without revealing too much.\n"
    "   - 3: Give clear instructions with some explicit steps, allowing room for independent reasoning.\n"
    "   - 4: Provide a detailed guide that walks the student through the step, offering crucial elements to overcome it.\n"
    "   - 5: Offer complete support with step-by-step explanations, significantly reducing the difficulty of the step.\n"
    "2) Guide the user step by step, focusing on the reasoning step where they need support.\n"
    "3) Maintain a clear, encouraging, and learning-oriented tone, facilitating comprehension without directly revealing the complete solution."
)

def call_reasoner(api_key, problem_description):
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="o3-mini",
            messages=[
                {
                    "role": "developer",
                    "content": [
                        {"type": "text", "text": SYSTEM_PROMPT_REASONER}
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": problem_description}
                    ]
                }
            ],
            response_format={"type": "text"},
            reasoning_effort="medium",
            store=False
        )
        reasoning = response.choices[0].message.content
        return reasoning
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nella chiamata al Reasoner: {e}")
        return None

def call_suggestion(api_key, problem_description, reasoning, suggestion_request, psycho_label):
    system_prompt = SYSTEM_PROMPT_SUGGERIMENTO_TEMPLATE.format(
        problem_description=problem_description,
        reasoning=reasoning
    )
    user_message = f"Richiesta: {suggestion_request}\nStato psicofisico: {map_value(psycho_label)}"
    print(user_message)
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "developer",
                    "content": [
                        {"type": "text", "text": system_prompt}
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message}
                    ]
                }
            ],
            response_format={"type": "text"},
            store=True
        )
        suggestion = response.choices[0].message.content
        return suggestion
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nella chiamata al Suggerimento: {e}")
        return None

# Session variables
session_problem = ""
session_reasoning = ""

def genera_ragionamento():
    api_key = entry_api_key.get().strip()
    problem_text = text_problem.get("1.0", tk.END).strip()
    if not api_key or not problem_text:
        messagebox.showwarning("Warning", "Insert API Key and problem description.")
        return

    reasoning = call_reasoner(api_key, problem_text)
    if reasoning:
        text_reasoning.delete("1.0", tk.END)
        text_reasoning.insert(tk.END, reasoning)
        global session_problem, session_reasoning
        session_problem = problem_text
        session_reasoning = reasoning

def richiedi_suggerimento():
    api_key = entry_api_key.get().strip()
    suggestion_request = entry_suggestion.get().strip()
    # Label refresh from serial data
    psycho_label = entry_label.get().strip()
    if not api_key or not suggestion_request or not psycho_label:
        messagebox.showwarning("Warning", "Insert Suggestion Request.")
        return

    try:
        label_val = int(psycho_label)
        if label_val < 0 or label_val > 6:
            messagebox.showwarning("Warning", "Wrong Mapped Label!")
            return
    except ValueError:
        messagebox.showwarning("Warning", "Wrong APW Judgment")
        return

    if not session_problem or not session_reasoning:
        messagebox.showwarning("Warning", "Generate or insert reasoning steps.")
        return

    suggestion = call_suggestion(api_key, session_problem, session_reasoning, suggestion_request, label_val)
    if suggestion:
        text_suggestion.delete("1.0", tk.END)
        text_suggestion.insert(tk.END, suggestion)

# ------------------------- Serial Communication (da APW_serial_v03) -------------------------

def map_value(val):
    if val in (0, 1):
        return "5"
    elif 2 <= val <= 4:
        return "4"
    elif 5 <= val <= 7:
        return "3"
    elif val in (10, 11):
        return "1"
    elif 8 <= val <= 9:
        return "2"
    else:
        return "6"

def start_serial_reading(porta):
    baud_rate = 115200
    try:
        ser = serial.Serial(
            port=porta,
            baudrate=baud_rate,
            timeout=None,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False
        )
    except serial.SerialException as e:
        messagebox.showerror("Serial Error", f"Error in opening serial port {porta}: {e}")
        return

    print(f"Serial Communication Opened od Port {porta} at {baud_rate} bps.")
    # Start streaming
    comando = "STREAM\n"
    ser.write(comando.encode('utf-8'))
    
    # Stream confirm
    risposta = ser.readline().decode('utf-8', errors='replace').strip()
    if risposta == "OK":
        print("OK. Stream started...")
    else:
        print("Proble in serial comminication!")
    
    try:
        while True:
            dati = ser.readline()
            linea = dati.decode('utf-8', errors='replace').strip()
            if linea:
                parti = linea.split(',')
                if len(parti) >= 3:
                    try:
                        valore = int(parti[1])
                        label = map_value(valore)
                        print("APW Judgment:", valore)
                        print("Mapped Label:", label)
                        # GUI Label Refresh (thread-safe)
                        root.after(0, update_label_field, label)
                    except ValueError:
                        print("Warning! Wrong APW Judgment", parti[1])
                else:
                    print("Warning!!!", linea)
            # Delay
            time.sleep(0.01)
    except Exception as e:
        print("Error in serial comminication", e)
    finally:
        ser.close()
        print("Serial Communication Closed.")

def update_label_field(label_value):
    # Label Refresh (read only) using set() on textvariable
    label_var.set(label_value)

def avvia_seriale():
    porta = entry_serial.get().strip()
    if not porta:
        messagebox.showwarning("Warning", "Insert serial port (es. COM3 o /dev/ttyUSB0).")
        return
    # Start serial thread
    t = threading.Thread(target=start_serial_reading, args=(porta,), daemon=True)
    t.start()

# ------------------------- Grafic Interface -------------------------

root = tk.Tk()
root.title("MathAssist & Serial Label Integration")

# API Key
frame_api = tk.Frame(root)
frame_api.pack(padx=10, pady=5, fill=tk.X)
tk.Label(frame_api, text="API Key:").pack(side=tk.LEFT)
entry_api_key = tk.Entry(frame_api, width=50, show="*")
entry_api_key.pack(side=tk.LEFT, padx=5)

# Math problem
frame_problem = tk.Frame(root)
frame_problem.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
tk.Label(frame_problem, text="Math Problem Description:").pack(anchor=tk.W)
text_problem = scrolledtext.ScrolledText(frame_problem, width=80, height=8)
text_problem.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

# Button for reasoning steps
btn_reasoner = tk.Button(root, text="Generate Reasoning Steps", command=genera_ragionamento)
btn_reasoner.pack(padx=10, pady=5)

# Frame for the reasoning steps
frame_reasoning = tk.Frame(root)
frame_reasoning.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
tk.Label(frame_reasoning, text="Reasoning steps:").pack(anchor=tk.W)
text_reasoning = scrolledtext.ScrolledText(frame_reasoning, width=80, height=8)
text_reasoning.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

# Suggestion Request
frame_suggestion = tk.Frame(root)
frame_suggestion.pack(padx=10, pady=5, fill=tk.X)
tk.Label(frame_suggestion, text="Suggestion Request:").grid(row=0, column=0, sticky=tk.W)
entry_suggestion = tk.Entry(frame_suggestion, width=60)
entry_suggestion.grid(row=0, column=1, padx=5, pady=2)

# Label
tk.Label(frame_suggestion, text="Label (0-6):").grid(row=1, column=0, sticky=tk.W)
label_var = tk.StringVar()
entry_label = tk.Entry(frame_suggestion, width=10, textvariable=label_var, state="readonly")
entry_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

# Button for suggestion_request
btn_suggestion = tk.Button(root, text="Suggestion Request", command=richiedi_suggerimento)
btn_suggestion.pack(padx=10, pady=5)

# Frame for the suggestion
frame_output = tk.Frame(root)
frame_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
tk.Label(frame_output, text="Suggestion:").pack(anchor=tk.W)
text_suggestion = scrolledtext.ScrolledText(frame_output, width=80, height=8)
text_suggestion.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

# Frame serial port setting
frame_serial = tk.Frame(root)
frame_serial.pack(padx=10, pady=5, fill=tk.X)
tk.Label(frame_serial, text="Serial Port (es. COM3 o /dev/ttyUSB0):").pack(side=tk.LEFT)
entry_serial = tk.Entry(frame_serial, width=20)
entry_serial.pack(side=tk.LEFT, padx=5)
btn_serial = tk.Button(frame_serial, text="Connect Sleep Buster", command=avvia_seriale)
btn_serial.pack(side=tk.LEFT, padx=5)

root.mainloop()

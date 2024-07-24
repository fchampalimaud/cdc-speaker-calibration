import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    port_strings.append("Refresh")

    return port_strings


def spinbox_row(container, label_text, default_value, from_, to, increment, row, spinbox_width=10, int_value: int = 0):
    label = tk.Label(container, text=label_text)
    label.grid(row=row, column=0, sticky="e")

    if int_value == 0:
        spinbox_variable = tk.StringVar(container, str(default_value))
    else:
        spinbox_variable = tk.IntVar(container, int(default_value))

    spinbox = ttk.Spinbox(container, from_=from_, to=to, increment=increment, textvariable=spinbox_variable, width=spinbox_width, justify="center")
    spinbox.grid(row=row, column=1, sticky="w", pady=5, padx=5)

    return label, spinbox_variable, spinbox

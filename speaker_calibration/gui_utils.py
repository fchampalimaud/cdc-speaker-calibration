import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    return port_strings


class SpinboxFrame(tk.Frame):
    def __init__(self, container, label, default_value, from_, to, increment, spinbox_width=10):
        super().__init__(container)

        self.label = tk.Label(self.intercept_frame, text=label)
        self.label.grid(row=0, column=0, sticky="e")

        self.spinbox_variable = tk.StringVar(self, str(default_value))
        self.spinbox = ttk.Spinbox(self, from_=from_, to=to, increment=increment, textvariable=self.spinbox_variable, width=spinbox_width, justify="center")
        self.spinbox.grid(row=0, column=1, sticky="w")

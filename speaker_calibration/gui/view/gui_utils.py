import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import numpy as np


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    port_strings.append("Refresh")

    return port_strings


def spinbox_row(
    container,
    label_text,
    default_value,
    from_,
    to,
    increment,
    row,
    spinbox_width=10,
    int_value: int = 0,
):
    label = tk.Label(container, text=label_text)
    label.grid(row=row, column=0, sticky="e")

    if int_value == 0:
        spinbox_variable = tk.StringVar(container, str(default_value))
    else:
        spinbox_variable = tk.IntVar(container, int(default_value))

    spinbox = ttk.Spinbox(
        container,
        from_=from_,
        to=to,
        increment=increment,
        textvariable=spinbox_variable,
        width=spinbox_width,
        justify="center",
    )
    spinbox.grid(row=row, column=1, sticky="w", pady=5, padx=5)

    return label, spinbox_variable, spinbox


class SpinboxesFrame(ttk.LabelFrame):
    def __init__(self, container, init_file_path: str, text: str):
        super().__init__(container, text=text)

        # Loads some configuration parameters regarding the layout of the widgets in the window
        init = np.loadtxt(init_file_path, dtype=str, delimiter=",", skiprows=1)

        # Configures columns of the window
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Initializes the spinboxes arrays
        self.variables = np.zeros(init.shape[0], dtype=object)
        self.labels = np.zeros(init.shape[0], dtype=object)
        self.spinboxes = np.zeros(init.shape[0], dtype=object)

        # Creates and configures each row containing a spinbox
        for i in range(init.shape[0]):
            self.grid_rowconfigure(i, weight=1)
            self.labels[i], self.variables[i], self.spinboxes[i] = spinbox_row(
                self,
                init[i, 0],
                float(init[i, 1]),
                float(init[i, 1]),
                float(init[i, 2]),
                float(init[i, 3]),
                i,
                int(init[i, 4]),
                int(init[i, 5]),
            )

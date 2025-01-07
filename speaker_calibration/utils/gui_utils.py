import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
import numpy as np
from typing import Union


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    port_strings.append("Refresh")

    return port_strings


# TODO: modify to be a class instead of a function
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


class LabeledSpinbox:
    def __init__(
        self,
        container,
        label_text: str,
        default_value: Union[int, float],
        from_: Union[int, float],
        to: Union[int, float],
        increment: Union[int, float],
        row: int,
        column: int = 0,
        rowspan: int = 1,
        columnspan: int = 1,
        spinbox_width: float = 10,
    ):
        self.frame = tk.Frame(container)
        for i in range(1):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        self.label = tk.Label(self.frame, text=label_text)
        self.label.grid(row=0, column=0, sticky="e")

        if (
            isinstance(default_value, int)
            and isinstance(from_, int)
            and isinstance(to, int)
            and isinstance(increment, int)
        ):
            self.var = tk.IntVar(self.frame, default_value)
        else:
            self.var = tk.StringVar(self.frame, str(default_value))

        self.spinbox = ttk.Spinbox(
            self.frame,
            textvariable=self.var,
            from_=from_,
            to=to,
            increment=increment,
            width=spinbox_width,
            justify="center",
        )
        self.spinbox.grid(row=0, column=1, padx=5, sticky="w")

        self.frame.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            padx=5,
            pady=5,
        )

    def get(self):
        return self.var.get()

    def set(self, value):
        return self.var.set(value)


class LabeledCombobox:
    def __init__(
        self,
        container,
        label_text: str,
        row: int,
        column: int = 0,
        rowspan: int = 1,
        columnspan: int = 1,
        value_list: list = None,
        default_value: Union[str, int] = "",
        combobox_width: float = 15,
    ):
        self.frame = tk.Frame(container)
        for i in range(1):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        self.label = tk.Label(self.frame, text=label_text)
        self.label.grid(row=0, column=0, sticky="e")

        if isinstance(default_value, int) and all(
            isinstance(x, int) for x in value_list
        ):
            self.var = tk.IntVar(self.frame, default_value)
        else:
            self.var = tk.StringVar(self.frame, str(default_value))

        self.combobox = ttk.Combobox(
            self.frame,
            textvariable=self.var,
            justify="center",
            state="readonly",
            width=combobox_width,
        )
        self.combobox.grid(row=0, column=1, padx=5, sticky="w")

        if value_list is not None:
            self.combobox["values"] = value_list

        self.frame.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            padx=5,
            pady=5,
        )

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def set_values(self, value_list: list):
        self.combobox["values"] = value_list


class LabeledEntry:
    def __init__(
        self,
        container,
        label_text: str,
        row: int,
        column: int = 0,
        rowspan: int = 1,
        columnspan: int = 1,
    ):
        self.frame = tk.Frame(container)
        for i in range(1):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        self.label = tk.Label(self.frame, text=label_text)
        self.label.grid(row=0, column=0, sticky="e")

        self.var = tk.StringVar(self.frame)
        self.entry = tk.Entry(self.frame, textvariable=self.var, width=15)
        self.entry.grid(row=0, column=1, padx=5, sticky="w")

        self.frame.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            padx=5,
            pady=5,
        )

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)


class Checkbox:
    def __init__(
        self,
        container,
        text: str,
        row: int,
        column: int,
        rowspan: int = 1,
        columnspan: int = 1,
        default_value: bool = False,
        command: callable = None,
    ):
        self.var = tk.BooleanVar(container, default_value)
        self.checkbutton = ttk.Checkbutton(
            container,
            command=command,
            variable=self.var,
            onvalue=True,
            offvalue=False,
            text=text,
        )
        self.checkbutton.grid(
            row=row,
            column=column,
            rowspan=rowspan,
            columnspan=columnspan,
            padx=5,
            pady=5,
        )

    def get(self):
        return self.var.get()

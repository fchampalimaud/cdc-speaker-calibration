import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports
from typing import Union


def get_ports():
    ports = serial.tools.list_ports.comports()

    port_strings = []
    for port in ports:
        port_strings.append(port.device)

    port_strings.append("Refresh")

    return port_strings


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
        sticky=None,
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
            sticky=sticky,
        )

    def get(self):
        return self.var.get()

    def set(self, value):
        return self.var.set(value)

    def grid(self, row: int, column: int, padx: int = 5, pady: int = 5):
        self.frame.grid(row=row, column=column, padx=padx, pady=pady)

    def grid_forget(self):
        self.frame.grid_forget()


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
        sticky=None,
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
            sticky=sticky,
        )

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def set_values(self, value_list: list):
        self.combobox["values"] = value_list

    def bind(self, command: callable):
        self.combobox.bind("<<ComboboxSelected>>", command)

    def grid(self, row: int, column: int, padx: int = 5, pady: int = 5):
        self.frame.grid(row=row, column=column, padx=padx, pady=pady)

    def grid_forget(self):
        self.frame.grid_forget()


class LabeledEntry:
    def __init__(
        self,
        container,
        label_text: str,
        row: int,
        column: int = 0,
        rowspan: int = 1,
        columnspan: int = 1,
        sticky=None,
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
            sticky=sticky,
        )

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)

    def grid(self, row: int, column: int, padx: int = 5, pady: int = 5):
        self.frame.grid(row=row, column=column, padx=padx, pady=pady)

    def grid_forget(self):
        self.frame.grid_forget()


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
        sticky=None,
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
            sticky=sticky,
        )

    def get(self):
        return self.var.get()

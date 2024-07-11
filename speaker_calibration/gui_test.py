import tkinter as tk
from tkinter import ttk
import matplotlib
import ctypes
from configuration_window import ConfigurationWindow
from hardware_frame import HardwareFrame
from main import noise_calibration
from pyharp.device import Device
from pyharp.messages import HarpMessage
from serial.serialutil import SerialException
# import matplotlib.pyplot as plt

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

myappid = "fchampalimaud.cdc.speaker_calibration.alpha"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class PlotFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # prepare data
        data = {"Python": 11.27, "C": 11.16, "Java": 10.46, "C++": 7.5, "C#": 5.26}
        languages = data.keys()
        popularity = data.values()

        # create a figure
        figure = Figure(figsize=(6, 4), dpi=100)

        # create FigureCanvasTkAgg object
        figure_canvas = FigureCanvasTkAgg(figure, self)

        # create the toolbar
        NavigationToolbar2Tk(figure_canvas, self)

        # create axes
        axes = figure.add_subplot()

        # create the barchart
        axes.bar(languages, popularity)
        axes.set_title("Top 5 Programming Languages")
        axes.set_ylabel("Popularity")

        figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)


class OptionsFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.config_window = ConfigurationWindow()

        self.grid_columnconfigure(0, weight=1)
        for i in range(6):
            self.grid_rowconfigure(i, weight=1)

        self.logo = tk.PhotoImage(file="assets/cf_logo.png")
        self.logo_label = tk.Label(self, image=self.logo)
        self.logo_label.grid(column=0, row=0)

        # button
        self.run_button = ttk.Button(self, text="Run", command=self.run_calibration)
        self.run_button.grid(column=0, row=1)

        self.combobox = ttk.Combobox(self, justify="center")
        self.combobox.grid(column=0, row=2)

        # button
        self.config_button = ttk.Button(self, text="Open Configuration Window", command=self.config_window.deiconify)
        self.config_button.grid(column=0, row=3)

        # label
        self.hardware_frame = HardwareFrame(self)
        self.hardware_frame.grid(column=0, row=4)

        self.hardware_frame.port_cb.bind("<<ComboboxSelected>>", self.connect_soundcard)

        self.test_frame = TestFrame(self)
        self.test_frame.grid(column=0, row=5)

    def connect_soundcard(self, event):
        if hasattr(self, "soundcard"):
            self.soundcard.disconnect()

        try:
            self.soundcard = Device(self.hardware_frame.port_var.get())
            if self.soundcard.WHO_AM_I == 1280:
                self.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
                self.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)
        except SerialException:
            print("This is not a Harp device.")

    def run_calibration(self):
        self.config_window.load_input_parameters()
        self.calibration_factor, self.fit_parameters = noise_calibration(float(self.hardware_frame.fs_var.get()), self.config_window.input_parameters)


class TestFrame(ttk.LabelFrame):
    def __init__(self, container, text="Test Calibration"):
        super().__init__(container, text=text)

        self.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)

        self.lim_frame = tk.Frame(self)
        self.lim_frame.grid(column=0, row=0, pady=5)

        self.min_frame = tk.Frame(self.lim_frame)
        self.min_frame.grid(column=0, row=0, padx=10)

        self.min_label = ttk.Label(self.min_frame, text="Min dB")
        self.min_label.grid(column=0, row=0, sticky="e")

        self.min_var = tk.StringVar(self, "40.0")
        self.min_sb = ttk.Spinbox(self.min_frame, from_=0, to=100, increment=0.1, textvariable=self.min_var, width=10, justify="center")
        self.min_sb.grid(column=1, row=0, sticky="w")

        self.max_frame = tk.Frame(self.lim_frame)
        self.max_frame.grid(column=1, row=0, padx=10)

        self.max_label = ttk.Label(self.max_frame, text="Max dB")
        self.max_label.grid(column=0, row=0, sticky="e")

        self.max_var = tk.StringVar(self, "60.0")
        self.max_sb = ttk.Spinbox(self.max_frame, from_=0, to=100, increment=0.1, textvariable=self.max_var, width=10, justify="center")
        self.max_sb.grid(column=1, row=0, sticky="w")

        self.steps_frame = tk.Frame(self)
        self.steps_frame.grid(column=0, row=1, pady=5)

        self.steps_label = ttk.Label(self.steps_frame, text="Steps")
        self.steps_label.grid(column=0, row=0, sticky="e")

        self.steps_var = tk.IntVar(self, 15)
        self.steps_sb = ttk.Spinbox(self.steps_frame, from_=0, to=50, increment=1, textvariable=self.steps_var, width=10, justify="center")
        self.steps_sb.grid(column=1, row=0, sticky="w")

        self.par_frame = tk.Frame(self)
        self.par_frame.grid(column=0, row=2, pady=5)

        self.slope_frame = tk.Frame(self.par_frame)
        self.slope_frame.grid(column=0, row=0, padx=10)

        self.slope_label = ttk.Label(self.slope_frame, text="Slope")
        self.slope_label.grid(column=0, row=0, sticky="e")

        self.slope_var = tk.StringVar(self, "70.00")
        self.slope_sb = ttk.Spinbox(self.slope_frame, from_=-500, to=500, increment=0.01, textvariable=self.slope_var, width=10, justify="center")
        self.slope_sb.grid(column=1, row=0, sticky="w")

        self.intercept_frame = tk.Frame(self.par_frame)
        self.intercept_frame.grid(column=1, row=0, padx=10)

        self.intercept_label = ttk.Label(self.intercept_frame, text="Intercept")
        self.intercept_label.grid(column=0, row=0, sticky="e")

        self.intercept_var = tk.StringVar(self, "20.00")
        self.intercept_sb = ttk.Spinbox(self.intercept_frame, from_=-500, to=500, increment=0.01, textvariable=self.intercept_var, width=10, justify="center")
        self.intercept_sb.grid(column=1, row=0, sticky="w")

        self.test_button = ttk.Button(self, text="Load Fit Parameters")
        self.test_button.grid(column=0, row=3, pady=5)

        self.inverse_filter_frame = tk.Frame(self)
        self.inverse_filter_frame.grid(column=0, row=4, pady=5)

        self.inverse_filter_button = ttk.Button(self.inverse_filter_frame, text="Load Filter")
        self.inverse_filter_button.grid(column=0, row=0)

        self.inverse_filter_label = ttk.Label(self.inverse_filter_frame, text="No Filter")
        self.inverse_filter_label.grid(column=1, row=0)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # configure the root window
        self.title("Speaker Calibration")
        self.iconbitmap("docs/img/favicon.ico")

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set the window width and height
        window_width = 1280
        window_height = 720

        # Calculate the x and y coordinates to center the window
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)

        # Set the window position
        self.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(column=0, row=0, sticky="nsew")

        self.options_frame = OptionsFrame(self)
        self.options_frame.grid(column=1, row=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()

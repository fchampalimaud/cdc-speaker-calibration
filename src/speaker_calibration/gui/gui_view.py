import tkinter as tk
from tkinter import ttk
import numpy as np

from speaker_calibration.gui.view.settings_window import SettingsWindow
from speaker_calibration.gui.view.hardware_frame import HardwareFrame
from speaker_calibration.gui.view.plot_config_frame import PlotConfigFrame
from matplotlib.figure import Figure

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class SpeakerCalibrationView(ttk.Frame):
    """
    The frontend of the application.
    """

    # plot_frame: PlotFrame
    settings_window: SettingsWindow

    def __init__(self, container):
        super().__init__(container)

        # Configure the rows and columns of the view
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Position the Matplotlib figure frame
        self.plot_frame = ttk.Frame(self)  # PlotFrame(self)
        self.plot_frame.grid(column=0, row=0, sticky="nsew")

        # Position the settings widgets frame
        self.config = ttk.Frame(self)
        self.config.grid(column=1, row=0, sticky="nsew")

        self.config.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.config.grid_rowconfigure(i, weight=1)

        self.logo = tk.PhotoImage(file="assets/cf_logo.png")
        self.logo_label = tk.Label(self.config, image=self.logo)
        self.logo_label.grid(column=0, row=0)

        # button
        self.settings_button = ttk.Button(self.config, text="Open Settings Window")
        self.settings_button.grid(column=0, row=1)

        self.plot_config = PlotConfigFrame(self.config)
        self.plot_config.grid(column=0, row=2)

        # label
        self.hardware = HardwareFrame(self.config)
        self.hardware.grid(column=0, row=3)

        # button
        self.run_button = ttk.Button(self.config, text="Run")
        self.run_button.grid(row=4, column=0, pady=5)

        self.create_figure()

        # Creates the configuration window
        self.settings_window = SettingsWindow()

        # Shows the configuration window when the button is pressed
        self.settings_button["command"] = self.settings_window.deiconify

    def set_controller(self, controller):
        """
        Sets the controller.

        Parameters
        ----------
        controller
            the controller object which allows for the frontend and backend to communicate.
        """
        self.controller = controller

    def generate_figures(self):
        if self.settings_window.sound_type.get() == "Noise":
            self.figure = Figure(dpi=100)
            self.ax = self.figure.add_subplot()
            self.plots = []
            for i in range(3):
                (plot,) = self.ax.plot(0)
                self.plots.append(plot)
            plot_list = [
                "PSD Signal",
                "Inverse Filter",
                "Calibration Signals",
                "Calibration Data",
                "Test Signals",
                "Test Data",
            ]
            self.set_figure(self.figure)
        elif self.settings_window.sound_type.get() == "Pure Tones":
            self.figure = []
            self.ax = []
            for i in range(2):
                self.figure.append(Figure(dpi=100))
            ax = self.figure[0].add_subplot()
            self.ax.append(ax)
            self.plots = []
            plot = self.ax[0].imshow(
                np.zeros(
                    (
                        self.settings_window.calibration.att_steps.get(),
                        self.settings_window.freq_frame.num_freqs.get(),
                    ),
                ),
                cmap="plasma",
            )
            self.plots.append(plot)
            ax = self.figure[1].add_subplot()
            self.ax.append(ax)
            for i in range(2):
                (plot,) = self.ax[1].plot(0)
                self.plots.append(plot)

            plot_list = [
                "Calibration Signals",
                "Calibration Data",
                "Test Signals",
                "Test Data",
            ]

        self.plot_config.plot.set_values(plot_list)

    def create_figure(self):
        # Create a new Matplotlib figure
        self.figure = Figure(dpi=100)
        self.ax = self.figure.add_subplot()

        # Create a canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Plot the initial data
        # self.plot()

    def set_figure(self, figure):
        # Destroys current figure and toolbar
        self.canvas.get_tk_widget().destroy()
        self.toolbar.destroy()

        self.current_figure = figure

        # Creates new figure
        self.canvas = FigureCanvasTkAgg(self.current_figure, self.plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Creates new toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas.draw()

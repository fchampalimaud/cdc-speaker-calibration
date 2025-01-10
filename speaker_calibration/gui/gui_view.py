from tkinter import ttk
import numpy as np

from speaker_calibration.gui.view.plot_frame import PlotFrame
from speaker_calibration.gui.view.config_frame import ConfigFrame
from speaker_calibration.gui.view.settings_window import SettingsWindow
from matplotlib.figure import Figure


class SpeakerCalibrationView(ttk.Frame):
    """
    The frontend of the application.
    """

    plot_frame: PlotFrame
    config_frame: ConfigFrame
    settings_window: SettingsWindow

    def __init__(self, container):
        super().__init__(container)

        # Configure the rows and columns of the view
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Position the Matplotlib figure frame
        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(column=0, row=0, sticky="nsew")

        # Position the settings widgets frame
        self.config_frame = ConfigFrame(self)
        self.config_frame.grid(column=1, row=0, sticky="nsew")

        # Creates the configuration window
        self.settings_window = SettingsWindow()

        # Shows the configuration window when the button is pressed
        self.config_frame.settings_button["command"] = self.settings_window.deiconify

    def set_controller(self, controller):
        """
        Sets the controller.

        Parameters
        ----------
        controller
            the controller object which allows for the frontend and backend to communicate.
        """
        self.controller = controller

    def create_figures(self):
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
            self.plot_frame.set_figure(self.figure)
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

        self.config_frame.plot_config.plot.set_values(plot_list)

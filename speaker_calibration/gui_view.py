from tkinter import ttk

from speaker_calibration.gui.plot_frame import PlotFrame
from speaker_calibration.gui.config_frame import ConfigFrame
from speaker_calibration.gui.settings_window import SettingsWindow


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
        self.grid_columnconfigure(0, weight=2)
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

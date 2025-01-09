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

    # def update_plot(self, event=None):
    #     """
    #     Updates the plot based on the item selected in a combobox.

    #     Parameters
    #     ----------
    #     event
    #         this parameter is sent by the combobox when an event is triggered.
    #     """
    #     if self.config_frame.plot_config.plot_var.get() == "PSD Signal":
    #         for i in range(self.plot_frame.plots.size):
    #             self.plot_frame.plots[i].set_marker("")
    #         self.plot_frame.plots[0].set_data(
    #             np.linspace(
    #                 0, self.model.psd_signal.duration, self.model.psd_signal.signal.size
    #             ),
    #             self.model.psd_signal.signal,
    #         )
    #         self.plot_frame.plots[1].set_data(
    #             np.linspace(
    #                 0,
    #                 self.model.psd_signal.duration,
    #                 self.model.psd_signal.recorded_sound.size,
    #             ),
    #             self.model.psd_signal.recorded_sound,
    #         )
    #         self.plot_frame.plots[2].set_data([], [])
    #     elif self.config_frame.plot_config.plot_var.get() == "Inverse Filter":
    #         for i in range(self.plot_frame.plots.size):
    #             self.plot_frame.plots[i].set_marker("")
    #         self.plot_frame.plots[0].set_data(
    #             self.model.inverse_filter[:, 0], self.model.inverse_filter[:, 1]
    #         )
    #         self.plot_frame.plots[1].set_data([], [])
    #         self.plot_frame.plots[2].set_data([], [])
    #     elif self.config_frame.plot_config.plot_var.get() == "Calibration Signals":
    #         for i in range(self.plot_frame.plots.size):
    #             self.plot_frame.plots[i].set_marker("")
    #         i = self.config_frame.plot_config.calibration_signal_var.get()
    #         if self.config_frame.plot_config.signal.get() == 1:
    #             self.plot_frame.plots[0].set_data(
    #                 np.linspace(
    #                     0,
    #                     self.model.calibration_signals[i].duration,
    #                     self.model.calibration_signals[i].signal.size,
    #                 ),
    #                 self.model.calibration_signals[i].signal,
    #             )
    #         else:
    #             self.plot_frame.plots[0].set_data([], [])
    #         if self.config_frame.plot_config.recorded_sound.get() == 1:
    #             self.plot_frame.plots[1].set_data(
    #                 np.linspace(
    #                     0,
    #                     self.model.calibration_signals[i].duration,
    #                     self.model.calibration_signals[i].recorded_sound.size,
    #                 ),
    #                 self.model.calibration_signals[i].recorded_sound,
    #             )
    #         else:
    #             self.plot_frame.plots[1].set_data([], [])
    #         self.plot_frame.plots[2].set_data([], [])
    #     elif self.config_frame.plot_config.plot_var.get() == "Calibration Data":
    #         for i in range(self.plot_frame.plots.size):
    #             self.plot_frame.plots[i].set_marker("o")
    #         self.plot_frame.plots[0].set_data(
    #             self.model.calibration_data[:, 0], self.model.calibration_data[:, 1]
    #         )
    #         self.plot_frame.plots[1].set_data(
    #             self.model.calibration_data[:, 0], self.model.calibration_data[:, 2]
    #         )
    #         self.plot_frame.plots[2].set_data([], [])
    #     elif self.config_frame.plot_config.plot_var.get() == "Test Signals":
    #         for i in range(self.plot_frame.plots.size):
    #             self.plot_frame.plots[i].set_marker("")
    #         i = self.config_frame.plot_config.test_signal_var.get()
    #         if self.config_frame.plot_config.signal.get() == 1:
    #             self.plot_frame.plots[0].set_data(
    #                 np.linspace(
    #                     0,
    #                     self.model.test_signals[i].duration,
    #                     self.model.test_signals[i].signal.size,
    #                 ),
    #                 self.model.test_signals[i].signal,
    #             )
    #         else:
    #             self.plot_frame.plots[0].set_data([], [])
    #         if self.config_frame.plot_config.recorded_sound.get() == 1:
    #             self.plot_frame.plots[1].set_data(
    #                 np.linspace(
    #                     0,
    #                     self.model.test_signals[i].duration,
    #                     self.model.test_signals[i].recorded_sound.size,
    #                 ),
    #                 self.model.test_signals[i].recorded_sound,
    #             )
    #         else:
    #             self.plot_frame.plots[1].set_data([], [])
    #         self.plot_frame.plots[2].set_data([], [])
    #     elif self.config_frame.plot_config.plot_var.get() == "Test Data":
    #         for i in range(self.plot_frame.plots.size):
    #             self.plot_frame.plots[i].set_marker("o")
    #         self.plot_frame.plots[0].set_data(
    #             self.model.test_data[:, 0], self.model.test_data[:, 1]
    #         )
    #         self.plot_frame.plots[1].set_data(
    #             self.model.test_data[:, 0], self.model.test_data[:, 2]
    #         )
    #         self.plot_frame.plots[2].set_data(
    #             self.model.test_data[:, 0], self.model.test_data[:, 0]
    #         )

    #     # Assures that the x and y axis are autoscaled when the figure is redrawn
    #     self.plot_frame.ax.relim()
    #     self.plot_frame.ax.autoscale_view()
    #     self.plot_frame.figure_canvas.draw_idle()

    def create_figure(self):
        if self.settings_window.sound_type.get() == "Noise":
            self.figure = Figure(dpi=100)
            ax = self.figure.add_subplot()
            self.plots = []
            for i in range(3):
                (plot,) = ax.plot(0)
                self.plots.append(plot)
        elif self.settings_window.sound_type.get() == "Pure Tones":
            self.figure = []
            for i in range(2):
                self.figure.append(Figure(dpi=100))
            ax = self.figure[0].add_subplot()
            self.plots = []
            plot = ax.imshow(
                np.zeros(
                    self.settings_window.calibration.att_steps.get(),
                    self.settings_window.freq_frame.num_freqs.get(),
                ),
                cmap="plasma",
            )
            self.plots.append(plot)
            ax = self.figure[1].add_subplot()
            for i in range(2):
                (plot,) = ax.plot(0)
                self.plots.append(plot)

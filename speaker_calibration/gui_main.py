import tkinter as tk
import ctypes
from plot_frame import PlotFrame
from options_frame import OptionsFrame
import numpy as np
from classes import InputParameters
from main import noise_calibration
from pyharp.messages import HarpMessage

myappid = "fchampalimaud.cdc.speaker_calibration.alpha"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class SpeakerCalibrationGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure the main window
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

        # Configure the rows and columns of the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        # Position the Matplotlib figure frame
        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(column=0, row=0, sticky="nsew")

        # Position the settings widgets frame
        self.options_frame = OptionsFrame(self)
        self.options_frame.grid(column=1, row=0, sticky="nsew")

        self.options_frame.run_button.configure(command=self.calibrate)

        # Configure the event triggered when a type of plot is selected
        self.options_frame.combobox.bind("<<ComboboxSelected>>", self.change_plot)

    def calibrate(self):
        self.load_input_parameters()

        self.options_frame.soundcard.send(HarpMessage.WriteU8(41, 0).frame, False)
        self.options_frame.soundcard.send(HarpMessage.WriteU8(44, 2).frame, False)

        self.psd_signal = np.zeros(2, dtype=np.ndarray)
        self.calibration_signals = np.zeros((self.input_parameters.att_steps, 2), dtype=np.ndarray)
        self.calibration_curve = np.zeros((self.input_parameters.att_steps, 3), dtype=np.ndarray)
        self.test_signals = np.zeros((self.options_frame.test_frame.steps_var.get(), 2), dtype=np.ndarray)
        self.test_plot = np.zeros((self.options_frame.test_frame.steps_var.get(), 3), dtype=np.ndarray)

        if self.input_parameters.sound_type == "Noise":
            self.calibration_factor, self.fit_parameters = noise_calibration(
                float(self.options_frame.hardware_frame.fs_var.get()),
                self.input_parameters,
                self.calibration_factor if hasattr(self, "calibration_factor") else None,
                np.array([float(self.options_frame.test_frame.slope_var.get()), float(self.options_frame.test_frame.intercept_var.get())]),
                float(self.options_frame.test_frame.min_var.get()),
                float(self.options_frame.test_frame.max_var.get()),
                self.options_frame.test_frame.steps_var.get(),
                self.options_frame.speaker_filter.get(),
                self.options_frame.calibration_curve.get(),
                self.options_frame.test_calibration.get(),
                self.package_receiver,
            )

        np.savetxt(
            "output/calibration_factor_speaker"
            + str(self.options_frame.hardware_frame.speaker_var.get())
            + "_setup"
            + str(self.options_frame.hardware_frame.setup_var.get())
            + ".csv",
            self.calibration_factor,
            delimiter=",",
            fmt="%f",
        )
        np.savetxt(
            "output/fit_parameters_speaker" + str(self.options_frame.hardware_frame.speaker_var.get()) + "_setup" + str(self.options_frame.hardware_frame.setup_var.get()) + ".csv",
            self.fit_parameters,
            delimiter=",",
            fmt="%f",
        )

    def load_input_parameters(self):
        values = []
        for i in range(self.options_frame.config_window.spinbox_variables.size):
            if isinstance(self.options_frame.config_window.spinbox_variables[i], tk.StringVar):
                values.append(float(self.options_frame.config_window.spinbox_variables[i].get()))
            else:
                values.append(int(self.options_frame.config_window.spinbox_variables[i].get()))
        values.append(self.options_frame.config_window.sound_var.get())

        self.input_parameters = InputParameters(dict(zip(self.options_frame.config_window.settings_keys, values)))

    def package_receiver(self, package: list, message: str):
        if message == "Inverse Filter":
            self.inverse_filter = package[0]
            self.psd_signal[0] = package[1].signal
            self.psd_signal[1] = package[1].recorded_sound
        elif message == "Calibration":
            self.calibration_signals[package[1], 0] = package[0].signal
            self.calibration_signals[package[1], 1] = package[0].recorded_sound
            self.calibration_curve[package[1], 0] = package[0].db_spl
            self.calibration_curve[package[1], 1] = package[0].db_fft
        elif message == "Test":
            self.test_signals[package[1], 0] = package[0].signal
            self.test_signals[package[1], 1] = package[0].recorded_sound
            self.test_plot[package[1], 0] = package[0].db_spl
            self.test_plot[package[1], 1] = package[0].db_fft

        self.change_plot(None)

    def change_plot(self, event):
        if self.options_frame.combobox_var.get() == "PSD Signal":
            self.plot_frame.plots[0].set_data(np.linspace(0, self.psd_signal[0].size - 1, self.psd_signal[0].size), self.psd_signal[0])
            self.plot_frame.plots[1].set_data(np.linspace(0, self.psd_signal[1].size - 1, self.psd_signal[1].size), self.psd_signal[1])
            self.plot_frame.plots[2].set_data([], [])
        elif self.options_frame.combobox_var.get() == "Inverse Filter":
            self.plot_frame.plot[0].set_data(self.inverse_filter)
            self.plot_frame.plots[1].set_data([], [])
            self.plot_frame.plots[2].set_data([], [])
        elif self.options_frame.combobox_var.get() == "Calibration Signals":
            self.plot_frame.plot[0].set_data(self.calibration_signals[:, 0])
            self.plot_frame.plot[1].set_data(self.calibration_signals[:, 1])
            self.plot_frame.plots[2].set_data([], [])
        elif self.options_frame.combobox_var.get() == "Calibration Curve":
            self.plot_frame.plot[0].set_data(self.calibration_curve[:, 0])
            self.plot_frame.plot[1].set_data(self.calibration_curve[:, 1])
            self.plot_frame.plots[2].set_data([], [])
        elif self.options_frame.combobox_var.get() == "Test Signals":
            self.plot_frame.plot[0].set_data(self.test_signals[:, 0])
            self.plot_frame.plot[1].set_data(self.test_signals[:, 1])
            self.plot_frame.plots[2].set_data([], [])
        elif self.options_frame.combobox_var.get() == "Test Plot":
            self.plot_frame.plot[0].set_data(self.test_plot[:, 0])
            self.plot_frame.plot[1].set_data(self.test_plot[:, 1])
            self.plot_frame.plots[2].set_data([], [])

        self.plot_frame.ax.relim()
        self.plot_frame.ax.autoscale_view()
        self.plot_frame.figure_canvas.draw_idle()


if __name__ == "__main__":
    gui = SpeakerCalibrationGUI()
    gui.mainloop()

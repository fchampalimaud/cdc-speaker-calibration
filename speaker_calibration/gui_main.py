import tkinter as tk
import ctypes
from plot_frame import PlotFrame
from options_frame import OptionsFrame
import numpy as np
from classes import InputParameters
from main import noise_calibration

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

        if self.input_parameters.sound_type == "Noise":
            self.calibration_factor, self.fit_parameters = noise_calibration(
                float(self.options_frame.hardware_frame.fs_var.get()),
                self.config_window.input_parameters,
                self.calibration_factor if hasattr(self, "calibration_factor") else None,
                np.array([float(self.test_frame.slope_var.get()), float(self.test_frame.intercept_var.get())]),
                float(self.test_frame.min_var.get()),
                float(self.test_frame.max_var.get()),
                self.test_frame.steps_var.get(),
                self.sf_var.get(),
                self.cc_var.get(),
                self.tc_var.get(),
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

    def package_receiver(package: list, message: str):
        if message == "PSD Signal":
            print("TODO")
        elif message == "Inverse Filter":
            print("TODO")
        elif message == "Calibration Signals":
            print("TODO")
        elif message == "Calibration Curve":
            print("TODO")
        elif message == "Test Signals":
            print("TODO")
        elif message == "Test Plot":
            print("TODO")

    def change_plot(self, event):
        if self.options_frame.combobox_var.get() == "PSD Signal":
            print("TODO")
        elif self.options_frame.combobox_var.get() == "Inverse Filter":
            print("TODO")
        elif self.options_frame.combobox_var.get() == "Calibration Signals":
            print("TODO")
        elif self.options_frame.combobox_var.get() == "Calibration Curve":
            print("TODO")
        elif self.options_frame.combobox_var.get() == "Test Signals":
            print("TODO")
        elif self.options_frame.combobox_var.get() == "Test Plot":
            print("TODO")

        self.plot_frame.figure_canvas.draw_idle()


if __name__ == "__main__":
    gui = SpeakerCalibrationGUI()
    gui.mainloop()

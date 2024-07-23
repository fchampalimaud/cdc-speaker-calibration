import tkinter as tk
import numpy as np
from speaker_calibration.gui.controller.calibration_thread import AsyncCalibration


class SpeakerCalibrationController:
    """
    The controller object which serves as an intermediary between the frontend and backend.

    Attributes
    ----------
    model
        the backend object.
    view
        the frontend object.
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Changes the default values of the spinboxes of the settings window
        self.set_settings_defaults()

        self.view.config_frame.run_button["command"] = self.calibrate

    def set_settings_defaults(self):
        """
        Changes the default values of the spinboxes of the settings window.
        """

        setting_list = list(self.model.input_parameters.__dict__.values())

        # FIXME

        # for i in range(self.view.settings_window.settings_values.size):
        #     if isinstance(self.view.settings_window.settings_values[i], tk.IntVar):
        #         self.view.settings_window.settings_values[i].set(setting_list[i])
        #     else:
        #         self.view.settings_window.settings_values[i].set(str(setting_list[i]))

    def update_hardware(self):
        """
        Updates the hardware information in the model based on the inputs from the view.
        """

        self.model.hardware.fs_sc = self.view.config_frame.hardware_frame.fs_sc.get()
        self.model.hardware.harp_soundcard = bool(self.view.config_frame.hardware_frame.harp_soundcard.get())
        self.model.hardware.soundcard_com = self.view.config_frame.hardware_frame.soundcard_com.get()
        self.model.hardware.soundcard_id = ""
        self.model.hardware.harp_audio_amp = bool(self.view.config_frame.hardware_frame.harp_audio_amp.get())
        self.model.hardware.audio_amp_id = ""
        self.model.hardware.speaker_id = self.view.config_frame.hardware_frame.speaker_id.get()
        self.model.hardware.setup_id = self.view.config_frame.hardware_frame.setup_id.get()

    def update_settings(self):
        """
        Updates the InputParameters object in the model based on the inputs from the view's settings window.
        """

        values = []
        for i in range(self.view.settings_window.settings_values.size):
            if isinstance(self.view.settings_window.settings_values[i], tk.IntVar):
                values.append(self.view.settings_window.settings_values[i].get())
            else:
                values.append(float(self.view.settings_window.settings_values[i].get()))
        values.append(self.view.settings_window.sound_type.get())

        self.model.input_parameters.update(dict(zip(self.model.input_parameters.__dict__.keys(), values)))

    def update_calibration_parameters(self):
        """
        Updates the calibration parameters in the model based on inputs from the view.
        """

        self.model.calibration_parameters[0] = float(self.view.config_frame.test_frame.slope.get())
        self.model.calibration_parameters[1] = float(self.view.config_frame.test_frame.intercept.get())

    def calibrate(self):
        """
        Performs the speaker calibration on a new thread to not freeze the GUI.
        """

        # Updates the model data based on the inputs from the view.
        self.update_settings()
        self.update_hardware()
        self.update_calibration_parameters()

        # Initializes/Resets some attributes of the model object
        self.model.calibration_signals = np.zeros((self.model.input_parameters.att_steps, 2), dtype=np.ndarray)
        self.model.calibration_data = np.zeros((self.model.input_parameters.att_steps, 3), dtype=np.ndarray)
        self.test_signals = np.zeros((self.view.config_frame.test_frame.steps_var.get(), 2), dtype=np.ndarray)
        self.model.test_data = np.zeros((self.view.config_frame.test_frame.steps_var.get(), 3), dtype=np.ndarray)

        # Creates and runs the thread that executes the noise calibration
        if self.model.input_parameters.sound_type == "Noise":
            self.view.config_frame.run_button["state"] = tk.DISABLED
            calibration_thread = AsyncCalibration(
                self.model.hardware.fs_sc,
                self.model.input_parameters,
                self.model.hardware,
                self.model.inverse_filter,
                self.model.calibration_parameters,
                float(self.view.config_frame.test_frame.min_var.get()),
                float(self.view.config_frame.test_frame.max_var.get()),
                self.view.config_frame.test_frame.steps_var.get(),
                self.view.config_frame.speaker_filter.get(),
                self.view.config_frame.calibration_curve.get(),
                self.view.config_frame.test_calibration.get(),
                self.package_receiver,
            )
            calibration_thread.start()

            # Starts the monitorization of the thread
            self.monitor(calibration_thread)

    def monitor(self, thread):
        """
        Monitorizes the thread. If the thread is alive, this function is called recursively, otherwise some post-calibration operations are executed.

        Parameters
        ----------
        thread: Thread
            a Thread object.
        """

        if thread.is_alive():
            # Check the thread every 100 ms
            self.view.after(100, lambda: self.monitor(thread))
        else:
            # Activates the Run button again
            self.view.config_frame.run_button["state"] = tk.NORMAL

            # Updates the inverse filter and the calibration curve parameters
            self.model.inverse_filter = thread.inverse_filter
            self.model.calibration_parameters = thread.calibration_parameters

            # Updates the calibration curve parameters spinboxes in the view
            self.view.config_frame.test_frame.slope.set(str(self.model.calibration_parameters[0]))
            self.view.config_frame.test_frame.intercept.set(str(self.model.calibration_parameters[1]))

            # Saves the results
            save_string = str(self.model.hardware.speaker_id) + "_setup" + str(self.model.hardware.setup_id) + ".csv"
            np.savetxt(
                "output/inverse_filter_speaker" + save_string,
                self.model.inverse_filter,
                delimiter=",",
                fmt="%f",
            )
            np.savetxt(
                "output/fit_parameters_speaker" + save_string,
                self.model.calibration_parameters,
                delimiter=",",
                fmt="%f",
            )

    def package_receiver(self, package: list, message: str):
        """
        This is a callback function which interfaces with the noise_calibration function to update different attributes of the model based on the message it receives.

        Parameters
        ----------
        package : list
            contains the data used to update the attributes of the model. The package varies according to the message it receives.
        message : str
            used to check which set of instructions must be executed.
        """

        if message == "Inverse Filter":
            # Executed after the inverse filter is calculated
            self.model.inverse_filter = package[0]
            self.model.psd_signal[0] = package[1].signal
            self.model.psd_signal[1] = package[1].recorded_sound
        elif message == "Calibration":
            # Executed after calculating the dB SPL of each calibration signal
            self.model.calibration_signals[package[1], 0] = package[0].signal
            self.model.calibration_signals[package[1], 1] = package[0].recorded_sound
            self.model.calibration_data[package[1], 0] = package[0].db_spl
            self.model.calibration_data[package[1], 1] = package[0].db_fft
        elif message == "Test":
            # Executed after calculating the dB SPL of each test signal
            self.model.test_signals[package[1], 0] = package[0].signal
            self.model.test_signals[package[1], 1] = package[0].recorded_sound
            self.model.test_data[package[1], 0] = package[0].db_spl
            self.model.test_data[package[1], 1] = package[0].db_fft

        # Updates the GUI's plot
        self.update_plot(None)

    def update_plot(self, event):
        """
        Updates the plot based on the item selected in a combobox.

        Parameters
        ----------
        event
            this parameter is sent by the combobox when an event is triggered.
        """
        if self.view.config_frame.combobox_var.get() == "PSD Signal":
            self.view.plot_frame.plots[0].set_data(np.linspace(0, self.model.psd_signal[0].size - 1, self.model.psd_signal[0].size), self.model.psd_signal[0])
            self.view.plot_frame.plots[1].set_data(np.linspace(0, self.model.psd_signal[1].size - 1, self.model.psd_signal[1].size), self.model.psd_signal[1])
            self.view.plot_frame.plots[2].set_data([], [])
        elif self.view.config_frame.combobox_var.get() == "Inverse Filter":
            self.view.plot_frame.plots[0].set_data(self.model.inverse_filter)
            self.view.plot_frame.plots[1].set_data([], [])
            self.view.plot_frame.plots[2].set_data([], [])
        elif self.view.config_frame.combobox_var.get() == "Calibration Signals":
            self.view.plot_frame.plots[0].set_data(self.model.calibration_signals[:, 0])
            self.view.plot_frame.plots[1].set_data(self.model.calibration_signals[:, 1])
            self.view.plot_frame.plots[2].set_data([], [])
        elif self.view.config_frame.combobox_var.get() == "Calibration Data":
            self.view.plot_frame.plots[0].set_data(self.model.calibration_data[:, 0])
            self.view.plot_frame.plots[1].set_data(self.model.calibration_data[:, 1])
            self.view.plot_frame.plots[2].set_data([], [])
        elif self.view.config_frame.combobox_var.get() == "Test Signals":
            self.view.plot_frame.plots[0].set_data(self.model.test_signals[:, 0])
            self.view.plot_frame.plots[1].set_data(self.model.test_signals[:, 1])
            self.view.plot_frame.plots[2].set_data([], [])
        elif self.options_frame.combobox_var.get() == "Test Data":
            self.view.plot_frame.plots[0].set_data(self.model.test_data[:, 0])
            self.view.plot_frame.plots[1].set_data(self.model.test_data[:, 1])
            self.view.plot_frame.plots[2].set_data([], [])

        # Assures that the x and y axis are autoscaled when the figure is redrawn
        self.view.plot_frame.ax.relim()
        self.view.plot_frame.ax.autoscale_view()
        self.view.plot_frame.figure_canvas.draw_idle()

import tkinter as tk
import numpy as np
from speaker_calibration.gui.calibration_thread import AsyncCalibration


class SpeakerCalibrationController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        # Changes the default values of the spinboxes of the configuration window
        self.set_settings_defaults()

        self.view.config_frame.run_button["command"] = self.calibrate

    def set_settings_defaults(self):
        setting_list = list(self.model.input_parameters.__dict__.values())

        for i in range(self.view.settings_window.settings_values.size):
            if isinstance(self.view.settings_window.settings_values[i], tk.IntVar):
                self.view.settings_window.settings_values[i].set(setting_list[i])
            else:
                self.view.settings_window.settings_values[i].set(str(setting_list[i]))

    def update_hardware(self):
        self.model.hardware_config.fs_sc = self.view.config_frame.hardware_frame.fs_sc.get()
        self.model.hardware_config.harp_soundcard = bool(self.view.config_frame.hardware_frame.harp_soundcard.get())
        self.model.hardware_config.soundcard_com = self.view.config_frame.hardware_frame.soundcard_com.get()
        self.model.hardware_config.soundcard_id = ""
        self.model.hardware_config.harp_audio_amp = bool(self.view.config_frame.hardware_frame.harp_audio_amp.get())
        self.model.hardware_config.audio_amp_id = ""
        self.model.hardware_config.speaker_id = self.view.config_frame.hardware_frame.speaker_id.get()
        self.model.hardware_config.setup_id = self.view.config_frame.hardware_frame.setup_id.get()

    def update_settings(self):
        values = []
        for i in range(self.view.settings_window.settings_values.size):
            if isinstance(self.view.settings_window.settings_values[i], tk.IntVar):
                values.append(self.view.settings_window.settings_values[i].get())
            else:
                values.append(float(self.view.settings_window.settings_values[i].get()))
        values.append(self.view.settings_window.sound_type.get())

        self.model.input_parameters.update(dict(zip(self.model.input_parameters.__dict__.keys(), values)))

    def update_calibration_parameters(self):
        self.model.calibration_parameters[0] = float(self.view.config_frame.test_frame.slope.get())
        self.model.calibration_parameters[1] = float(self.view.config_frame.test_frame.intercept.get())

    def calibrate(self):
        self.update_settings()
        self.update_hardware()
        self.update_calibration_parameters()

        self.calibration_signals = np.zeros((self.model.input_parameters.att_steps, 2), dtype=np.ndarray)
        self.calibration_data = np.zeros((self.model.input_parameters.att_steps, 3), dtype=np.ndarray)
        self.test_signals = np.zeros((self.view.config_frame.test_frame.steps_var.get(), 2), dtype=np.ndarray)
        self.test_data = np.zeros((self.view.config_frame.test_frame.steps_var.get(), 3), dtype=np.ndarray)

        if self.model.input_parameters.sound_type == "Noise":
            self.view.config_frame.run_button["state"] = tk.DISABLED
            calibration_thread = AsyncCalibration(
                self.model.hardware_config.fs_sc,
                self.model.input_parameters,
                self.model.hardware_config,
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

            self.monitor(calibration_thread)

    def monitor(self, thread):
        if thread.is_alive():
            # check the thread every 100ms
            self.view.after(100, lambda: self.monitor(thread))
        else:
            self.view.config_frame.run_button["state"] = tk.NORMAL
            self.model.inverse_filter = thread.inverse_filter
            self.model.calibration_parameters = thread.calibration_parameters

            self.view.config_frame.test_frame.slope.set(str(self.model.calibration_parameters[0]))
            self.view.config_frame.test_frame.intercept.set(str(self.model.calibration_parameters[1]))

            save_string = str(self.model.hardware_config.speaker_id) + "_setup" + str(self.model.hardware_config.setup_id) + ".csv"
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
        if message == "Inverse Filter":
            self.model.inverse_filter = package[0]
            self.model.psd_signal[0] = package[1].signal
            self.model.psd_signal[1] = package[1].recorded_sound
        elif message == "Calibration":
            self.model.calibration_signals[package[1], 0] = package[0].signal
            self.model.calibration_signals[package[1], 1] = package[0].recorded_sound
            self.model.calibration_data[package[1], 0] = package[0].db_spl
            self.model.calibration_data[package[1], 1] = package[0].db_fft
        elif message == "Test":
            self.model.test_signals[package[1], 0] = package[0].signal
            self.model.test_signals[package[1], 1] = package[0].recorded_sound
            self.model.test_data[package[1], 0] = package[0].db_spl
            self.model.test_data[package[1], 1] = package[0].db_fft

        self.change_plot(None)

    def change_plot(self, event):
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

        self.view.plot_frame.ax.relim()
        self.view.plot_frame.ax.autoscale_view()
        self.view.plot_frame.figure_canvas.draw_idle()

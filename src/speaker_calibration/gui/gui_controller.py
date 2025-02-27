import tkinter as tk
import numpy as np
from speaker_calibration.gui.controller.calibration_thread import AsyncCalibration
from speaker_calibration.protocol.calibration_steps import save_data
from speaker_calibration.settings.hardware import HarpSoundCard, ComputerSoundCard


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
        # self.set_settings_defaults()

        self.view.run_button["command"] = self.calibrate
        self.view.plot_config.plot.combobox.bind(
            "<<ComboboxSelected>>", self.change_plot
        )

        # self.view.config_frame.plot_config.calibration_signal["command"] = (
        #     self.view.update_plot
        # )
        # self.view.config_frame.plot_config.test_signal["command"] = (
        #     self.view.update_plot
        # )
        # self.view.config_frame.plot_config.signal_cb["command"] = self.view.update_plot
        # self.view.config_frame.plot_config.recorded_sound_cb["command"] = (
        #     self.view.update_plot
        # )

        # self.view.config_frame.plot_config.plot_cb.bind(
        #     "<<ComboboxSelected>>", self.view.update_plot
        # )

    def open_calibration_factor(self):
        filename = tk.filedialog.askopenfilename()
        self.model.inverse_filter = np.loadtxt(filename, delimiter=",")

        self.inverse_filter_var.set("Filter Loaded")

    def update_hardware(self):
        """
        Updates the hardware information in the model based on the inputs from the view.
        """

        frame = self.view.hardware

        self.model.hardware.is_harp = frame.is_harp.get()
        self.model.hardware.speaker_id = frame.speaker_id.get()
        self.model.hardware.setup_id = frame.setup_id.get()

        if self.model.hardware.is_harp:
            self.model.hardware.soundcard = HarpSoundCard(
                com_port=frame.frames[0].port.get(), fs=frame.frames[0].fs.get()
            )
            if frame.frames[0].soundcard_id.get() != "":
                self.model.hardware.soundcard.soundcard_id = frame.frames[
                    0
                ].soundcard_id.get()

            if frame.frames[0].audio_amp_id.get() != "":
                self.model.hardware.soundcard.audio_amp_id = frame.frames[
                    0
                ].audio_amp_id.get()
        else:
            self.model.hardware.soundcard = ComputerSoundCard(
                soundcard_name=frame.frames[1].soundcard_name.get(),
                fs=frame.frames[1].fs.get(),
            )

    def update_settings(self):
        frame = self.view.settings_window

        self.model.settings.sound_type = frame.sound_type.get()
        self.model.settings.reference_pressure = frame.reference_pressure.get()
        self.model.settings.sound.ramp_time = frame.ramp_time.get()
        self.model.settings.sound.amplification = frame.amplification.get()
        self.model.settings.sound.freq.num_freqs = frame.freq_frame.num_freqs.get()
        self.model.settings.sound.freq.min_freq = frame.freq_frame.min_value.get()
        self.model.settings.sound.freq.max_freq = frame.freq_frame.max_value.get()
        self.model.settings.sound.filter.filter_input = (
            frame.filter_frame.filter_input.get()
        )
        self.model.settings.sound.filter.filter_acquisition = (
            frame.filter_frame.filter_acquisition.get()
        )
        self.model.settings.sound.filter.min_value = frame.filter_frame.min_value.get()
        self.model.settings.sound.filter.max_value = frame.filter_frame.max_value.get()
        self.model.settings.sound.inverse_filter.determine_filter = (
            frame.inverse_filter.determine_filter.get()
        )
        self.model.settings.sound.inverse_filter.sound_duration = (
            frame.inverse_filter.sound_duration.get()
        )
        self.model.settings.sound.inverse_filter.time_constant = (
            frame.inverse_filter.time_constant.get()
        )
        self.model.settings.sound.calibration.calibrate = (
            frame.calibration.calibrate.get()
        )
        self.model.settings.sound.calibration.sound_duration = (
            frame.calibration.sound_duration.get()
        )
        self.model.settings.sound.calibration.att_min = frame.calibration.att_min.get()
        self.model.settings.sound.calibration.att_max = frame.calibration.att_max.get()
        self.model.settings.sound.calibration.att_steps = (
            frame.calibration.att_steps.get()
        )
        self.model.settings.sound.test_calibration.test = (
            frame.test_calibration.test.get()
        )
        self.model.settings.sound.test_calibration.sound_duration = (
            frame.test_calibration.sound_duration.get()
        )
        self.model.settings.sound.test_calibration.db_min = (
            frame.test_calibration.db_min.get()
        )
        self.model.settings.sound.test_calibration.db_max = (
            frame.test_calibration.db_max.get()
        )
        self.model.settings.sound.test_calibration.db_steps = (
            frame.test_calibration.db_steps.get()
        )

    def calibrate(self):
        """
        Performs the speaker calibration on a new thread to not freeze the GUI.
        """

        # Updates the model data based on the inputs from the view.
        self.update_settings()
        self.update_hardware()
        self.model.initialize_data()
        self.view.generate_figures()
        # self.update_calibration_parameters()

        # self.view.config_frame.plot_config.calibration_signal_var.set(0)
        # self.view.config_frame.plot_config.test_signal_var.set(0)
        # self.view.config_frame.plot_config.calibration_signal["to"] = (
        #     self.model.calibration_signals.size - 1
        # )
        # self.view.config_frame.plot_config.test_signal["to"] = (
        #     self.model.test_signals.size - 1
        # )

        # # Creates and runs the thread that executes the noise calibration
        # if self.model.input_parameters.sound_type == "Noise":
        #     self.view.config_frame.run_button["state"] = tk.DISABLED
        #     calibration_thread = AsyncCalibration(
        #         self.model.hardware,
        #         self.model.input_parameters,
        #         self.model.inverse_filter,
        #         self.model.calibration_parameters,
        #         self.package_receiver,
        #     )
        #     calibration_thread.start()

        #     # Starts the monitorization of the thread
        #     self.monitor(calibration_thread)

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
            self.view.run_button["state"] = tk.NORMAL

            # Updates the inverse filter and the calibration curve parameters
            self.model.inverse_filter = thread.inverse_filter
            self.model.calibration_parameters = thread.calibration_parameters

            # Updates the calibration curve parameters spinboxes in the view
            self.view.slope.set(str(self.model.calibration_parameters[0]))
            self.view.intercept.set(str(self.model.calibration_parameters[1]))

            # Saves the results
            save_data(
                self.model.input_parameters,
                self.model.hardware,
                self.model.inverse_filter,
                self.model.calibration_parameters,
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
            self.model.psd_signal = package[1]
        elif message == "Pre-calibration":
            self.model.calibration_data[:, 0] = package[0]
        elif message == "Calibration":
            # Executed after calculating the dB SPL of each calibration signal
            self.model.calibration_signals[package[1]] = package[0]
            self.model.calibration_data[package[1], 1] = package[0].db_spl
            self.model.calibration_data[package[1], 2] = package[0].db_fft
        elif message == "Pre-test":
            self.model.test_data[:, 0] = package[0]
        elif message == "Test":
            # Executed after calculating the dB SPL of each test signal
            self.model.test_signals[package[1]] = package[0]
            self.model.test_data[package[1], 1] = package[0].db_spl
            self.model.test_data[package[1], 2] = package[0].db_fft

        # Updates the GUI's plot
        self.view.update_plot()

    def change_plot(self, event=None):
        plot_name = self.view.plot_config.plot
        data = self.model.data
        if self.view.settings_window.sound_type.get() == "Noise":
            self.view.plot_config.grid_forget()
            if plot_name.get() == "PSD Signal":
                self.view.plots[0].set_data(
                    data.inverse_filter.signal[:, 0], data.inverse_filter.signal[:, 1]
                )
                self.view.plots[1].set_data(
                    data.inverse_filter.recording[:, 0],
                    data.inverse_filter.recording[:, 1],
                )
            elif plot_name.get() == "Inverse Filter":
                self.view.plots[0].set_data(
                    data.inverse_filter.filter[:, 0], data.inverse_filter.filter[:, 1]
                )
                self.view.plots[1].set_data([], [])
            elif plot_name.get() == "Calibration Signals":
                self.view.plot_config.frames[0].signal_index.spinbox.config(
                    to=data.calibration.signals.shape[1] - 1
                )
                self.view.plot_config.frames[0].signal_index.set(0)
                self.view.plot_config.frames[0].grid(column=0, row=1)
                index = self.view.plot_config.frames[0].signal_index.get() + 1
                self.view.plots[0].set_data(
                    data.calibration.signals[:, 0], data.calibration.signals[:, index]
                )
                self.view.plots[1].set_data(
                    data.calibration.recorded_sounds[:, 0],
                    data.calibration.recorded_sounds[:, index],
                )
            elif plot_name.get() == "Calibration Data":
                self.view.plots[0].set_data(
                    data.calibration.data[:, 0], data.calibration.data[:, 1]
                )
                self.view.plots[1].set_data([], [])
            elif plot_name.get() == "Test Signals":
                self.view.plot_config.frames[0].signal_index.spinbox.config(
                    to=data.test.signals.shape[1] - 1
                )
                self.view.plot_config.frames[0].signal_index.set(0)
                self.view.plot_config.frames[0].grid(column=0, row=1)
                index = self.view.plot_config.frames[0].signal_index.get() + 1
                self.view.plots[0].set_data(
                    data.test.signals[:, 0], data.test.signals[:, index]
                )
                self.view.plots[1].set_data(
                    data.test.recorded_sounds[:, 0], data.test.recorded_sounds[:, index]
                )
            elif plot_name.get() == "Test Data":
                self.view.plots[0].set_data(data.test.data[:, 0], data.test.data[:, 1])
                self.view.plots[1].set_data(data.test.data[:, 0], data.test.data[:, 0])

            # TODO: pure tones

        # self.view.ax.relim()
        # self.view.ax.autoscale_view()
        self.view.canvas.draw_idle()

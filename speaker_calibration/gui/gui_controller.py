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

        self.view.config_frame.run_button["command"] = self.calibrate
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

    # def set_settings_defaults(self):
    #     """
    #     Changes the default values of the spinboxes of the settings window.
    #     """

    #     setting_list = list(self.model.input_parameters.__dict__.values())
    #     general = [x for x in setting_list if not isinstance(x, dict)][1:]
    #     noise_all = list([x for x in setting_list if isinstance(x, dict)][0].values())
    #     noise = [x for x in noise_all if not isinstance(x, dict)]
    #     psd = list([x for x in noise_all if isinstance(x, dict)][0].values())
    #     calibration = list([x for x in noise_all if isinstance(x, dict)][1].values())
    #     test = list([x for x in noise_all if isinstance(x, dict)][2].values())
    #     pure_tone_all = list(
    #         [x for x in setting_list if isinstance(x, dict)][1].values()
    #     )
    #     pure_tone = [x for x in pure_tone_all if not isinstance(x, dict)]
    #     pt_calibration = list(
    #         [x for x in pure_tone_all if isinstance(x, dict)][0].values()
    #     )
    #     pt_test = list([x for x in pure_tone_all if isinstance(x, dict)][1].values())

    #     # General Frame
    #     for i in range(self.view.settings_window.general.variables.size):
    #         if isinstance(self.view.settings_window.general.variables[i], tk.IntVar):
    #             self.view.settings_window.general.variables[i].set(general[i])
    #         else:
    #             self.view.settings_window.general.variables[i].set(str(general[i]))

    #     # Noise Frame
    #     for i in range(self.view.settings_window.frames[0].variables.size):
    #         if isinstance(self.view.settings_window.frames[0].variables[i], tk.IntVar):
    #             self.view.settings_window.frames[0].variables[i].set(noise[i])
    #         else:
    #             self.view.settings_window.frames[0].variables[i].set(str(noise[i]))

    #     # PSD Frame
    #     for i in range(self.view.settings_window.frames[0].psd.variables.size):
    #         if isinstance(
    #             self.view.settings_window.frames[0].psd.variables[i], tk.IntVar
    #         ):
    #             self.view.settings_window.frames[0].psd.variables[i].set(psd[i])
    #         else:
    #             self.view.settings_window.frames[0].psd.variables[i].set(str(psd[i]))

    #     # Calibration Frame
    #     for i in range(self.view.settings_window.frames[0].calibration.variables.size):
    #         if isinstance(
    #             self.view.settings_window.frames[0].calibration.variables[i], tk.IntVar
    #         ):
    #             self.view.settings_window.frames[0].calibration.variables[i].set(
    #                 calibration[i]
    #             )
    #         else:
    #             self.view.settings_window.frames[0].calibration.variables[i].set(
    #                 str(calibration[i])
    #             )

    #     # Test Frame
    #     for i in range(self.view.settings_window.frames[0].test.variables.size):
    #         if isinstance(
    #             self.view.settings_window.frames[0].test.variables[i], tk.IntVar
    #         ):
    #             self.view.settings_window.frames[0].test.variables[i].set(test[i])
    #         else:
    #             self.view.settings_window.frames[0].test.variables[i].set(str(test[i]))

    #     # Pure Tone Frame
    #     for i in range(self.view.settings_window.frames[1].variables.size):
    #         if isinstance(self.view.settings_window.frames[1].variables[i], tk.IntVar):
    #             self.view.settings_window.frames[1].variables[i].set(pure_tone[i])
    #         else:
    #             self.view.settings_window.frames[1].variables[i].set(str(pure_tone[i]))

    #     # Pure Tone Calibration Frame
    #     for i in range(self.view.settings_window.frames[1].calibration.variables.size):
    #         if isinstance(
    #             self.view.settings_window.frames[1].calibration.variables[i], tk.IntVar
    #         ):
    #             self.view.settings_window.frames[1].calibration.variables[i].set(
    #                 pt_calibration[i]
    #             )
    #         else:
    #             self.view.settings_window.frames[1].calibration.variables[i].set(
    #                 str(pt_calibration[i])
    #             )

    #     # Pure Tone Test Frame
    #     for i in range(self.view.settings_window.frames[1].test.variables.size):
    #         if isinstance(
    #             self.view.settings_window.frames[1].test.variables[i], tk.IntVar
    #         ):
    #             self.view.settings_window.frames[1].test.variables[i].set(pt_test[i])
    #         else:
    #             self.view.settings_window.frames[1].test.variables[i].set(
    #                 str(pt_test[i])
    #             )

    def update_hardware(self):
        """
        Updates the hardware information in the model based on the inputs from the view.
        """

        frame = self.view.config_frame.hardware_frame

        self.model.hardware.is_harp = frame.is_harp.get()
        self.model.hardware.speaker_id = frame.speaker_id.get()
        self.model.hardware.setup_id = frame.setup_id.get()

        if self.model.hardware.is_harp:
            self.model.hardware.sound = HarpSoundCard(
                com_port=frame.frames[0].port.get(), fs=frame.frames[0].fs.get()
            )
            if frame.soundcard_id.get() != "":
                self.model.hardware.sound.soundcard_id = frame.frames[
                    0
                ].soundcard_id.get()

            if frame.setup_id.get() != "":
                self.model.hardware.sound.audio_amp_id = frame.frames[
                    0
                ].audio_amp_id.get()
        else:
            self.model.hardware.sound = ComputerSoundCard(
                soundcard_name=frame.frames[1].soundcard_name.get(),
                fs=frame.frames[1].fs.get(),
            )

    # def update_settings(self):
    #     """
    #     Updates the InputParameters object in the model based on the inputs from the view's settings window.
    #     """

    #     setting_list = list(self.model.input_parameters.__dict__.values())
    #     noise_all = list([x for x in setting_list if isinstance(x, dict)][0].values())
    #     noise_keys = [x for x in setting_list if isinstance(x, dict)][0].keys()
    #     psd_keys = [x for x in noise_all if isinstance(x, dict)][0].keys()
    #     calibration_keys = [x for x in noise_all if isinstance(x, dict)][1].keys()
    #     test_keys = [x for x in noise_all if isinstance(x, dict)][2].keys()
    #     pure_tone_keys = [x for x in setting_list if isinstance(x, dict)][1].keys()

    #     # General Frame
    #     general = []
    #     general.append(self.view.settings_window.general.sound_type.get())
    #     for i in range(self.view.settings_window.general.variables.size):
    #         if isinstance(self.view.settings_window.general.variables[i], tk.IntVar):
    #             general.append(self.view.settings_window.general.variables[i].get())
    #         else:
    #             general.append(
    #                 float(self.view.settings_window.general.variables[i].get())
    #             )

    #     # Noise Frame
    #     noise = []
    #     for i in range(self.view.settings_window.noise.variables.size):
    #         if isinstance(self.view.settings_window.noise.variables[i], tk.IntVar):
    #             noise.append(self.view.settings_window.noise.variables[i].get())
    #         else:
    #             noise.append(float(self.view.settings_window.noise.variables[i].get()))

    #     # PSD Frame
    #     psd = []
    #     for i in range(self.view.settings_window.noise.psd.variables.size):
    #         if isinstance(self.view.settings_window.noise.psd.variables[i], tk.IntVar):
    #             psd.append(self.view.settings_window.noise.psd.variables[i].get())
    #         else:
    #             psd.append(
    #                 float(self.view.settings_window.noise.psd.variables[i].get())
    #             )

    #     # Calibration Frame
    #     calibration = []
    #     for i in range(self.view.settings_window.noise.calibration.variables.size):
    #         if isinstance(
    #             self.view.settings_window.noise.calibration.variables[i], tk.IntVar
    #         ):
    #             calibration.append(
    #                 self.view.settings_window.noise.calibration.variables[i].get()
    #             )
    #         else:
    #             calibration.append(
    #                 float(
    #                     self.view.settings_window.noise.calibration.variables[i].get()
    #                 )
    #             )

    #     # Test Frame
    #     test = []
    #     for i in range(self.view.settings_window.noise.test.variables.size):
    #         if isinstance(self.view.settings_window.noise.test.variables[i], tk.IntVar):
    #             test.append(self.view.settings_window.noise.test.variables[i].get())
    #         else:
    #             test.append(
    #                 float(self.view.settings_window.noise.test.variables[i].get())
    #             )

    #     # Pure Tone Frame
    #     pure_tone = []
    #     for i in range(self.view.settings_window.pure_tone.variables.size):
    #         if isinstance(self.view.settings_window.pure_tone.variables[i], tk.IntVar):
    #             pure_tone.append(self.view.settings_window.pure_tone.variables[i].get())
    #         else:
    #             pure_tone.append(
    #                 float(self.view.settings_window.pure_tone.variables[i].get())
    #             )

    #     psd_dict = dict(zip(psd_keys, psd))
    #     calibration_dict = dict(zip(calibration_keys, calibration))
    #     test_dict = dict(zip(test_keys, test))
    #     noise.append(psd_dict)
    #     noise.append(calibration_dict)
    #     noise.append(test_dict)
    #     noise_dict = dict(zip(noise_keys, noise))
    #     pure_tone_dict = dict(zip(pure_tone_keys, pure_tone))
    #     general.append(noise_dict)
    #     general.append(pure_tone_dict)
    #     self.model.input_parameters.update(
    #         dict(zip(self.model.input_parameters.__dict__.keys(), general))
    #     )

    # def update_calibration_parameters(self):
    #     """
    #     Updates the calibration parameters in the model based on inputs from the view.
    #     """

    #     self.model.calibration_parameters[0] = float(self.view.config_frame.slope.get())
    #     self.model.calibration_parameters[1] = float(
    #         self.view.config_frame.intercept.get()
    #     )

    def calibrate(self):
        """
        Performs the speaker calibration on a new thread to not freeze the GUI.
        """

        # Updates the model data based on the inputs from the view.
        self.update_settings()
        self.update_hardware()
        # self.update_calibration_parameters()

        # Initializes/Resets some attributes of the model object
        self.model.calibration_signals = np.zeros(
            (self.model.input_parameters.noise["calibration"]["att_steps"]),
            dtype=np.ndarray,
        )
        self.model.calibration_data = np.zeros(
            (self.model.input_parameters.noise["calibration"]["att_steps"], 3),
            dtype=np.ndarray,
        )
        self.model.test_signals = np.zeros(
            (self.model.input_parameters.noise["test"]["db_steps"]), dtype=np.ndarray
        )
        self.model.test_data = np.zeros(
            (self.model.input_parameters.noise["test"]["db_steps"], 3), dtype=np.ndarray
        )

        self.view.config_frame.plot_config.calibration_signal_var.set(0)
        self.view.config_frame.plot_config.test_signal_var.set(0)
        self.view.config_frame.plot_config.calibration_signal["to"] = (
            self.model.calibration_signals.size - 1
        )
        self.view.config_frame.plot_config.test_signal["to"] = (
            self.model.test_signals.size - 1
        )

        # Creates and runs the thread that executes the noise calibration
        if self.model.input_parameters.sound_type == "Noise":
            self.view.config_frame.run_button["state"] = tk.DISABLED
            calibration_thread = AsyncCalibration(
                self.model.hardware,
                self.model.input_parameters,
                self.model.inverse_filter,
                self.model.calibration_parameters,
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
            self.view.config_frame.slope.set(str(self.model.calibration_parameters[0]))
            self.view.config_frame.intercept.set(
                str(self.model.calibration_parameters[1])
            )

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

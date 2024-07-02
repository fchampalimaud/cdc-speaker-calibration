import tkinter as tk
from tkinter import ttk
import matplotlib
# import matplotlib.pyplot as plt

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class PlotFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # prepare data
        data = {"Python": 11.27, "C": 11.16, "Java": 10.46, "C++": 7.5, "C#": 5.26}
        languages = data.keys()
        popularity = data.values()

        # create a figure
        figure = Figure(figsize=(6, 4), dpi=100)

        # create FigureCanvasTkAgg object
        figure_canvas = FigureCanvasTkAgg(figure, self)

        # create the toolbar
        NavigationToolbar2Tk(figure_canvas, self)

        # create axes
        axes = figure.add_subplot()

        # create the barchart
        axes.bar(languages, popularity)
        axes.set_title("Top 5 Programming Languages")
        axes.set_ylabel("Popularity")

        figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)


class OptionsFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        self.config_window = ConfigurationWindow()

        self.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.grid_rowconfigure(i, weight=1)

        # label
        self.hardware_frame = HardwareFrame(self)
        self.hardware_frame.grid(column=0, row=0)

        self.combobox = ttk.Combobox(self)
        self.combobox.grid(column=0, row=1)

        # button
        self.config_button = ttk.Button(self, text="Open Configuration Window", command=self.config_window.deiconify)
        self.config_button.grid(column=0, row=2)

        # button
        self.run_button = ttk.Button(self, text="Run")
        self.run_button.grid(column=0, row=3)


class HardwareFrame(ttk.LabelFrame):
    def __init__(self, container, text="Hardware Settings"):
        super().__init__(container, text=text)

        self.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)

        # Parameters Frame
        self.par_frame = tk.Frame(self)
        self.par_frame.grid(column=0, row=0, pady=5)

        self.port_frame = tk.Frame(self.par_frame)
        self.port_frame.grid(column=0, row=0, padx=10)

        self.port_label = ttk.Label(self.port_frame, text="Port")
        self.port_label.grid(column=0, row=0, sticky="e")

        self.port_cb = ttk.Combobox(self.port_frame, width=5)
        self.port_cb.grid(column=1, row=0, sticky="w")

        self.fs_frame = tk.Frame(self.par_frame)
        self.fs_frame.grid(column=1, row=0, padx=10)

        self.fs_label = ttk.Label(self.fs_frame, text="Sampling Frequency (Hz)")
        self.fs_label.grid(column=0, row=0, sticky="e")

        self.fs_cb = ttk.Combobox(self.fs_frame, width=10)
        self.fs_cb.grid(column=1, row=0, sticky="w")

        # self.harp_soundcard_cb = ttk.Checkbutton(self, text="Harp SoundCard")
        # self.harp_soundcard_cb.grid(column=0, row=0)

        # self.sc_id_text = ttk.Entry(self)
        # self.sc_id_text.grid(column=2, row=0)

        # self.harp_amp_cb = ttk.Checkbutton(self, text="Harp Amp")
        # self.harp_amp_cb.grid(column=0, row=1)

        # self.amp_id_text = ttk.Entry(self)
        # self.amp_id_text.grid(column=1, row=1)

        # ID frame
        self.id_frame = tk.Frame(self)
        self.id_frame.grid(column=0, row=3, pady=5)

        self.speaker_frame = tk.Frame(self.id_frame)
        self.speaker_frame.grid(column=0, row=0, padx=10)

        self.speaker_id_label = ttk.Label(self.speaker_frame, text="Speaker ID")
        self.speaker_id_label.grid(column=0, row=0, sticky="e")

        self.speaker_id_sb = ttk.Spinbox(self.speaker_frame, width=5)
        self.speaker_id_sb.grid(column=1, row=0, sticky="w")

        self.setup_frame = tk.Frame(self.id_frame)
        self.setup_frame.grid(column=1, row=0, padx=10)

        self.setup_id_label = ttk.Label(self.setup_frame, text="Setup ID")
        self.setup_id_label.grid(column=0, row=0, sticky="e")

        self.setup_id_sb = ttk.Spinbox(self.setup_frame, width=5)
        self.setup_id_sb.grid(column=1, row=0, sticky="w")


class ConfigurationWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()

        self.geometry("400x600")
        self.resizable(0, 0)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.withdraw()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        for i in range(16):
            self.grid_rowconfigure(i, weight=1)

        # fs_adc
        self.fs_label = ttk.Label(self, text="ADC Sampling Frequency (Hz)")
        self.fs_label.grid(column=0, row=0, sticky="e")

        self.fs_var = tk.IntVar(self, 250000)
        self.fs_sb = ttk.Spinbox(self, from_=0, to=250000, textvariable=self.fs_var)
        self.fs_sb.grid(column=1, row=0, sticky="w")

        # sound_duration_psd
        self.duration_psd_label = ttk.Label(self, text="PSD Calibration Sound Duration (s)")
        self.duration_psd_label.grid(column=0, row=1, sticky="e")

        self.duration_psd_var = tk.IntVar(self, 30)
        self.duration_psd_sb = ttk.Spinbox(self, from_=1, to=60, textvariable=self.duration_psd_var)
        self.duration_psd_sb.grid(column=1, row=1, sticky="w")

        # sound_duration_db
        self.duration_db_label = ttk.Label(self, text="dB Calibration Sound Duration (s)")
        self.duration_db_label.grid(column=0, row=2, sticky="e")

        self.duration_db_var = tk.IntVar(self, 15)
        self.duration_db_sb = ttk.Spinbox(self, from_=1, to=60, textvariable=self.duration_db_var)
        self.duration_db_sb.grid(column=1, row=2, sticky="w")

        # sound_duration_test
        self.duration_test_label = ttk.Label(self, text="Test Calibration Sound Duration (s)")
        self.duration_test_label.grid(column=0, row=3, sticky="e")

        self.duration_test_var = tk.IntVar(self, 5)
        self.duration_test_sb = ttk.Spinbox(self, from_=1, to=60, textvariable=self.duration_test_var)
        self.duration_test_sb.grid(column=1, row=3, sticky="w")

        # ramp_time
        self.ramp_time_label = ttk.Label(self, text="Ramp Time (s)")
        self.ramp_time_label.grid(column=0, row=4, sticky="e")

        self.ramp_time_var = tk.StringVar(self, "0.005")
        self.ramp_time_sb = ttk.Spinbox(self, from_=0.005, to=1, increment=0.005, textvariable=self.ramp_time_var)
        self.ramp_time_sb.grid(column=1, row=4, sticky="w")

        # reference_pressure
        self.pressure_label = ttk.Label(self, text="Reference Pressure (Pa)")
        self.pressure_label.grid(column=0, row=5, sticky="e")

        self.pressure_var = tk.StringVar(self, "0.00002")
        self.pressure_sb = ttk.Spinbox(self, from_=0.000001, to=1, increment=0.000005, textvariable=self.pressure_var)
        self.pressure_sb.grid(column=1, row=5, sticky="w")

        # mic_factor
        self.mic_factor_label = ttk.Label(self, text="Microphone Factor (V/Pa)")
        self.mic_factor_label.grid(column=0, row=6, sticky="e")

        self.mic_factor_var = tk.StringVar(self, "10")
        self.mic_factor_sb = ttk.Spinbox(self, from_=0, to=100, increment=0.1, textvariable=self.mic_factor_var)
        self.mic_factor_sb.grid(column=1, row=6, sticky="w")

        # att_min
        self.att_min_label = ttk.Label(self, text="Minimum Attenuation")
        self.att_min_label.grid(column=0, row=7, sticky="e")

        self.att_min_var = tk.StringVar(self, "0")
        self.att_min_sb = ttk.Spinbox(self, from_=-10, to=0, increment=0.1, textvariable=self.att_min_var)
        self.att_min_sb.grid(column=1, row=7, sticky="w")

        # att_max
        self.att_max_label = ttk.Label(self, text="Maximum Attenuation")
        self.att_max_label.grid(column=0, row=8, sticky="e")

        self.att_max_var = tk.StringVar(self, "-1")
        self.att_max_sb = ttk.Spinbox(self, from_=-10, to=0, increment=0.1, textvariable=self.att_max_var)
        self.att_max_sb.grid(column=1, row=8, sticky="w")

        # att_steps
        self.att_steps_label = ttk.Label(self, text="Attenuation Steps")
        self.att_steps_label.grid(column=0, row=9, sticky="e")

        self.att_steps_var = tk.IntVar(self, 15)
        self.att_steps_sb = ttk.Spinbox(self, from_=1, to=100, textvariable=self.att_steps_var)
        self.att_steps_sb.grid(column=1, row=9, sticky="w")

        # smooth_window
        self.smooth_window_label = ttk.Label(self, text="Smoothing Window")
        self.smooth_window_label.grid(column=0, row=10, sticky="e")

        self.smooth_window_var = tk.IntVar(self, 15)
        self.smooth_window_sb = ttk.Spinbox(self, from_=1, to=100, textvariable=self.smooth_window_var)
        self.smooth_window_sb.grid(column=1, row=10, sticky="w")

        # time_constant
        self.time_constant_label = ttk.Label(self, text="Time Constant (s)")
        self.time_constant_label.grid(column=0, row=11, sticky="e")

        self.time_constant_var = tk.StringVar(self, "0.025")
        self.time_constant_sb = ttk.Spinbox(self, from_=0.001, to=10, increment=0.001, textvariable=self.time_constant_var)
        self.time_constant_sb.grid(column=1, row=11, sticky="w")

        # freq_min
        self.freq_min_label = ttk.Label(self, text="Minimum Frequency (Hz)")
        self.freq_min_label.grid(column=0, row=12, sticky="e")

        self.freq_min_var = tk.StringVar(self, "5000")
        self.freq_min_sb = ttk.Spinbox(self, from_=0, to=80000, increment=0.1, textvariable=self.freq_min_var)
        self.freq_min_sb.grid(column=1, row=12, sticky="w")

        # freq_max
        self.freq_max_label = ttk.Label(self, text="Maximum Frequency (Hz)")
        self.freq_max_label.grid(column=0, row=13, sticky="e")

        self.freq_max_var = tk.StringVar(self, "20000")
        self.freq_max_sb = ttk.Spinbox(self, from_=0, to=80000, increment=0.1, textvariable=self.freq_max_var)
        self.freq_max_sb.grid(column=1, row=13, sticky="w")

        # amplification
        self.amplification_label = ttk.Label(self, text="Amplification")
        self.amplification_label.grid(column=0, row=14, sticky="e")

        self.amplification_var = tk.StringVar(self, "1")
        self.amplification_sb = ttk.Spinbox(self, from_=0, to=1, increment=0.01, textvariable=self.amplification_var)
        self.amplification_sb.grid(column=1, row=14, sticky="w")

        # sound_type
        self.sound_type_label = ttk.Label(self, text="Sound Type")
        self.sound_type_label.grid(column=0, row=15, sticky="e")

        self.sound_type_cb = ttk.Combobox(self)
        self.sound_type_cb.grid(column=1, row=15, sticky="w")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # configure the root window
        self.title("Speaker Calibration")

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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(column=0, row=0, sticky="nsew")

        self.options_frame = OptionsFrame(self)
        self.options_frame.grid(column=1, row=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()

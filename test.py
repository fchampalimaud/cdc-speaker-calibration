import tkinter as tk
import tkinter as ttk
from tkinter import Frame
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from speaker_calibration.gui.view.settings_window import SettingsWindow
from speaker_calibration.gui.view.hardware_frame import HardwareFrame
from speaker_calibration.gui.view.plot_config_frame import PlotConfigFrame

import ctypes

ctypes.windll.shcore.SetProcessDpiAwareness(1)


class App(tk.Tk):
    def __init__(self):
        super().__init__()  # Initialize the Tk class
        self.title("Tkinter Matplotlib Example")
        self.call("tk", "scaling", 1.25)
        self.update_idletasks()

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  # Left side (figure and toolbar)

        # Create a frame for the grid layout
        self.frame = ttk.Frame(self)
        self.frame.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)  # Left side (figure and toolbar)
        self.frame.grid_columnconfigure(1, weight=1)  # Right side (button)

        # Create a frame for the figure and toolbar
        self.figure_frame = ttk.Frame(self.frame)
        self.figure_frame.grid(row=0, column=0, sticky="nsew")

        # Position the settings widgets frame
        self.config = ttk.Frame(self)
        self.config.grid(column=1, row=0, sticky="nsew")

        self.config.grid_columnconfigure(0, weight=1)
        for i in range(5):
            self.config.grid_rowconfigure(i, weight=1)

        self.logo = tk.PhotoImage(file="assets/cf_logo.png")
        self.logo_label = tk.Label(self.config, image=self.logo)
        self.logo_label.grid(column=0, row=0)

        # button
        self.settings_button = ttk.Button(self.config, text="Open Settings Window")
        self.settings_button.grid(column=0, row=1)

        self.plot_config = PlotConfigFrame(self.config)
        self.plot_config.grid(column=0, row=2)

        # label
        self.hardware = HardwareFrame(self.config)
        self.hardware.grid(column=0, row=3)

        # button
        self.run_button = ttk.Button(
            self.config, text="Run", command=self.recreate_figure
        )
        self.run_button.grid(row=4, column=0, pady=5)

        # # Create a frame for the button
        # self.button_frame = ttk.Frame(self.frame)
        # self.button_frame.grid(row=0, column=1, sticky="nsew")

        # self.button_frame.grid_rowconfigure(0, weight=1)
        # self.button_frame.grid_columnconfigure(
        #     0, weight=1
        # )  # Left side (figure and toolbar)

        # Create the initial figure
        self.create_figure()

        # # Create a button to recreate the figure
        # self.button = ttk.Button(
        #     self.button_frame, text="Recreate Figure", command=self.recreate_figure
        # )
        # self.button.grid(row=0, column=0)

    def create_figure(self):
        # Create a new Matplotlib figure
        self.figure = plt.Figure(figsize=(5, 5), dpi=100)
        self.ax = self.figure.add_subplot(111)

        # Create a canvas for the figure
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.figure_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create a navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.figure_frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Plot the initial data
        # self.plot()

    def plot(self):
        # Clear the previous plot
        self.ax.clear()
        # Generate some data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        # Plot the data
        self.ax.plot(x, y)
        self.ax.set_title("Sine Wave")
        self.ax.set_xlabel("X-axis")
        self.ax.set_ylabel("Y-axis")
        # Draw the canvas
        self.canvas.draw()

    def recreate_figure(self):
        # Destroy the existing canvas and toolbar
        self.canvas.get_tk_widget().destroy()
        self.toolbar.destroy()
        # Create a new figure
        self.create_figure()


if __name__ == "__main__":
    app = App()  # Create an instance of the App class
    app.mainloop()  # Start the Tkinter main loop

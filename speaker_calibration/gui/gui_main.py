import tkinter as tk
import ctypes
from plot_frame import PlotFrame
from options_frame import OptionsFrame

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

        # Configure the event triggered when a type of plot is selected
        self.options_frame.combobox.bind("<<ComboboxSelected>>", self.change_plot)

    def change_plot(self, event):
        # TODO
        if self.options_frame.combobox_var.get() == "Plot1":
            self.plot_frame.plot[0].set_data([0, 1, 2], [1, 2, 3])
            self.plot_frame.figure_canvas.draw_idle()
        else:
            self.plot_frame.plot[0].set_data([0, 1, 2], [1, 2, 4])
            self.plot_frame.figure_canvas.draw_idle()


if __name__ == "__main__":
    gui = SpeakerCalibrationGUI()
    gui.mainloop()

import tkinter as tk
import ctypes
from plot_frame import PlotFrame
from options_frame import OptionsFrame

myappid = "fchampalimaud.cdc.speaker_calibration.alpha"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # configure the root window
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

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)

        self.plot_frame = PlotFrame(self)
        self.plot_frame.grid(column=0, row=0, sticky="nsew")

        self.options_frame = OptionsFrame(self)
        self.options_frame.grid(column=1, row=0, sticky="nsew")
        self.options_frame.combobox.bind("<<ComboboxSelected>>", self.plot_chosen)

    def plot_chosen(self, event):
        if self.options_frame.combobox_var.get() == "Plot1":
            self.plot_frame.plot[0].set_data([0, 1, 2], [1, 2, 3])
            self.plot_frame.figure_canvas.draw_idle()
        else:
            self.plot_frame.plot[0].set_data([0, 1, 2], [1, 2, 4])
            self.plot_frame.figure_canvas.draw_idle()


if __name__ == "__main__":
    app = App()
    app.mainloop()

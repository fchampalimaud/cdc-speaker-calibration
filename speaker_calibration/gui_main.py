import tkinter as tk
import ctypes

from gui_model import SpeakerCalibrationModel
from gui_view import SpeakerCalibrationView
from gui_controller import SpeakerCalibrationController

myappid = "fchampalimaud.cdc.speaker_calibration.alpha"
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


class SpeakerCalibrationGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuration of the main window
        # Sets the window title and icon
        self.title("Speaker Calibration")
        self.iconbitmap("docs/img/favicon.ico")
        # Sets the window width and height
        window_width = 1280
        window_height = 720
        # Gets the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Sets the window position
        x = (screen_width / 2) - (window_width / 2)
        y = (screen_height / 2) - (window_height / 2)
        self.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
        # Configures the row and column of the main window
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Initializes the model
        model = SpeakerCalibrationModel()

        # Sets the view and places it on the window
        view = SpeakerCalibrationView(self)
        view.grid(row=0, column=0, sticky="nsew")

        # Initializes the controller
        controller = SpeakerCalibrationController(model, view)

        # Sets the controller of the view
        view.set_controller(controller)


if __name__ == "__main__":
    gui = SpeakerCalibrationGUI()
    gui.mainloop()

import tkinter as tk
from tkinter import ttk
import matplotlib

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class PlotFrame(ttk.Frame):
    """
    Frame responsible for displaying the Matplotlib figure in the GUI.
    """

    def __init__(self, container):
        super().__init__(container)

        # Creates a figure
        self.current_figure = Figure(dpi=100)

        # Creates the FigureCanvasTkAgg object
        self.canvas = FigureCanvasTkAgg(self.current_figure, self)

        # Creates the toolbar
        NavigationToolbar2Tk(self.canvas, self)

        # Places the figure widget in the GUI
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def set_figure(self, figure):
        self.canvas.get_tk_widget().destroy()
        self.current_figure = figure
        self.canvas = FigureCanvasTkAgg(self.current_figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        self.canvas.draw()

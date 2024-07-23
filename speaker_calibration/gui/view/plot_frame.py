import tkinter as tk
from tkinter import ttk
import matplotlib
import numpy as np

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
        figure = Figure(figsize=(6, 4), dpi=100)

        # Creates the FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(figure, self)

        # Creates the toolbar
        NavigationToolbar2Tk(self.figure_canvas, self)

        # Create an axes
        self.ax = figure.add_subplot()

        # Generates 3 empty plots in the axes
        self.plots = np.zeros(3, dtype=matplotlib.lines.Line2D)
        for i in range(self.plots.size):
            (self.plots[i],) = self.ax.plot(0)

        # Places the figure widget in the GUI
        self.figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

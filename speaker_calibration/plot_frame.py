import tkinter as tk
from tkinter import ttk
import matplotlib
import numpy as np

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class PlotFrame(ttk.Frame):
    def __init__(self, container):
        super().__init__(container)

        # create a figure
        figure = Figure(figsize=(6, 4), dpi=100)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(figure, self)

        # create the toolbar
        NavigationToolbar2Tk(self.figure_canvas, self)

        # create axes
        self.ax = figure.add_subplot()

        self.plots = np.zeros(3, dtype=matplotlib.lines.Line2D)
        for i in range(self.plots.size):
            (self.plots[i],) = self.ax.plot(0)

        self.figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

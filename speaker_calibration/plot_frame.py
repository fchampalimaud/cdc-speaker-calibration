import tkinter as tk
from tkinter import ttk
import matplotlib

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

        # create the barchart
        self.plot = self.ax.plot([1, 2, 3])
        self.ax.set_title("Top 5 Programming Languages")
        self.ax.set_ylabel("Popularity")

        self.figure_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
